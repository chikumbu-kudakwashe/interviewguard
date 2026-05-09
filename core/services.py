import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import BadHeaderError, EmailMessage

logger = logging.getLogger(__name__)


class Alerts:
    MAIL_EXCEPTIONS = (SMTPException, BadHeaderError, OSError)

    @staticmethod
    def _send_plain_email(subject, body, recipients, log_message, reply_to="", bcc=None) -> bool:
        recipients = [email for email in recipients if email]
        if not recipients:
            return False

        headers = {"Reply-To": reply_to} if reply_to else None
        email = EmailMessage(
            subject=subject,
            body=body or "",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
            bcc=[email for email in (bcc or []) if email],
            headers=headers,
        )

        try:
            res = email.send(fail_silently=False)
            return bool(res)
        except Alerts.MAIL_EXCEPTIONS:
            logger.exception(log_message)
            return False

    @staticmethod
    def send_email(to_email, message, reply_to="") -> bool:
        copy_to_user = ""
        if reply_to and reply_to.lower() != to_email.lower():
            copy_to_user = reply_to

        return Alerts._send_plain_email(
            subject="Connection Issue During Interview",
            body=message or "",
            recipients=[to_email],
            bcc=[copy_to_user] if copy_to_user else None,
            reply_to=reply_to,
            log_message="Failed to send interview alert email.",
        )

    @staticmethod
    def send_sms(phone_number: str) -> bool:
        logger.info("Sending mock SMS to %s", phone_number)
        return True

    @staticmethod
    def start_whatsapp_call(phone_number) -> bool:
        logger.info("Starting mock WhatsApp call to %s", phone_number)
        return True

    @staticmethod
    def notify_admin_of_submission(submission) -> bool:
        """
        Emails the admin when a new question is submitted for review.
        Configure ADMIN_NOTIFICATION_EMAIL in settings.py.
        """
        admin_email = getattr(settings, "ADMIN_NOTIFICATION_EMAIL", None)
        if not admin_email:
            return False

        body = (
            f"A new interview question has been submitted for review.\n\n"
            f"Faculty:    {submission.get_faculty_display()}\n"
            f"Difficulty: {submission.get_difficulty_display()}\n"
            f"Question:   {submission.question}\n\n"
            f"Submitted by: {submission.submitted_by_name or 'Anonymous'} "
            f"({submission.submitted_by_email or 'no email'})\n\n"
            f"Review at: /admin/core/interviewquestion/?status__exact=pending"
        )

        return Alerts._send_plain_email(
            subject="[InterviewGuard] New Question Submission Pending Review",
            body=body,
            recipients=[admin_email],
            log_message="Failed to send admin submission notification.",
        )

    @staticmethod
    def notify_submitter_of_submission(submission) -> bool:
        submitter_email = getattr(submission, "submitted_by_email", "")
        if not submitter_email:
            return False

        name = submission.submitted_by_name or "there"
        body = (
            f"Hi {name},\n\n"
            f"Thanks for submitting an interview question to InterviewGuard.\n\n"
            f"Your question is now pending review. If approved, it will appear in the prep bank for other students.\n\n"
            f"Question: {submission.question}\n\n"
            f"InterviewGuard Team"
        )

        return Alerts._send_plain_email(
            subject="[InterviewGuard] Question Submission Received",
            body=body,
            recipients=[submitter_email],
            log_message="Failed to send submitter question confirmation.",
        )

    @staticmethod
    def notify_submitter_of_question_approval(submission) -> bool:
        submitter_email = getattr(submission, "submitted_by_email", "")
        if not submitter_email:
            return False

        name = submission.submitted_by_name or "there"
        body = (
            f"Hi {name},\n\n"
            f"Good news: your interview question has been approved and added to InterviewGuard.\n\n"
            f"Question: {submission.question}\n\n"
            f"Thank you for helping other students prepare.\n\n"
            f"InterviewGuard Team"
        )

        return Alerts._send_plain_email(
            subject="[InterviewGuard] Your Question Was Approved",
            body=body,
            recipients=[submitter_email],
            log_message="Failed to send submitter question approval email.",
        )

    @staticmethod
    def notify_admin_of_cv_builder_submission(submission) -> bool:
        """
        Emails the admin when a new CV builder is submitted for review.
        Configure ADMIN_NOTIFICATION_EMAIL in settings.py.
        """
        admin_email = getattr(settings, "ADMIN_NOTIFICATION_EMAIL", None)
        if not admin_email:
            return False

        body = (
            f"A new CV builder has been submitted for review.\n\n"
            f"Name:        {submission.name}\n"
            f"Link:        {submission.link}\n"
            f"Description: {submission.short_description}\n\n"
            f"Submitted by: {submission.submitted_by_name or 'Anonymous'} "
            f"({submission.submitted_by_email or 'no email'})\n\n"
            f"Review at: /admin/core/cvbuilder/?status__exact=pending"
        )

        return Alerts._send_plain_email(
            subject="[InterviewGuard] New CV Builder Submission Pending Review",
            body=body,
            recipients=[admin_email],
            log_message="Failed to send admin CV builder notification.",
        )

    @staticmethod
    def notify_submitter_of_cv_builder_submission(submission) -> bool:
        submitter_email = getattr(submission, "submitted_by_email", "")
        if not submitter_email:
            return False

        name = submission.submitted_by_name or "there"
        body = (
            f"Hi {name},\n\n"
            f"Thanks for recommending a CV builder to InterviewGuard.\n\n"
            f"Your recommendation is now pending review. If approved, it will appear in the recommended builders list.\n\n"
            f"Builder: {submission.name}\n"
            f"Link: {submission.link}\n\n"
            f"InterviewGuard Team"
        )

        return Alerts._send_plain_email(
            subject="[InterviewGuard] CV Builder Submission Received",
            body=body,
            recipients=[submitter_email],
            log_message="Failed to send submitter CV builder confirmation.",
        )

    @staticmethod
    def notify_submitter_of_cv_builder_approval(submission) -> bool:
        submitter_email = getattr(submission, "submitted_by_email", "")
        if not submitter_email:
            return False

        name = submission.submitted_by_name or "there"
        body = (
            f"Hi {name},\n\n"
            f"Good news: your CV builder recommendation has been approved and added to InterviewGuard.\n\n"
            f"Builder: {submission.name}\n"
            f"Link: {submission.link}\n\n"
            f"Thank you for helping other students find useful CV tools.\n\n"
            f"InterviewGuard Team"
        )

        return Alerts._send_plain_email(
            subject="[InterviewGuard] Your CV Builder Was Approved",
            body=body,
            recipients=[submitter_email],
            log_message="Failed to send submitter CV builder approval email.",
        )
