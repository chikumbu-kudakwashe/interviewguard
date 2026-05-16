from django.contrib import admin
from django.urls import path, include
from core.views import frontend_asset

urlpatterns = [
    path("interviewguard-logo.png", frontend_asset, {"asset_name": "interviewguard-logo.png"}, name="interviewguard-logo"),
    path("interviewguard-logo.ico", frontend_asset, {"asset_name": "interviewguard-logo.ico"}, name="interviewguard-favicon"),
    path('admin/', admin.site.urls),
    path('', include("core.urls"))
]
