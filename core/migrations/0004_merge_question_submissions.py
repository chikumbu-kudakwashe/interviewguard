# Generated for InterviewGuard question workflow cleanup.

from django.db import migrations, models


def merge_submitted_questions(apps, schema_editor):
    InterviewQuestion = apps.get_model("core", "InterviewQuestion")
    SubmittedQuestion = apps.get_model("core", "SubmittedQuestion")

    InterviewQuestion.objects.all().update(status="approved")

    for submitted in SubmittedQuestion.objects.all():
        obj, _ = InterviewQuestion.objects.update_or_create(
            question=submitted.question,
            defaults={
                "faculty": submitted.faculty,
                "difficulty": submitted.difficulty,
                "answer": submitted.answer,
                "tip": submitted.tip,
                "tags": submitted.tags,
                "status": submitted.status,
                "submitted_by_name": submitted.submitted_by_name,
                "submitted_by_email": submitted.submitted_by_email,
                "reviewed_at": submitted.reviewed_at,
                "reviewer_note": submitted.reviewer_note,
            },
        )
        InterviewQuestion.objects.filter(pk=obj.pk).update(created_at=submitted.submitted_at)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_submittedquestion"),
    ]

    operations = [
        migrations.AddField(
            model_name="interviewquestion",
            name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="interviewquestion",
            name="reviewer_note",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="interviewquestion",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="interviewquestion",
            name="submitted_by_email",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name="interviewquestion",
            name="submitted_by_name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterModelOptions(
            name="interviewquestion",
            options={"ordering": ["faculty", "order", "difficulty", "id"]},
        ),
        migrations.RunPython(merge_submitted_questions, noop_reverse),
        migrations.DeleteModel(
            name="SubmittedQuestion",
        ),
    ]
