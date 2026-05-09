from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from django.views.decorators.cache import cache_control
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, parser_classes, throttle_classes
from rest_framework.parsers import BaseParser, FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import CVBuilder, InterviewQuestion
from .serializers import (
    AlertEmailSerializer,
    CVBuilderSerializer,
    CVBuilderSubmitSerializer,
    InterviewQuestionSerializer,
    InterviewQuestionSubmitSerializer,
)
from .services import Alerts
from .throttles import AlertEmailRateThrottle, CVBuilderSubmitRateThrottle, QuestionSubmitRateThrottle


class OctetStreamParser(BaseParser):
    media_type = "application/octet-stream"

    def parse(self, stream, media_type=None, parser_context=None):
        return {}


FRONTEND_ASSETS = {
    "interviewguard-logo.png": ("interviewguard.png", "image/png"),
    "interviewguard-logo.ico": ("interviewguard-logo.ico", "image/x-icon"),
}


@cache_control(public=True, max_age=60 * 60 * 24)
def frontend_asset(request, asset_name):
    asset = FRONTEND_ASSETS.get(asset_name)
    if not asset:
        raise Http404("Asset not found.")

    filename, content_type = asset
    path = Path(settings.BASE_DIR) / "frontend" / filename
    if not path.exists():
        raise Http404("Asset not found.")

    return FileResponse(path.open("rb"), content_type=content_type)


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
        return qs.order_by("faculty", "order", "difficulty", "id")

    @action(detail=False, methods=["post"], permission_classes=[AllowAny], throttle_classes=[QuestionSubmitRateThrottle])
    def submit(self, request):
        serializer = InterviewQuestionSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save()

        Alerts.notify_admin_of_submission(question)
        Alerts.notify_submitter_of_submission(question)

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


class CVBuilderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CVBuilder.objects.filter(status="approved")
    serializer_class = CVBuilderSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "short_description", "link"]

    def get_queryset(self):
        return super().get_queryset().order_by("order", "name", "id")

    @action(detail=False, methods=["post"], permission_classes=[AllowAny], throttle_classes=[CVBuilderSubmitRateThrottle])
    def submit(self, request):
        serializer = CVBuilderSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        builder = serializer.save()

        Alerts.notify_admin_of_cv_builder_submission(builder)
        Alerts.notify_submitter_of_cv_builder_submission(builder)

        return Response(
            {
                "message": "Thank you! Your CV builder has been submitted for review.",
                "detail": "Once approved, it will appear in the recommended builders list.",
                "status": "pending",
                "id": builder.id,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAdminUser])
    def pending(self, request):
        queryset = CVBuilder.objects.filter(status="pending").order_by("-created_at")
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

@api_view(["POST"])
@throttle_classes([AlertEmailRateThrottle])
def send_alert_email(request):
    serializer = AlertEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    sent = Alerts.send_email(**serializer.validated_data)
    if not sent:
        return Response({"message": "Error sending email"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"message": "Email sent!"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)

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
@parser_classes([JSONParser, FormParser, MultiPartParser, OctetStreamParser])
def upload(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)
