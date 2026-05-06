from rest_framework import serializers
from .models import CVBuilder, InterviewQuestion


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
        if len(value) < 10:
            raise serializers.ValidationError("Question must be at least 10 characters.")
        return value

    def validate_answer(self, value):
        value = value.strip()
        if len(value) < 20:
            raise serializers.ValidationError("Suggested answer must be at least 20 characters.")
        return value

    def validate_tags(self, value):
        return ", ".join(tag.strip() for tag in value.split(",") if tag.strip())

    def create(self, validated_data):
        validated_data["status"] = "pending"
        return super().create(validated_data)


class AlertEmailSerializer(serializers.Serializer):
    to_email = serializers.EmailField()
    reply_to = serializers.EmailField(required=False, allow_blank=True)
    message = serializers.CharField(min_length=20, max_length=5000, trim_whitespace=True)


class CVBuilderSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    icon_letter = serializers.SerializerMethodField()

    class Meta:
        model = CVBuilder
        fields = [
            "id", "name", "short_description", "link", "icon_letter",
            "order", "status", "status_label", "created_at",
        ]
        read_only_fields = ["id", "icon_letter", "order", "status", "status_label", "created_at"]

    def get_icon_letter(self, obj):
        return (obj.name or "?").strip()[:1].upper() or "?"


class CVBuilderSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = CVBuilder
        fields = [
            "id", "name", "short_description", "link",
            "submitted_by_name", "submitted_by_email",
            "status", "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Builder name must be at least 2 characters.")
        return value

    def validate_short_description(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters.")
        return value

    def validate_link(self, value):
        value = value.strip()
        if not value.startswith(("http://", "https://")):
            raise serializers.ValidationError("Link must start with http:// or https://.")
        if CVBuilder.objects.filter(link__iexact=value).exists():
            raise serializers.ValidationError("This CV builder has already been submitted.")
        return value

    def create(self, validated_data):
        validated_data["status"] = "pending"
        return super().create(validated_data)
