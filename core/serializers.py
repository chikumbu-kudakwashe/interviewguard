from rest_framework import serializers
from .models import Profile, InterviewQuestion


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"
        read_only_fields = ["uuid", "created_at", "ip_address"]


class InterviewQuestionSerializer(serializers.ModelSerializer):
    faculty_label = serializers.CharField(source="get_faculty_display", read_only=True)
    difficulty_label = serializers.CharField(source="get_difficulty_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = InterviewQuestion
        fields = [
            "id", "faculty", "faculty_label",
            "difficulty", "difficulty_label",
            "question", "answer", "tip", "tags", "order",
            "status", "status_label", "created_at",
        ]
        read_only_fields = ["id", "status", "status_label", "created_at", "order"]


class InterviewQuestionSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewQuestion
        fields = [
            "id", "faculty", "difficulty", "question", "answer",
            "tip", "tags", "submitted_by_name", "submitted_by_email",
            "status", "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate_question(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Question is required.")
        return value

    def validate_answer(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Suggested answer is required.")
        return value

    def create(self, validated_data):
        validated_data["status"] = "pending"
        return super().create(validated_data)
