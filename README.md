InterviewGuard
==============

InterviewGuard is a lightweight Django + vanilla JavaScript app for interview preparation, local-only profile-based emergency alerts, and simple browser network checks. It is designed to stay usable on modest internet connections: no frontend build step, no heavy JavaScript framework, and a small JSON API.

Requirements
------------

- Python 3.12+
- `uv`
- A modern browser

Install
-------

```bash
uv sync
```

Database Setup
--------------

```bash
uv run python manage.py migrate
uv run python manage.py seed_data
```

`seed_data` is safe to run multiple times. It updates or creates approved seed questions and approved CV builder recommendations without duplicating matching question text or builder links.

Run The Backend
---------------

```bash
uv run python manage.py runserver 127.0.0.1:8000
```

Open The Frontend
-----------------

For a quick local static server:

```bash
cd frontend
python3 -m http.server 5050
```

Then open:

```txt
http://127.0.0.1:5050/index.html
```

API Endpoints
-------------

```txt
GET  /api/questions/
POST /api/questions/submit/
GET  /api/questions/pending/   admin only
GET  /api/cv-builders/
POST /api/cv-builders/submit/
GET  /api/cv-builders/pending/   admin only
POST /api/alerts/email/
GET  /api/health/
GET  /api/ping/
GET  /api/download/?size=200000
POST /api/upload/
```

Question Review Flow
--------------------

InterviewGuard now uses one question model: `InterviewQuestion`.

- Seeded questions are saved with `status="approved"`.
- Public `GET /api/questions/` only returns approved questions.
- User submissions go through `POST /api/questions/submit/` and are saved with `status="pending"`.
- Pending questions are not public until approved in Django admin.
- Admins can approve or reject questions from `/admin/core/interviewquestion/`.

CV Builder Review Flow
----------------------

Recommended CV builders use the `CVBuilder` model.

- Seeded builders are saved with `status="approved"`.
- Public `GET /api/cv-builders/` only returns approved builders.
- User submissions go through `POST /api/cv-builders/submit/` and are saved with `status="pending"`.
- Pending builders are not public until approved in Django admin.
- Admins can approve or reject builders from `/admin/core/cvbuilder/`.

Local Profile Data
------------------

The profile form is stored in browser `localStorage` only. There is no backend `Profile` model and no `/api/profiles/` endpoint. When Guard needs to send an apology email, the frontend posts the current email message to `POST /api/alerts/email/`; the server sends the email and stores nothing.

Production Notes
----------------

- Configure `DJANGO_SECRET_KEY` before setting `DEBUG=False`.
- Configure `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` for your real domain.
- Configure `DEFAULT_FROM_EMAIL` and a real Django email backend for alert delivery.
- Anonymous API requests are throttled with `DRF_ANON_THROTTLE_RATE` and default to `120/minute`.
- Alert emails are throttled with `DRF_ALERT_EMAIL_THROTTLE_RATE` and default to `5/hour`.
- Question submissions are throttled with `DRF_QUESTION_SUBMIT_THROTTLE_RATE` and default to `20/hour`.
- CV builder submissions are throttled with `DRF_CV_BUILDER_SUBMIT_THROTTLE_RATE` and default to `20/hour`.

Seed Data Sources
-----------------

The question bank is based on common internship and entry-level interview themes from university career centers and career-readiness guidance, including:

- NACE career readiness competencies: https://www.naceweb.org/career-readiness/competencies/career-readiness-defined
- University of Maryland interview types and STAR guidance: https://careers.umd.edu/find-jobs-internships/interviewing/types-of-interviews
- University of Cincinnati STAR method guide: https://www.uc.edu/campus-life/career-co-op-support/interviews/biginterview/star-method-behavioral-interview.html
- Harvard FAS technical interview guidance: https://careerservices.fas.harvard.edu/resources/technical-interviews/
- UMBC technical interview guidance: https://careers.umbc.edu/students/interview/types/technical-interviews/

Useful Checks
-------------

```bash
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run python manage.py test
node --check frontend/app.js
```
