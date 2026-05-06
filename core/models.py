from django.db import models
import uuid


class Profile(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    interviewer_email = models.EmailField()
    interviewer_phone = models.CharField(max_length=20, blank=True)

    bio = models.TextField()
    cv = models.FileField(upload_to="cvs/", blank=True, null=True)

    ip_address = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class InterviewQuestion(models.Model):
    FACULTY_CHOICES = [
        ("computer_science", "Computer Science"),
        ("engineering", "Engineering"),
        ("business", "Business"),
        ("social_behavioural", "Social & Behavioural Science"),
        ("medicine", "Medicine & Health Sciences"),
        ("law", "Law"),
        ("arts", "Arts & Humanities"),
        ("natural_sciences", "Natural Sciences"),
        ("education", "Education"),
        ("general", "General / All Faculties"),
    ]

    DIFFICULTY_CHOICES = [
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("advanced", "Advanced"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    faculty = models.CharField(max_length=50, choices=FACULTY_CHOICES, default="general")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default="beginner")
    question = models.TextField()
    answer = models.TextField()
    tip = models.TextField(blank=True, help_text="A short tip or what the interviewer is really looking for.")
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated tags e.g. 'OOP, Python, algorithms'")
    order = models.PositiveIntegerField(default=0, help_text="Display order within faculty")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    submitted_by_name = models.CharField(max_length=255, blank=True)
    submitted_by_email = models.EmailField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["faculty", "order", "difficulty", "id"]

    def __str__(self):
        return f"[{self.get_status_display()}] [{self.get_faculty_display()}] {self.question[:80]}"
