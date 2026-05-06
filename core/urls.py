from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CVBuilderViewSet, InterviewQuestionViewSet, download, health, ping, send_alert_email, upload

router = DefaultRouter()
router.register(r"questions", InterviewQuestionViewSet)
router.register(r"cv-builders", CVBuilderViewSet)

urlpatterns = router.urls + [
    path("alerts/email/", send_alert_email, name="send-alert-email"),
    path("health/", health, name="health"),
    path("ping/", ping, name="ping"),
    path("download/", download, name="download"),
    path("upload/", upload, name="upload"),
]
