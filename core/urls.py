from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, InterviewQuestionViewSet, ping, download, upload, summary

router = DefaultRouter()
router.register(r"profiles", ProfileViewSet)
router.register(r"questions", InterviewQuestionViewSet)

urlpatterns = router.urls + [
    path("summary/", summary, name="summary"),
    path("summary", summary, name="summary-no-slash"),
    path("ping/", ping, name="ping"),
    path("download/", download, name="download"),
    path("upload/", upload, name="upload"),
]
