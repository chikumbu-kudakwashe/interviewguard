from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .admin import approve_questions, reject_questions
from .models import InterviewQuestion, Profile


class ProfileApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.profile = Profile.objects.create(
            full_name="Tariro Moyo",
            email="tariro@example.com",
            phone="+263771234567",
            interviewer_email="recruiter@example.com",
            interviewer_phone="",
            bio="Computer Science attachment candidate.",
            ip_address="127.0.0.1",
        )

    def test_profile_list_requires_uuid_filter(self):
        response = self.client.get("/api/profiles/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 0)

        response = self.client.get(f"/api/profiles/?uuid={self.profile.uuid}")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["uuid"], str(self.profile.uuid))

    def test_profile_detail_uses_uuid(self):
        response = self.client.patch(
            f"/api/profiles/{self.profile.uuid}/",
            {"phone": "+263779999999"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.phone, "+263779999999")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        DEFAULT_FROM_EMAIL="tests@example.com",
    )
    def test_send_email_requires_message_and_sends_to_interviewer(self):
        missing = self.client.post(
            f"/api/profiles/{self.profile.uuid}/send_email/",
            {},
            format="json",
        )
        self.assertEqual(missing.status_code, 400)

        response = self.client.post(
            f"/api/profiles/{self.profile.uuid}/send_email/",
            {"message": "My connection dropped."},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.profile.interviewer_email])
        self.assertIn("My connection dropped.", mail.outbox[0].body)


class InterviewQuestionApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        for index in range(3):
            InterviewQuestion.objects.create(
                faculty="computer_science",
                difficulty="beginner",
                question=f"Question {index}",
                answer=f"Answer {index}",
                order=index,
                status="approved",
            )
        self.pending = InterviewQuestion.objects.create(
            faculty="business",
            difficulty="beginner",
            question="Pending contribution?",
            answer="Awaiting review.",
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

    def test_submit_question_creates_pending_question(self):
        response = self.client.post(
            "/api/questions/submit/",
            {
                "faculty": "engineering",
                "difficulty": "beginner",
                "question": "How do you approach safety?",
                "answer": "I identify hazards, follow procedure, and ask for supervision.",
                "submitted_by_name": "Student",
                "submitted_by_email": "student@example.com",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        question = InterviewQuestion.objects.get(question="How do you approach safety?")
        self.assertEqual(question.status, "pending")

    def test_summary_endpoint_returns_dashboard_counts_with_or_without_slash(self):
        for path in ["/api/summary/", "/api/summary"]:
            response = self.client.get(path)

            self.assertEqual(response.status_code, 200)
            payload = response.json()
            self.assertEqual(payload["questions"]["approved"], 3)
            self.assertEqual(payload["questions"]["pending"], 1)
            self.assertIn("faculties", payload)


class AdminSubmissionActionTests(TestCase):
    def setUp(self):
        self.submission = InterviewQuestion.objects.create(
            faculty="computer_science",
            difficulty="beginner",
            question="What is Django?",
            answer="A Python web framework.",
            status="pending",
        )

    def test_approve_submission_does_not_duplicate_already_approved_items(self):
        queryset = InterviewQuestion.objects.filter(pk=self.submission.pk)

        approve_questions(None, None, queryset)
        approve_questions(None, None, queryset)

        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, "approved")
        self.assertEqual(InterviewQuestion.objects.count(), 1)

    def test_reject_submission_does_not_change_approved_items(self):
        queryset = InterviewQuestion.objects.filter(pk=self.submission.pk)

        approve_questions(None, None, queryset)
        reject_questions(None, None, queryset)

        self.submission.refresh_from_db()
        self.assertEqual(self.submission.status, "approved")
