from django.contrib import admin
from .models import Profile, InterviewQuestion
from django.utils import timezone

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "email", "phone", "created_at"]
    search_fields = ["full_name", "email"]


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ["status", "faculty", "difficulty", "question_preview", "submitted_by_name", "order", "created_at"]
    list_filter = ["status", "faculty", "difficulty"]
    search_fields = ["question", "answer", "tags", "submitted_by_name", "submitted_by_email"]
    ordering = ["status", "faculty", "order"]
    actions = ["approve_questions", "reject_questions"]
    readonly_fields = ["created_at"]

    def question_preview(self, obj):
        return obj.question[:80] + ("..." if len(obj.question) > 80 else "")
    question_preview.short_description = "Question"

    @admin.action(description="Approve selected questions")
    def approve_questions(self, request, queryset):
        queryset.update(status="approved", reviewed_at=timezone.now())

    @admin.action(description="Reject selected questions")
    def reject_questions(self, request, queryset):
        queryset.exclude(status="approved").update(status="rejected", reviewed_at=timezone.now())


@admin.action(description="Approve selected questions")
def approve_questions(modeladmin, request, queryset):
    queryset.update(status="approved", reviewed_at=timezone.now())


@admin.action(description="Reject selected questions")
def reject_questions(modeladmin, request, queryset):
    queryset.exclude(status="approved").update(status="rejected", reviewed_at=timezone.now())
