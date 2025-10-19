"""API views for LocTur backend."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import mixins, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from . import filters, models, permissions, serializers


class TravelerViewSet(viewsets.ModelViewSet):
    """CRUD operations for travelers."""

    queryset = models.Traveler.objects.all()
    serializer_class = serializers.TravelerSerializer
    filterset_fields = ["telegram_id"]
    search_fields = ["first_name", "last_name", "phone_number", "telegram_handle"]
    permission_classes = [permissions.IsStaffOrBotForWrite]


class PlaceViewSet(viewsets.ModelViewSet):
    """CRUD operations for places."""

    queryset = models.Place.objects.prefetch_related("photos").all()
    serializer_class = serializers.PlaceSerializer
    permission_classes = [permissions.IsStaffOrReadOnly]
    search_fields = ["name"]


class PlacePhotoViewSet(viewsets.ModelViewSet):
    """Manage place photo gallery."""

    queryset = models.PlacePhoto.objects.select_related("place").all()
    serializer_class = serializers.PlacePhotoSerializer
    permission_classes = [IsAdminUser]


class TripViewSet(viewsets.ModelViewSet):
    """Manage trips."""

    queryset = models.Trip.objects.select_related("place").all()
    serializer_class = serializers.TripSerializer
    filterset_class = filters.TripFilter
    permission_classes = [permissions.IsStaffOrReadOnly]
    ordering_fields = ["trip_start", "trip_end", "created_at"]
    search_fields = ["title", "place__name"]


class UserTripViewSet(viewsets.ModelViewSet):
    """Join requests made by travelers."""

    queryset = models.UserTrip.objects.select_related("trip", "traveler").all()
    serializer_class = serializers.UserTripSerializer
    filterset_class = filters.UserTripFilter
    permission_classes = [permissions.IsStaffOrBotForWrite]
    ordering_fields = ["created_at", "confirmed_at"]

    def perform_create(self, serializer):
        serializer.save(payment_status=models.UserTrip.PAYMENT_PENDING, status=models.UserTrip.STATUS_PENDING)


class ExpenseViewSet(viewsets.ModelViewSet):
    """Manage trip expenses for accounting."""

    queryset = models.Expense.objects.select_related("trip", "recorded_by").all()
    serializer_class = serializers.ExpenseSerializer
    filterset_class = filters.ExpenseFilter
    permission_classes = [IsAdminUser]
    ordering_fields = ["incurred_at", "amount"]


class TripAnnouncementViewSet(viewsets.ModelViewSet):
    """Track announcement events for trips."""

    queryset = models.TripAnnouncement.objects.select_related("trip", "sent_by").all()
    serializer_class = serializers.TripAnnouncementSerializer
    permission_classes = [IsAdminUser]


class BotTokenViewSet(viewsets.ModelViewSet):
    """Manage bot tokens used for authenticating Telegram bots."""

    queryset = models.BotToken.objects.all()
    serializer_class = serializers.BotTokenSerializer
    permission_classes = [IsAdminUser]


class OverviewMetricsView(APIView):
    """Returns financial and registration metrics for dashboards."""

    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        range_param = request.query_params.get("range", "30d")
        try:
            days = int(range_param.rstrip("d"))
        except ValueError:
            return Response({"detail": "Invalid range parameter."}, status=status.HTTP_400_BAD_REQUEST)

        end_dt = timezone.now().date()
        start_dt = end_dt - timedelta(days=days)

        confirmed_user_trips = models.UserTrip.objects.filter(
            status=models.UserTrip.STATUS_CONFIRMED, confirmed_at__date__gte=start_dt
        )
        income_total = confirmed_user_trips.aggregate(total=Sum("paid_amount"))["total"] or Decimal("0.00")

        expenses_total = (
            models.Expense.objects.filter(incurred_at__gte=start_dt).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        outstanding_total = (
            models.UserTrip.objects.filter(
                payment_status=models.UserTrip.PAYMENT_PENDING,
                created_at__date__gte=start_dt,
            ).aggregate(total=Sum("quoted_price"))["total"]
            or Decimal("0.00")
        )

        active_registrations = (
            models.Trip.objects.filter(status=models.Trip.STATUS_REGISTRATION)
            .annotate(signups=Count("user_trips"))
            .values("id", "title", "signups", "default_price")
        )

        data = {
            "range_days": days,
            "income_total": income_total,
            "expenses_total": expenses_total,
            "net": income_total - expenses_total,
            "outstanding_total": outstanding_total,
            "active_registrations": list(active_registrations),
        }
        return Response(data)


class TripParticipantsView(ListAPIView):
    """List confirmed participants for a trip with payment status."""

    serializer_class = serializers.UserTripSerializer
    permission_classes = [IsAdminUser]
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        trip_id = self.kwargs["pk"]
        return models.UserTrip.objects.filter(trip_id=trip_id).select_related("traveler", "trip")


class TripAnnouncementToggleView(APIView):
    """Toggle the announcement flag for a trip."""

    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        trip_id = kwargs.get("pk")
        try:
            trip = models.Trip.objects.get(id=trip_id)
        except models.Trip.DoesNotExist:
            return Response({"detail": "Trip not found."}, status=status.HTTP_404_NOT_FOUND)

        trip.announce_in_channel = not trip.announce_in_channel
        trip.save(update_fields=["announce_in_channel"])

        return Response({"id": str(trip.id), "announce_in_channel": trip.announce_in_channel})


class TripLinkGroupView(APIView):
    """Allow bots to register the Telegram group metadata for a trip."""

    permission_classes = [permissions.IsStaffOrBotForWrite]

    def post(self, request, *args, **kwargs):
        trip_id = kwargs.get("pk")
        try:
            trip = models.Trip.objects.get(id=trip_id)
        except models.Trip.DoesNotExist:
            return Response({"detail": "Trip not found."}, status=status.HTTP_404_NOT_FOUND)

        chat_id = request.data.get("chat_id")
        if not chat_id:
            return Response({"detail": "chat_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            chat_id_int = int(chat_id)
        except (TypeError, ValueError):
            return Response({"detail": "chat_id must be numeric."}, status=status.HTTP_400_BAD_REQUEST)

        invite_link = (request.data.get("invite_link") or "").strip()

        update_fields = ["group_chat_id"]
        trip.group_chat_id = str(chat_id_int)
        if invite_link:
            trip.group_invite_link = invite_link
            update_fields.append("group_invite_link")

        trip.save(update_fields=update_fields)

        serializer = serializers.TripSerializer(instance=trip, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserTripGroupJoinView(APIView):
    """Allow bots to record the outcome of adding a traveler to the trip's Telegram group."""

    permission_classes = [permissions.IsStaffOrBotForWrite]

    def post(self, request, *args, **kwargs):
        user_trip_id = kwargs.get("pk")
        try:
            user_trip = models.UserTrip.objects.get(id=user_trip_id)
        except models.UserTrip.DoesNotExist:
            return Response({"detail": "User trip not found."}, status=status.HTTP_404_NOT_FOUND)

        success = bool(request.data.get("success"))
        error_message = request.data.get("error", "")

        update_fields = []
        if success:
            user_trip.group_joined_at = timezone.now()
            user_trip.group_join_error = ""
            update_fields.extend(["group_joined_at", "group_join_error"])
        else:
            if not error_message:
                return Response({"detail": "Error message required when success is false."}, status=status.HTTP_400_BAD_REQUEST)
            user_trip.group_join_error = error_message
            update_fields.append("group_join_error")

        user_trip.save(update_fields=update_fields)
        serializer = serializers.UserTripSerializer(instance=user_trip, context={"request": request})
        return Response(serializer.data)
