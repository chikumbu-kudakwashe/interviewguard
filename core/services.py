import logging
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import BadHeaderError, EmailMessage

logger = logging.getLogger(__name__)


class Alerts:

    @staticmethod
    def send_email(profile, message) -> bool:
        email = EmailMessage(
            subject="Connection Issue During Interview",
            body=message or "",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[profile.interviewer_email],
            headers={"Reply-To": profile.email}
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

# message = f"""
# Hi,

# I’m currently experiencing connectivity issues during our interview.

# Please feel free to reach me via:
# Phone: {profile.phone}
# WhatsApp: https://wa.me/{profile.phone}

# or we can have a whatsapp vidoo call if you

# You can also view my details here:
# http://localhost:3000/profile/{profile.id}

# Apologies for the inconvenience.
# """
