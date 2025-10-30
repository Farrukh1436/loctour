"""URL configuration for LocTur backend."""
from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from core import views

router = routers.DefaultRouter()
router.register("travelers", views.TravelerViewSet, basename="traveler")
router.register("places", views.PlaceViewSet, basename="place")
router.register("place-photos", views.PlacePhotoViewSet, basename="place-photo")
router.register("trips", views.TripViewSet, basename="trip")
router.register("user-trips", views.UserTripViewSet, basename="user-trip")
router.register("expenses", views.ExpenseViewSet, basename="expense")
router.register("announcements", views.TripAnnouncementViewSet, basename="announcement")
router.register("bot-tokens", views.BotTokenViewSet, basename="bot-token")
router.register("settings", views.SettingsViewSet, basename="settings")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/login/", views.LoginView.as_view(), name="login"),
    path("api/auth/logout/", views.LogoutView.as_view(), name="logout"),
    path("api/auth/user/", views.UserView.as_view(), name="user"),
    path("api/auth/csrf/", views.CSRFTokenView.as_view(), name="csrf-token"),
    path("api/auth/", include("rest_framework.urls")),
    path("api/files/stats/", views.FileStatsView.as_view(), name="file-stats"),
    path("api/files/bulk-delete/", views.BulkDeleteFilesView.as_view(), name="bulk-delete-files"),
    path("api/trips/<uuid:pk>/files/stats/", views.TripFileStatsView.as_view(), name="trip-file-stats"),
    path("api/trips/<uuid:pk>/files/delete/", views.TripDeleteFilesView.as_view(), name="trip-delete-files"),
    path("api/metrics/overview/", views.OverviewMetricsView.as_view(), name="metrics-overview"),
    path("api/trips/<uuid:pk>/participants/", views.TripParticipantsView.as_view(), name="trip-participants"),
    path(
        "api/trips/<uuid:pk>/toggle-announcement/",
        views.TripAnnouncementToggleView.as_view(),
        name="trip-toggle-announcement",
    ),
    path(
        "api/trips/<uuid:pk>/link-group/",
        views.TripLinkGroupView.as_view(),
        name="trip-link-group",
    ),
    path(
        "api/user-trips/<uuid:pk>/group-join/",
        views.UserTripGroupJoinView.as_view(),
        name="user-trip-group-join",
    ),
    path("api/settings/update/", views.SettingsUpdateView.as_view(), name="settings-update"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
