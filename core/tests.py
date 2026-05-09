from django.core import mail
from django.test import Client
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .admin import approve_cv_builders, approve_questions, reject_cv_builders, reject_questions
from .models import CVBuilder, InterviewQuestion


class AlertEmailApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="tests@example.com",
    )
    def test_alert_email_endpoint_validates_and_sends_without_profile_storage(self):
        response = self.client.post(
            "/api/alerts/email/",
            {
                "to_email": "recruiter@example.com",
                "reply_to": "student@example.com",
                "message": "My connection dropped during the interview. Please contact me by phone.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["recruiter@example.com"])
        self.assertEqual(mail.outbox[0].bcc, ["student@example.com"])
        self.assertEqual(mail.outbox[0].extra_headers["Reply-To"], "student@example.com")
        self.assertIn("My connection dropped", mail.outbox[0].body)

        missing = self.client.post("/api/alerts/email/", {}, format="json")
        self.assertEqual(missing.status_code, 400)

    def test_profile_api_and_summary_endpoint_are_removed(self):
        self.assertEqual(self.client.get("/api/profiles/").status_code, 404)
        self.assertEqual(self.client.get("/api/summary/").status_code, 404)
        self.assertEqual(self.client.get("/api/summary").status_code, 404)


class ProductionSmokeTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_logo_asset_is_available_at_root(self):
        response = self.client.get("/interviewguard-logo.png")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")

    def test_upload_endpoint_accepts_octet_stream_speed_test_payloads(self):
        response = self.client.post(
            "/api/upload/",
            data=b"speed-test",
            content_type="application/octet-stream",
        )

        self.assertEqual(response.status_code, 200)


class InterviewQuestionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        for index in range(3):
            InterviewQuestion.objects.create(
                faculty="computer_science",
                difficulty="beginner",
                question=f"Question {index}",
                answer=f"Answer {index} with enough detail for tests.",
                order=index,
                status="approved",
            )
        self.pending = InterviewQuestion.objects.create(
            faculty="business",
            difficulty="beginner",
            question="Pending contribution?",
            answer="Awaiting review with enough detail for validation.",
            status="pending",
        )

    def test_questions_endpoint_honors_page_size_query_param(self):
        response = self.client.get("/api/questions/?page_size=2")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 3)
        self.assertEqual(len(payload["results"]), 2)

    def test_questions_endpoint_only_lists_approved_questions(self):
        response = self.client.get("/api/questions/?page_size=20")

        self.assertEqual(response.status_code, 200)
        questions = [item["question"] for item in response.json()["results"]]
        self.assertNotIn(self.pending.question, questions)

    @override_settings(
        ADMIN_NOTIFICATION_EMAIL="alerts@example.com",
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="tests@example.com",
    )
    def test_submit_question_creates_pending_question_and_emails_admin_and_submitter(self):
        response = self.client.post(
            "/api/questions/submit/",
            {
                "faculty": "engineering",
                "difficulty": "beginner",
                "question": "How do you approach safety?",
                "answer": "I identify hazards, follow procedure, and ask for supervision before continuing.",
                "submitted_by_name": "Student",
                "submitted_by_email": "student@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        question = InterviewQuestion.objects.get(question="How do you approach safety?")
        self.assertEqual(question.status, "pending")
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ["alerts@example.com"])
        self.assertEqual(mail.outbox[1].to, ["student@example.com"])

    def test_health_endpoint(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class CVBuilderApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.approved = CVBuilder.objects.create(
            name="Zety",
            short_description="Professional templates and writing guidance.",
            link="https://zety.com",
            order=1,
            status="approved",
        )
        self.pending = CVBuilder.objects.create(
            name="Pending Builder",
            short_description="Awaiting editorial review.",
            link="https://pending-builder.example.com",
            status="pending",
        )

    def test_cv_builders_endpoint_only_lists_approved_builders(self):
        response = self.client.get("/api/cv-builders/?page_size=20")

        self.assertEqual(response.status_code, 200)
        builders = response.json()["results"]
        self.assertEqual(len(builders), 1)
        self.assertEqual(builders[0]["name"], self.approved.name)
        self.assertEqual(builders[0]["icon_letter"], "Z")
        self.assertNotIn(self.pending.name, [item["name"] for item in builders])

    @override_settings(
        ADMIN_NOTIFICATION_EMAIL="alerts@example.com",
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="tests@example.com",
    )
    def test_submit_cv_builder_creates_pending_builder_and_emails_admin_and_submitter(self):
        response = self.client.post(
            "/api/cv-builders/submit/",
            {
                "name": "FlowCV",
                "short_description": "Simple browser-based CV builder with clean exports.",
                "link": "https://flowcv.com",
                "submitted_by_name": "Student",
                "submitted_by_email": "student@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        builder = CVBuilder.objects.get(name="FlowCV")
        self.assertEqual(builder.status, "pending")
        self.assertEqual(builder.submitted_by_email, "student@example.com")
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[0].to, ["alerts@example.com"])
        self.assertEqual(mail.outbox[1].to, ["student@example.com"])

    def test_submit_cv_builder_rejects_duplicate_links(self):
        response = self.client.post(
            "/api/cv-builders/submit/",
            {
                "name": "Zety Duplicate",
                "short_description": "Another submission for the same link.",
                "link": "https://zety.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)


class AdminQuestionActionTests(TestCase):
    def setUp(self):
        self.submission = InterviewQuestion.objects.create(
            faculty="computer_science",
            difficulty="beginner",
            question="What is Django?",
            answer="A Python web framework for building web applications quickly.",
            status="pending",
        )

    def test_approve_question_is_idempotent(self):
        queryset = InterviewQuestion.objects.filter(pk=self.submission.pk)

        approve_questions(None, None, queryset)
        approve_questions(None, None, queryset)

        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, "approved")
        self.assertEqual(InterviewQuestion.objects.count(), 1)

    def test_reject_question_does_not_change_approved_items(self):
        queryset = InterviewQuestion.objects.filter(pk=self.submission.pk)

        approve_questions(None, None, queryset)
        reject_questions(None, None, queryset)

        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, "approved")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="tests@example.com",
    )
    def test_approve_question_emails_submitter_once(self):
        self.submission.submitted_by_email = "student@example.com"
        self.submission.save(update_fields=["submitted_by_email"])
        queryset = InterviewQuestion.objects.filter(pk=self.submission.pk)

        approve_questions(None, None, queryset)
        approve_questions(None, None, queryset)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["student@example.com"])


class AdminCVBuilderActionTests(TestCase):
    def setUp(self):
        self.submission = CVBuilder.objects.create(
            name="FlowCV",
            short_description="Simple browser-based CV builder with clean exports.",
            link="https://flowcv.com",
            status="pending",
        )

    def test_approve_cv_builder_is_idempotent(self):
        queryset = CVBuilder.objects.filter(pk=self.submission.pk)

        approve_cv_builders(None, None, queryset)
        approve_cv_builders(None, None, queryset)

        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, "approved")
        self.assertEqual(CVBuilder.objects.count(), 1)

    def test_reject_cv_builder_does_not_change_approved_items(self):
        queryset = CVBuilder.objects.filter(pk=self.submission.pk)

        approve_cv_builders(None, None, queryset)
        reject_cv_builders(None, None, queryset)

        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, "approved")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="tests@example.com",
    )
    def test_approve_cv_builder_emails_submitter_once(self):
        self.submission.submitted_by_email = "student@example.com"
        self.submission.save(update_fields=["submitted_by_email"])
        queryset = CVBuilder.objects.filter(pk=self.submission.pk)

        approve_cv_builders(None, None, queryset)
        approve_cv_builders(None, None, queryset)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["student@example.com"])
