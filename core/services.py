import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import BadHeaderError, EmailMessage

logger = logging.getLogger(__name__)


class Alerts:

    @staticmethod
    def send_email(to_email, message, reply_to="") -> bool:
        headers = {"Reply-To": reply_to} if reply_to else None
        email = EmailMessage(
            subject="Connection Issue During Interview",
            body=message or "",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
            headers=headers,
        )

        try:
            res = email.send(fail_silently=False)
            return bool(res)
        except (SMTPException, BadHeaderError):
            logger.exception("Failed to send interview alert email.")
            return False

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

        email = EmailMessage(
            subject="[InterviewGuard] New Question Submission Pending Review",
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_email],
        )
        try:
            email.send(fail_silently=False)
            return True
        except (SMTPException, BadHeaderError):
            logger.exception("Failed to send admin submission notification.")
            return False

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

        email = EmailMessage(
            subject="[InterviewGuard] New CV Builder Submission Pending Review",
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_email],
        )
        try:
            email.send(fail_silently=False)
            return True
        except (SMTPException, BadHeaderError):
            logger.exception("Failed to send admin CV builder notification.")
            return False
