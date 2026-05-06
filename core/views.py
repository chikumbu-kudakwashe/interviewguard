from django.db.models import Count
from .models import Profile, InterviewQuestion
from .serializers import ProfileSerializer, InterviewQuestionSerializer, InterviewQuestionSubmitSerializer
from rest_framework import viewsets, filters, mixins
from rest_framework.decorators import action, api_view
from .services import Alerts
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from .utils import get_client_ip
from django.http import FileResponse, HttpResponse


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.order_by("id")
    serializer_class = ProfileSerializer
    lookup_field = "uuid"

    def get_queryset(self):
        qs = super().get_queryset()
        uuid_param = self.request.query_params.get("uuid")
        if getattr(self, "action", None) == "list":
            if uuid_param:
                return qs.filter(uuid=uuid_param)
            return qs.none()
        return qs

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["ip_address"] = get_client_ip(request)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def send_email(self, request, uuid=None):
        profile = self.get_object()
        message = (request.data.get("message") or "").strip()
        if not message:
            return Response({"error": "Message is required."}, status=status.HTTP_400_BAD_REQUEST)
        res = Alerts.send_email(profile, message)
        if not res:
            return Response({"message": "Error sending email"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Email sent!"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def download_cv(self, request, uuid=None):
        profile = self.get_object()
        if not profile.cv:
            return Response({"error": "CV not found"}, status=status.HTTP_404_NOT_FOUND)
        return FileResponse(profile.cv.open(), as_attachment=True, filename=profile.cv.name.split('/')[-1])


class InterviewQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = InterviewQuestion.objects.filter(status="approved")
    serializer_class = InterviewQuestionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["question", "tags", "faculty"]

    def get_queryset(self):
        qs = super().get_queryset()
        faculty = self.request.query_params.get("faculty")
        difficulty = self.request.query_params.get("difficulty")
        if faculty:
            qs = qs.filter(faculty=faculty)
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        return qs

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def submit(self, request):
        serializer = InterviewQuestionSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save()

        # Optional: notify admin by email
        Alerts.notify_admin_of_submission(question)

        return Response(
            {
                "message": "Thank you! Your question has been submitted for review.",
                "detail": "Our team will review your contribution. Once approved, it will appear in the prep section for all users.",
                "status": "pending",
                "id": question.id,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser])
    def pending(self, request):
        queryset = InterviewQuestion.objects.filter(status="pending").order_by("-created_at")
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


@api_view(["GET"])
def summary(request):
    questions = InterviewQuestion.objects.all()
    approved = questions.filter(status="approved")

    by_faculty = []
    counts_by_faculty = {
        row["faculty"]: row["count"]
        for row in approved.values("faculty").annotate(count=Count("id"))
    }
    for code, label in InterviewQuestion.FACULTY_CHOICES:
        by_faculty.append({
            "faculty": code,
            "faculty_label": label,
            "approved_count": counts_by_faculty.get(code, 0),
        })

    by_difficulty = {
        row["difficulty"]: row["count"]
        for row in approved.values("difficulty").annotate(count=Count("id"))
    }

    latest = approved.order_by("-created_at")[:5]
    return Response(
        {
            "questions": {
                "total": questions.count(),
                "approved": approved.count(),
                "pending": questions.filter(status="pending").count(),
                "rejected": questions.filter(status="rejected").count(),
            },
            "profiles": {
                "total": Profile.objects.count(),
            },
            "faculties": by_faculty,
            "difficulties": [
                {
                    "difficulty": code,
                    "difficulty_label": label,
                    "approved_count": by_difficulty.get(code, 0),
                }
                for code, label in InterviewQuestion.DIFFICULTY_CHOICES
            ],
            "latest_questions": InterviewQuestionSerializer(latest, many=True).data,
        },
        status=status.HTTP_200_OK,
    )

@api_view(["GET"])
def ping(request):
    dl = request.query_params.get("dl")
    if dl:
        try:
            size = max(0, min(int(dl), 2000000))
            return HttpResponse('0' * size, content_type='text/plain')
        except ValueError:
            pass
    return Response({"status": "ok"}, status=status.HTTP_200_OK)

@api_view(["GET"])
def download(request):
    size_param = request.query_params.get("size", 0)
    try:
        size = max(0, min(int(size_param), 2000000))  # Cap at 2MB for safety
        return HttpResponse('0' * size, content_type='application/octet-stream')
    except ValueError:
        return HttpResponse(status=400)

@api_view(["POST"])
def upload(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)
