// ── Configuration ─────────────────────────────────────────────
function resolveApiBase() {
    if (window.INTERVIEWGUARD_API_BASE) {
        return window.INTERVIEWGUARD_API_BASE.replace(/\/$/, '');
    }

    const host = window.location.hostname;
    if (!host || host === "localhost" || host === "127.0.0.1") {
        return "http://127.0.0.1:8000/api";
    }
    if (host === "192.168.50.1") {
        return "http://192.168.50.1:8000/api";
    }
    return `${window.location.origin}/api`;
}

const BASE = resolveApiBase();

        // ──────────────────────────────────────────────
        // CONSTANTS & STATE
        // ──────────────────────────────────────────────

        const PLATFORMS = {
            zoom: { name: 'Zoom', minDl: 1.5, minUl: 1.5, hdDl: 3.0 },
            teams: { name: 'MS Teams', minDl: 1.5, minUl: 1.5, hdDl: 4.0 },
            meet: { name: 'Google Meet', minDl: 1.0, minUl: 1.0, hdDl: 3.2 },
            webex: { name: 'Webex', minDl: 1.5, minUl: 1.5, hdDl: 4.0 },
            whatsapp: { name: 'WhatsApp', minDl: 0.3, minUl: 0.3, hdDl: 1.0 },
        };

        const state = {
            activePage: 'home',
            guardActive: false,
            guardMonitorId: null,
            lastTest: JSON.parse(localStorage.getItem('ig_last_test') || 'null'),
            profile: JSON.parse(localStorage.getItem('ig_profile') || 'null'),
            setupData: JSON.parse(localStorage.getItem('ig_setup') || 'null'),
            allQuestions: [],
            summary: null,
            selectedFaculty: 'all',
            selectedDiff: 'all',
            countdown: null,
            consecutiveFails: 0,
        };

        // ──────────────────────────────────────────────
        // ROUTER
        // ──────────────────────────────────────────────
        function navigateTo(page) {
            if (!document.getElementById('page-' + page)) page = 'home';
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById('page-' + page).classList.add('active');
            if (window.location.hash !== `#${page}`) history.replaceState(null, '', `#${page}`);
            const nav = document.getElementById('nav-' + page);
            if (nav) nav.classList.add('active');
            state.activePage = page;
            if (page === 'prep' && state.allQuestions.length === 0) loadQuestions();
            if (page === 'profile') loadProfileUI();
            if (page === 'home') {
                if (state.lastTest) updateHomeMetrics();
                loadSummary();
            }
        }

        // ──────────────────────────────────────────────
        // TOAST
        // ──────────────────────────────────────────────
        const TOAST_SVG = {
            success: '<polyline points="20 6 9 17 4 12"/>',
            warning: '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
            error: '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
            info: '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
        };

        function showToast(type, title, msg, duration = 4000) {
            const c = document.getElementById('toast-container');
            const el = document.createElement('div');
            el.className = 'toast ' + type;
            el.innerHTML = `<svg viewBox="0 0 24 24">${TOAST_SVG[type] || TOAST_SVG.info}</svg><div class="toast-body"><div class="toast-title">${title}</div>${msg ? `<div class="toast-msg">${msg}</div>` : ''}</div>`;
            el.onclick = () => el.remove();
            c.appendChild(el);
            setTimeout(() => { el.style.animation = 'toastOut .25s forwards'; setTimeout(() => el.remove(), 250); }, duration);
        }

        // ──────────────────────────────────────────────
        // NOTIFICATIONS
        // ──────────────────────────────────────────────
        async function toggleNotifications(btn) {
            btn.classList.toggle('on');
            if (btn.classList.contains('on')) {
                if (!('Notification' in window)) { btn.classList.remove('on'); return; }
                const perm = await Notification.requestPermission();
                if (perm !== 'granted') {
                    btn.classList.remove('on');
                    showToast('warning', 'Permission Denied', 'Enable notifications in your browser settings.');
                } else {
                    showToast('success', 'Notifications Enabled', 'You\'ll get alerts even in the background.');
                }
            }
        }

        function sendNotification(title, body) {
            if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {
                new Notification(title, { body, tag: 'interview-guard' });
            }
            showToast('warning', title, body, 6000);
        }

        // ──────────────────────────────────────────────
        // REAL SPEED TEST
        // Uses Blob + URL.createObjectURL to generate a real payload,
        // and XMLHttpRequest for measurable upload size.
        // ──────────────────────────────────────────────

        async function measurePing(count = 5) {
            const times = [];
            for (let i = 0; i < count; i++) {
                const t0 = performance.now();
                try { await fetch(`${BASE}/ping/?t=${Date.now()}`, { cache: 'no-store', mode: 'cors' }); }
                catch { /* server offline, use fallback */ }
                times.push(performance.now() - t0);
                await delay(80);
            }
            return Math.round(times.reduce((a, b) => a + b, 0) / times.length);
        }

        // Download test: fetches a sized blob from the API and measures true throughput.
        // Falls back to Network Information API or ping-based estimation if unavailable.
        async function measureDownload() {
            // Try 3 fetches of ~200 KB each, measure bits/time
            const sizes = [200_000, 500_000, 200_000]; // bytes
            let totalBits = 0, totalSeconds = 0;
            let succeeded = 0;

            for (const size of sizes) {
                const t0 = performance.now();
                try {
                    const res = await fetch(`${BASE}/download/?size=${size}&t=${Date.now()}`, { cache: 'no-store', mode: 'cors' });
                    if (!res.ok) throw new Error('not ok');
                    const buf = await res.arrayBuffer();
                    const elapsed = Math.max((performance.now() - t0) / 1000, 0.001); // Prevent division by zero
                    if (buf.byteLength > 100) {
                        totalBits += buf.byteLength * 8;
                        totalSeconds += elapsed;
                        succeeded++;
                    }
                } catch { /* endpoint not available */ }
            }

            if (succeeded > 0) {
                return parseFloat(((totalBits / totalSeconds) / 1_000_000).toFixed(2));
            }
            return null; // signal: use fallback
        }

        // Upload test: POST a generated Blob and measure throughput.
        async function measureUpload() {
            const sizes = [150_000, 300_000];
            let totalBits = 0, totalSeconds = 0;
            let succeeded = 0;

            for (const size of sizes) {
                const payload = new Uint8Array(size);
                crypto.getRandomValues(payload.slice(0, Math.min(size, 65536)));
                const blob = new Blob([payload]);

                const t0 = performance.now();
                try {
                    const res = await fetch(`${BASE}/upload/`, {
                        method: 'POST', body: blob, cache: 'no-store', mode: 'cors',
                        headers: { 'Content-Type': 'application/octet-stream' }
                    });
                    if (!res.ok) throw new Error('not ok');
                    const elapsed = Math.max((performance.now() - t0) / 1000, 0.001); // Prevent division by zero
                    totalBits += size * 8;
                    totalSeconds += elapsed;
                    succeeded++;
                } catch { /* endpoint not available */ }
            }

            if (succeeded > 0) {
                return parseFloat(((totalBits / totalSeconds) / 1_000_000).toFixed(2));
            }
            return null;
        }

        // Estimate speed from Network Information API + ping when endpoints unavailable
        function estimateFromNetworkInfo(ping) {
            const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
            if (conn && conn.downlink && conn.downlink > 0) {
                const dl = parseFloat(conn.downlink.toFixed(2));
                const ul = parseFloat((dl * (0.5 + Math.random() * 0.3)).toFixed(2));
                const effType = conn.effectiveType || '4g';
                const stability = effType === '4g' ? 85 + Math.random() * 12 : effType === '3g' ? 58 + Math.random() * 18 : 28 + Math.random() * 20;
                return { dl, ul, stability: Math.round(stability), estimated: true };
            }
            // Pure ping-based fallback
            let dl, stability;
            if (ping < 50) { dl = 12 + Math.random() * 25; stability = 90 + Math.random() * 8; }
            else if (ping < 100) { dl = 5 + Math.random() * 10; stability = 74 + Math.random() * 14; }
            else if (ping < 200) { dl = 1.5 + Math.random() * 4; stability = 52 + Math.random() * 16; }
            else if (ping < 400) { dl = 0.4 + Math.random() * 1; stability = 30 + Math.random() * 16; }
            else { dl = 0.1 + Math.random() * 0.3; stability = 10 + Math.random() * 14; }
            const ul = parseFloat((dl * (0.45 + Math.random() * 0.35)).toFixed(2));
            return { dl: parseFloat(dl.toFixed(2)), ul, stability: Math.round(stability), estimated: true };
        }

        async function runSpeedTest() {
            const btn = document.getElementById('testBtn');
            const btnText = document.getElementById('testBtnText');
            btn.disabled = true;
            btnText.innerHTML = '<div class="spinner"></div> Testing…';

            const steps = ['Measuring latency…', 'Testing download speed…', 'Testing upload speed…', 'Checking stability…', 'Calculating score…'];
            let si = 0;
            const stepTimer = setInterval(() => { if (si < steps.length - 1) btnText.innerHTML = `<div class="spinner"></div> ${steps[++si]}`; }, 1500);

            try {
                // 1. Ping
                const ping = await measurePing(5);

                // 2. Download (real if server available)
                let dl = await measureDownload();
                let ulMeasured = null;

                // 3. Upload (real if server available)
                if (dl !== null) {
                    ulMeasured = await measureUpload();
                }

                // 4. Fallback if endpoints unavailable
                let stability, estimated = false;
                if (dl === null) {
                    const est = estimateFromNetworkInfo(ping);
                    dl = est.dl;
                    ulMeasured = est.ul;
                    stability = est.stability;
                    estimated = est.estimated;
                } else {
                    if (ulMeasured === null) {
                        ulMeasured = parseFloat((dl * (0.45 + Math.random() * 0.35)).toFixed(2));
                    }
                    // Stability from Network Info or ping
                    const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
                    if (conn && conn.effectiveType) {
                        const et = conn.effectiveType;
                        stability = et === '4g' ? 85 + Math.random() * 12 : et === '3g' ? 58 + Math.random() * 18 : 28 + Math.random() * 20;
                    } else {
                        stability = ping < 100 ? 85 + Math.random() * 13 : ping < 200 ? 65 + Math.random() * 18 : ping < 400 ? 42 + Math.random() * 18 : 20 + Math.random() * 16;
                    }
                }

                // 5. Jitter check
                const ping2 = await measurePing(3);
                const jitter = Math.abs(ping2 - ping);
                if (jitter > 60) stability = Math.max(stability - 18, 8);
                stability = Math.round(stability);

                clearInterval(stepTimer);

                const result = { dl, ul: ulMeasured, ping, stability, estimated };
                state.lastTest = result;
                localStorage.setItem('ig_last_test', JSON.stringify(result));

                updateTestUI(result);
                updateHomeMetrics();

                btn.disabled = false;
                btnText.innerHTML = '<svg viewBox="0 0 24 24" style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2.5;stroke-linecap:round"><polyline points="20 6 9 17 4 12"/></svg> Test Complete';
                setTimeout(() => { btnText.innerHTML = '<svg viewBox="0 0 24 24" style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2.2;stroke-linecap:round"><polygon points="5 3 19 12 5 21 5 3"/></svg> Retest'; }, 3000);

                if (estimated) {
                    showToast('info', 'Estimated Results', 'Speed test endpoints not available — results estimated from latency & Network Info API.');
                }

            } catch (e) {
                clearInterval(stepTimer);
                btn.disabled = false;
                btnText.innerHTML = '<svg viewBox="0 0 24 24" style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2.2;stroke-linecap:round"><polygon points="5 3 19 12 5 21 5 3"/></svg> Retry Test';
                showToast('error', 'Test Failed', 'Could not complete the test. Check your connection.');
            }
        }

        function updateTestUI({ dl, ul, ping, stability }) {
            const plat = PLATFORMS[document.getElementById('platformSelect').value] || PLATFORMS.zoom;

            document.getElementById('dlVal').textContent = dl;
            document.getElementById('ulVal').textContent = ul;
            document.getElementById('pingVal').textContent = ping;
            document.getElementById('stabilityPct').textContent = stability + '%';
            const bar = document.getElementById('stabilityBar');
            bar.style.width = stability + '%';
            bar.style.background = stability > 70 ? 'var(--green)' : stability > 45 ? 'var(--yellow)' : 'var(--red)';

            // Badges
            const dlOk = dl >= plat.minDl;
            const ulOk = ul >= plat.minUl;
            const pingOk = ping < 150;

            setBadge('dlBadge', dl >= plat.hdDl ? 'good' : dlOk ? 'ok' : 'bad',
                dl >= plat.hdDl ? 'HD Ready' : dlOk ? 'Minimum' : 'Too Slow');
            setBadge('ulBadge', ulOk ? 'ok' : 'bad', ulOk ? 'Adequate' : 'Too Slow');
            setBadge('pingBadge', pingOk ? 'good' : ping < 300 ? 'ok' : 'bad',
                ping < 80 ? 'Excellent' : ping < 150 ? 'Good' : ping < 300 ? 'Fair' : 'High');

            // Score
            let score = 100;
            if (dl < plat.minDl) score -= Math.min(((plat.minDl - dl) / plat.minDl) * 45, 45);
            else if (dl < plat.hdDl) score -= 10;
            if (ul < plat.minUl) score -= Math.min(((plat.minUl - ul) / plat.minUl) * 35, 35);
            if (ping > 300) score -= 28; else if (ping > 150) score -= 14;
            if (stability < 40) score -= 20; else if (stability < 65) score -= 8;
            score = Math.max(0, Math.min(100, Math.round(score)));

            const C = 2 * Math.PI * 50;
            document.getElementById('probArc').setAttribute('stroke-dasharray', `${(score / 100) * C} ${C}`);
            const color = score >= 75 ? 'var(--green)' : score >= 50 ? 'var(--yellow)' : 'var(--red)';
            document.getElementById('probArc').style.stroke = color;
            document.getElementById('probPct').textContent = score + '%';
            document.getElementById('probPct').style.color = color;
            document.getElementById('probLabel').textContent = score >= 75 ? 'Looks good ✓' : score >= 50 ? 'Moderate risk' : 'High risk ⚠';

            // Insight
            const insight = document.getElementById('insightBox');
            const insightText = document.getElementById('insightText');
            let msg, bg, bc;
            if (score >= 75) { msg = `Your connection should handle ${plat.name} comfortably. Keep background apps closed.`; bg = 'var(--green-bg)'; bc = 'rgba(26,158,106,.15)'; }
            else if (score >= 50) { msg = `Moderate risk on ${plat.name}. Move closer to your router and close other tabs.`; bg = 'var(--yellow-bg)'; bc = 'rgba(200,134,10,.15)'; }
            else { msg = `High dropout risk. Consider switching to mobile data or requesting a phone interview instead.`; bg = 'var(--red-bg)'; bc = 'rgba(204,51,51,.15)'; }
            insightText.textContent = msg;
            insight.style.background = bg;
            insight.style.borderColor = bc;
        }

        function setBadge(id, type, text) {
            const el = document.getElementById(id);
            el.textContent = text;
            el.className = 'badge ' + ({ good: 'b-good', ok: 'b-ok', bad: 'b-bad' }[type] || 'b-neutral');
        }

        function updateHomeMetrics() {
            if (!state.lastTest) return;
            const { dl, ul, ping } = state.lastTest;
            document.getElementById('home-dl').textContent = dl;
            document.getElementById('home-ul').textContent = ul;
            document.getElementById('home-ping').textContent = ping;
        }

        async function loadSummary() {
            const statusEl = document.getElementById('summaryStatus');
            if (!statusEl) return;
            statusEl.textContent = 'Loading dashboard summary…';
            try {
                const res = await fetch(`${BASE}/summary/`, { cache: 'no-store', mode: 'cors' });
                if (!res.ok) throw new Error('summary unavailable');
                state.summary = await res.json();
                updateSummaryUI(state.summary);
            } catch {
                statusEl.textContent = 'Summary unavailable. Start the Django server and refresh.';
                ['summaryApproved', 'summaryPending', 'summaryFaculties', 'summaryProfiles'].forEach(id => {
                    const el = document.getElementById(id);
                    if (el) el.textContent = '—';
                });
                document.getElementById('summaryFacultyList').innerHTML = '';
            }
        }

        function updateSummaryUI(summary) {
            const activeFaculties = (summary.faculties || []).filter(f => f.approved_count > 0);
            document.getElementById('summaryStatus').textContent = 'Live from /api/summary/';
            document.getElementById('summaryApproved').textContent = summary.questions?.approved ?? 0;
            document.getElementById('summaryPending').textContent = summary.questions?.pending ?? 0;
            document.getElementById('summaryFaculties').textContent = activeFaculties.length;
            document.getElementById('summaryProfiles').textContent = summary.profiles?.total ?? 0;
            document.getElementById('summaryFacultyList').innerHTML = activeFaculties.slice(0, 6).map(f => `
                <button class="summary-chip" type="button" onclick="navigateTo('prep'); setFacultyByValue('${esc(f.faculty)}')">
                    ${esc(f.faculty_label)} <span>${f.approved_count}</span>
                </button>
            `).join('') || '<span class="summary-empty">Seed questions to populate the bank.</span>';
        }

        // ──────────────────────────────────────────────
        // GUARD
        // ──────────────────────────────────────────────
        async function activateGuard() {
            const email = document.getElementById('s-email').value.trim();
            if (!email) { showToast('error', 'Missing Email', 'Please enter the interviewer email.'); return; }

            const setupData = {
                company: document.getElementById('s-company').value.trim(),
                email,
                platform: document.getElementById('s-platform').value,
                datetime: document.getElementById('s-datetime').value,
                doNotif: document.getElementById('toggle-notif').classList.contains('on'),
                doMonitor: document.getElementById('toggle-monitor').classList.contains('on'),
                doCountdown: document.getElementById('toggle-countdown').classList.contains('on'),
            };
            localStorage.setItem('ig_setup', JSON.stringify(setupData));
            state.setupData = setupData;

            if (setupData.doNotif) await Notification.requestPermission().catch(() => { });
            state.guardActive = true;

            updateGuardChip('on', 'Guard On');
            showGuardBanner('Guard active — monitoring every 15s', false);
            showToast('success', 'Interview Guard Activated', `Monitoring started for ${setupData.platform || 'your interview'}.`);

            if (setupData.doMonitor) startNetworkMonitor();
            if (setupData.doCountdown && setupData.datetime) scheduleCountdown(new Date(setupData.datetime));

            const btn = document.getElementById('activateBtn');
            btn.style.background = 'var(--green)';
            btn.innerHTML = `<svg viewBox="0 0 24 24" style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2.5;stroke-linecap:round"><polyline points="20 6 9 17 4 12"/></svg> Guard is Active`;
        }

        function updateGuardChip(cls, text) {
            const chip = document.getElementById('guardChip');
            chip.className = 'guard-chip ' + cls;
            document.getElementById('guardChipText').textContent = text;
        }

        function showGuardBanner(msg, isDanger) {
            document.getElementById('bannerMsg').textContent = msg;
            const inner = document.getElementById('bannerInner');
            inner.className = 'banner-inner' + (isDanger ? ' danger' : '');
            document.getElementById('guard-banner').classList.add('visible');
        }

        function hideBanner() { document.getElementById('guard-banner').classList.remove('visible'); }

        function startNetworkMonitor() {
            if (state.guardMonitorId) clearInterval(state.guardMonitorId);
            checkNetwork();
            state.guardMonitorId = setInterval(checkNetwork, 15_000);
        }

        async function checkNetwork() {
            try {
                const t0 = performance.now();
                await fetch(`${BASE}/ping/?t=${Date.now()}`, { cache: 'no-store' });
                const lat = Math.round(performance.now() - t0);
                state.consecutiveFails = 0;
                const cls = lat < 100 ? 'on' : lat < 300 ? 'warn' : 'danger';
                const label = lat < 100 ? 'Guard On' : lat < 300 ? 'Slow' : 'Unstable';
                updateGuardChip(cls, label);
                if (lat > 400) {
                    showGuardBanner(`High latency (${lat}ms) — connection degrading`, true);
                    sendNotification('⚠ Connection Degrading', `Latency is ${lat}ms. You may lose the call soon.`);
                } else {
                    showGuardBanner(`Guard active — last ping ${lat}ms`, false);
                }
            } catch {
                state.consecutiveFails = (state.consecutiveFails || 0) + 1;
                if (state.consecutiveFails >= 2) {
                    updateGuardChip('danger', 'Disconnected');
                    showGuardBanner('⚠ Connection lost! Send apology email now.', true);
                    sendNotification('🚨 Connection Lost', 'Your internet is down. Send the apology email now.');
                    if (state.setupData?.doMonitor && state.profile) triggerApologyEmail();
                }
            }
        }

        function scheduleCountdown(date) {
            const ms = date.getTime() - 10 * 60 * 1000 - Date.now();
            if (ms > 0) {
                if (state.countdown) clearTimeout(state.countdown);
                state.countdown = setTimeout(() => sendNotification('⏰ Interview in 10 Minutes!', 'Run a quick test and make sure Guard is active.'), ms);
            }
        }

        async function triggerApologyEmail() {
            const profileKey = getServerProfileKey();
            if (!profileKey) return;
            try {
                const res = await fetch(`${BASE}/profiles/${encodeURIComponent(profileKey)}/send_email/`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: buildEmailBody(state.profile) }),
                });
                if (res.ok) showToast('success', 'Apology Email Sent', `Sent to ${state.setupData?.email || 'interviewer'}.`);
                else throw new Error();
            } catch { showToast('error', 'Auto-Email Failed', 'Could not reach server. Please send manually.'); }
        }

        // ──────────────────────────────────────────────
        // PROFILE
        // ──────────────────────────────────────────────
        function getServerProfileKey(profile = state.profile) {
            const uuid = profile?.uuid || localStorage.getItem('ig_profile_uuid');
            if (!uuid || String(uuid).startsWith('local-')) return null;
            return uuid;
        }

        function loadProfileUI() {
            const p = state.profile;
            if (!p) return;
            document.getElementById('p-name').value = p.full_name || '';
            document.getElementById('p-email').value = p.email || '';
            document.getElementById('p-phone').value = p.phone || '';
            document.getElementById('p-bio').value = p.bio || '';
            document.getElementById('p-int-email').value = p.interviewer_email || '';
            document.getElementById('p-int-phone').value = p.interviewer_phone || '';
            document.getElementById('profileBanner').style.display = 'block';
            document.getElementById('profileBannerName').textContent = p.full_name || '—';
            document.getElementById('profileBannerEmail').textContent = p.email || '—';
            document.getElementById('profileAvatarLetter').textContent = (p.full_name || 'U')[0].toUpperCase();
            document.getElementById('deleteZone').style.display = getServerProfileKey(p) ? 'block' : 'none';
            updateEmailPreview();
        }

        async function saveProfile() {
            const data = {
                full_name: document.getElementById('p-name').value.trim(),
                email: document.getElementById('p-email').value.trim(),
                phone: document.getElementById('p-phone').value.trim(),
                bio: document.getElementById('p-bio').value.trim(),
                interviewer_email: document.getElementById('p-int-email').value.trim(),
                interviewer_phone: document.getElementById('p-int-phone').value.trim(),
            };
            if (!data.full_name || !data.email) { showToast('error', 'Missing Fields', 'Name and email are required.'); return; }

            try {
                const uuid = localStorage.getItem('ig_profile_uuid');
                let res, json;
                if (uuid && !uuid.startsWith('local-')) {
                    res = await fetch(`${BASE}/profiles/${encodeURIComponent(uuid)}/`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
                    if (res.status === 404) {
                        res = await fetch(`${BASE}/profiles/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
                    }
                    json = await res.json();
                } else {
                    res = await fetch(`${BASE}/profiles/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
                    json = await res.json();
                }
                if (res.ok) {
                    localStorage.setItem('ig_profile_uuid', json.uuid);
                    localStorage.setItem('ig_profile', JSON.stringify(json));
                    state.profile = json;
                    showToast('success', 'Profile Saved', 'Stored locally and on server.');
                    loadProfileUI();
                } else throw new Error();
            } catch {
                const local = { ...data, uuid: localStorage.getItem('ig_profile_uuid') || ('local-' + Date.now()) };
                localStorage.setItem('ig_profile', JSON.stringify(local));
                localStorage.setItem('ig_profile_uuid', local.uuid);
                state.profile = local;
                showToast('warning', 'Saved Locally', 'Server offline — profile stored in browser only.');
                loadProfileUI();
            }
        }

        async function deleteProfile() {
            if (!confirm('Delete your profile? This cannot be undone.')) return;
            const uuid = localStorage.getItem('ig_profile_uuid');
            if (uuid && !uuid.startsWith('local-')) {
                try {
                    await fetch(`${BASE}/profiles/${encodeURIComponent(uuid)}/`, { method: 'DELETE' });
                } catch { }
            }
            localStorage.removeItem('ig_profile');
            localStorage.removeItem('ig_profile_uuid');
            state.profile = null;
            showToast('info', 'Profile Deleted', 'All data cleared.');
            document.getElementById('profileBanner').style.display = 'none';
            document.getElementById('deleteZone').style.display = 'none';
            ['p-name', 'p-email', 'p-phone', 'p-bio', 'p-int-email', 'p-int-phone'].forEach(id => document.getElementById(id).value = '');
        }

        function buildEmailBody(p) {
            const s = state.setupData;
            return `Dear ${s?.company || 'Interviewer'},

I sincerely apologise — I am currently experiencing an unexpected network outage that has disconnected our call. I am actively working to restore my connection.

If I am unable to rejoin within a few minutes, please let me know if we can continue via phone or reschedule at your convenience.

You can reach me at:
  📞 Phone / WhatsApp: ${p.phone || '—'}
  📧 Email: ${p.email || '—'}
${p.bio ? `\nAbout me:\n${p.bio}\n` : ''}
I remain very interested in this opportunity and appreciate your patience.

Kind regards,
${p.full_name || '—'}`;
        }

        function updateEmailPreview() {
            const el = document.getElementById('emailPreviewBody');
            el.textContent = state.profile ? buildEmailBody(state.profile) : 'Fill in your profile to preview the apology email.';
        }

        // ──────────────────────────────────────────────
        // PREP / Q&A
        // ──────────────────────────────────────────────
        async function loadQuestions() {
            document.getElementById('qaContainer').innerHTML = `<div class="empty-state"><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg><h3>Loading…</h3><p>Connecting to server.</p></div>`;
            try {
                const res = await fetch(`${BASE}/questions/?page_size=200`);
                if (!res.ok) throw new Error();
                const data = await res.json();
                state.allQuestions = data.results || data;
                renderQuestions();
            } catch {
                document.getElementById('qaContainer').innerHTML = `<div class="empty-state"><svg viewBox="0 0 24 24"><line x1="1" y1="1" x2="23" y2="23"/><path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55"/><path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39"/><path d="M10.71 5.05A16 16 0 0 1 22.56 9"/><path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/></svg><h3>Server Offline</h3><p>Start the Django server and reload.</p></div>`;
            }
        }

        function setFaculty(btn, val) {
            document.querySelectorAll('#facultyFilter .chip').forEach(c => { c.className = 'chip chip-out'; });
            btn.className = 'chip chip-fill';
            state.selectedFaculty = val;
            renderQuestions();
        }

        function setFacultyByValue(val) {
            const btn = document.querySelector(`#facultyFilter .chip[data-faculty="${val}"]`);
            if (btn) setFaculty(btn, val);
        }

        function setDiff(btn, val) {
            document.querySelectorAll('#diffFilter .chip').forEach(c => { c.className = 'chip chip-out'; });
            btn.className = 'chip chip-fill';
            state.selectedDiff = val;
            renderQuestions();
        }

        function filterQuestions() { renderQuestions(); }

        const FACULTY_LABELS = { computer_science: 'Computer Science', engineering: 'Engineering', business: 'Business', social_behavioural: 'Social Science', general: 'General', medicine: 'Medicine & Health Sciences', law: 'Law', arts: 'Arts & Humanities', natural_sciences: 'Natural Sciences', education: 'Education' };

        function renderQuestions() {
            const search = document.getElementById('qSearchInput').value.toLowerCase();
            const filtered = state.allQuestions.filter(q => {
                const fMatch = state.selectedFaculty === 'all' || q.faculty === state.selectedFaculty;
                const dMatch = state.selectedDiff === 'all' || q.difficulty === state.selectedDiff;
                const sMatch = !search || q.question.toLowerCase().includes(search) || (q.tags || '').toLowerCase().includes(search);
                return fMatch && dMatch && sMatch;
            });

            document.getElementById('qCount').textContent = filtered.length + ' Questions';
            document.getElementById('prepSectionLabel').textContent = state.selectedFaculty === 'all' ? 'All Questions' : (FACULTY_LABELS[state.selectedFaculty] || state.selectedFaculty);

            if (!filtered.length) {
                document.getElementById('qaContainer').innerHTML = `<div class="empty-state"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg><h3>No matches</h3><p>Try a different filter or search term.</p></div>`;
                return;
            }

            document.getElementById('qaContainer').innerHTML = filtered.map(q => `
    <details class="qa-item">
      <summary class="qa-q">
        <div class="qa-q-text">${esc(q.question)}</div>
        <div class="qa-q-right">
          <span class="diff-b ${q.difficulty === 'beginner' ? 'd-beg' : q.difficulty === 'intermediate' ? 'd-int' : 'd-adv'}">${esc(q.difficulty_label || q.difficulty)}</span>
          <i class="qa-chevron">▾</i>
        </div>
      </summary>
      <div class="qa-body">
        <div class="qa-sec-label">Model Answer</div>
        <div class="qa-answer">${esc(q.answer)}</div>
        ${q.tip ? `<div class="qa-tip"><strong>💡 Tip:</strong> ${esc(q.tip)}</div>` : ''}
        ${q.tags ? `<div class="qa-tags">${q.tags.split(',').map(t => `<span class="qa-tag">${esc(t.trim())}</span>`).join('')}</div>` : ''}
      </div>
    </details>
  `).join('');
        }

        // ──────────────────────────────────────────────
        // UTILS
        // ──────────────────────────────────────────────
        function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

        function esc(s) {
            return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
        }

        // ──────────────────────────────────────────────
        // INIT
        // ──────────────────────────────────────────────
        (function init() {
            if (typeof Notification !== 'undefined' && Notification.permission !== 'granted') {
                document.getElementById('toggle-notif').classList.remove('on');
            }
            if (state.profile) { updateEmailPreview(); }
            if (state.setupData) {
                const s = state.setupData;
                if (s.company) document.getElementById('s-company').value = s.company;
                if (s.email) document.getElementById('s-email').value = s.email;
                if (s.platform) document.getElementById('s-platform').value = s.platform;
                if (s.datetime) document.getElementById('s-datetime').value = s.datetime;
            }
            if (state.lastTest) updateHomeMetrics();
            const initialPage = (window.location.hash || '#home').slice(1);
            navigateTo(initialPage);
        })();

        // ── Question Submission ────────────────────────────────────────
        document.getElementById('submitForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await submitQuestion();
        });

        async function submitQuestion() {
            const btn = document.getElementById('submitBtn');

            // Gather data
            const data = {
                faculty:            document.getElementById('sub-faculty').value,
                difficulty:         document.getElementById('sub-difficulty').value,
                question:           document.getElementById('sub-question').value.trim(),
                answer:             document.getElementById('sub-answer').value.trim(),
                tip:                document.getElementById('sub-tip').value.trim(),
                tags:               document.getElementById('sub-tags').value.trim(),
                submitted_by_name:  document.getElementById('sub-name').value.trim(),
                submitted_by_email: document.getElementById('sub-email').value.trim(),
            };

            // Client-side validation
            if (!data.faculty) {
                showToast('error', 'Missing Field', 'Please select a faculty.');
                return;
            }
            if (!data.question) {
                showToast('error', 'Missing Field', 'Please enter the interview question.');
                return;
            }
            if (!data.answer) {
                showToast('error', 'Missing Field', 'Please provide a model answer.');
                return;
            }

            btn.disabled = true;
            btn.textContent = 'Submitting…';

            try {
                const res = await fetch(`${BASE}/questions/submit/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data),
                });

                const json = await res.json();

                if (res.ok) {
                    // Hide the form, show the pending confirmation
                    document.getElementById('submitForm').classList.add('hidden');
                    document.getElementById('submitSuccess').classList.remove('hidden');
                    loadSummary();
                    showToast('success', 'Question Submitted', 'It will be reviewed before publishing.');
                } else {
                    // Show field-level errors if DRF returns them
                    const errorMsg = typeof json === 'object'
                        ? Object.entries(json).map(([k, v]) => `${k}: ${v}`).join(' | ')
                        : 'Submission failed.';
                    showToast('error', 'Submission Error', errorMsg);
                }
            } catch {
                showToast('error', 'Server Offline', 'Could not reach the server. Try again shortly.');
            }

            btn.disabled = false;
            btn.textContent = 'Submit Question';
        }

        function resetSubmitForm() {
            document.getElementById('submitForm').reset();
            document.getElementById('submitForm').classList.remove('hidden');
            document.getElementById('submitSuccess').classList.add('hidden');
            document.getElementById('submitBtn').disabled = false;
            document.getElementById('submitBtn').textContent = 'Submit Question';
        }

        function toggleSubmitForm() {
            const section = document.getElementById('submit-section');
            const btn = document.getElementById('submitToggleBtn');
            if (section.classList.contains('hidden')) {
                section.classList.remove('hidden');
                btn?.setAttribute('aria-expanded', 'true');
                section.scrollIntoView({ behavior: 'smooth', block: 'start' });
                setTimeout(() => document.getElementById('sub-faculty')?.focus(), 250);
            } else {
                section.classList.add('hidden');
                btn?.setAttribute('aria-expanded', 'false');
            }
        }
