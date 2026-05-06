from django.db import models


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
        indexes = [
            models.Index(fields=["status", "faculty", "difficulty"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"[{self.get_status_display()}] [{self.get_faculty_display()}] {self.question[:80]}"


class CVBuilder(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    name = models.CharField(max_length=120)
    short_description = models.CharField(max_length=240)
    link = models.URLField(max_length=500, unique=True)
    order = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    submitted_by_name = models.CharField(max_length=255, blank=True)
    submitted_by_email = models.EmailField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "name", "id"]
        indexes = [
            models.Index(fields=["status", "order", "name"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"[{self.get_status_display()}] {self.name}"
