"""API views for LocTur backend."""
from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.conf import settings
import os
from pathlib import Path
from rest_framework import mixins, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token

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

        # Generate daily breakdown data for the chart
        daily_data = []
        current_date = start_dt
        while current_date <= end_dt:
            # Income for this day
            daily_income = models.UserTrip.objects.filter(
                status=models.UserTrip.STATUS_CONFIRMED,
                confirmed_at__date=current_date
            ).aggregate(total=Sum("paid_amount"))["total"] or Decimal("0.00")
            
            # Expenses for this day
            daily_expenses = models.Expense.objects.filter(
                incurred_at=current_date
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
            
            daily_data.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "income": float(daily_income),
                "expenses": float(daily_expenses),
                "net": float(daily_income - daily_expenses)
            })
            
            current_date += timedelta(days=1)

        data = {
            "range_days": days,
            "income_total": income_total,
            "expenses_total": expenses_total,
            "net": income_total - expenses_total,
            "outstanding_total": outstanding_total,
            "active_registrations": list(active_registrations),
            "daily_data": daily_data,
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


class LoginView(APIView):
    """Handle user login for the admin panel."""

    permission_classes = [AllowAny]
    authentication_classes = [SessionAuthentication]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active and user.is_staff:
                login(request, user)
                return Response({
                    "detail": "Login successful.",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "is_staff": user.is_staff,
                    }
                })
            else:
                return Response(
                    {"detail": "Account is not active or does not have admin privileges."},
                    status=status.HTTP_403_FORBIDDEN
                )
        else:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    """Handle user logout."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"detail": "Logout successful."})


class UserView(APIView):
    """Get current user information."""

    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
        })


class CSRFTokenView(APIView):
    """Get CSRF token for frontend authentication."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class FileStatsView(APIView):
    """Get file statistics for dashboard."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        media_root = settings.MEDIA_ROOT
        
        # Count files in payment_proofs directory
        payment_proofs_dir = Path(media_root) / "payment_proofs"
        payment_proofs_count = 0
        payment_proofs_size = 0
        
        if payment_proofs_dir.exists():
            for file_path in payment_proofs_dir.iterdir():
                if file_path.is_file():
                    payment_proofs_count += 1
                    payment_proofs_size += file_path.stat().st_size
        
        # Count files in place_photos directory
        place_photos_dir = Path(media_root) / "place_photos"
        place_photos_count = 0
        place_photos_size = 0
        
        if place_photos_dir.exists():
            for file_path in place_photos_dir.iterdir():
                if file_path.is_file():
                    place_photos_count += 1
                    place_photos_size += file_path.stat().st_size
        
        total_count = payment_proofs_count + place_photos_count
        total_size = payment_proofs_size + place_photos_size
        
        return Response({
            "payment_proofs": {
                "count": payment_proofs_count,
                "size": payment_proofs_size,
                "size_mb": round(payment_proofs_size / (1024 * 1024), 2)
            },
            "place_photos": {
                "count": place_photos_count,
                "size": place_photos_size,
                "size_mb": round(place_photos_size / (1024 * 1024), 2)
            },
            "total": {
                "count": total_count,
                "size": total_size,
                "size_mb": round(total_size / (1024 * 1024), 2)
            }
        })


class BulkDeleteFilesView(APIView):
    """Delete specified number of oldest files."""

    permission_classes = [IsAdminUser]

    def post(self, request):
        count_to_delete = request.data.get("count", 0)
        
        if not isinstance(count_to_delete, int) or count_to_delete <= 0:
            return Response(
                {"detail": "Invalid count. Must be a positive integer."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        media_root = settings.MEDIA_ROOT
        deleted_files = []
        
        # Get all files with their modification times
        all_files = []
        
        for directory in ["payment_proofs", "place_photos"]:
            dir_path = Path(media_root) / directory
            if dir_path.exists():
                for file_path in dir_path.iterdir():
                    if file_path.is_file():
                        all_files.append((file_path.stat().st_mtime, file_path))
        
        # Sort by modification time (oldest first)
        all_files.sort(key=lambda x: x[0])
        
        # Delete the oldest files
        files_deleted = 0
        for _, file_path in all_files:
            if files_deleted >= count_to_delete:
                break
            
            try:
                file_size = file_path.stat().st_size
                file_path.unlink()
                deleted_files.append({
                    "path": str(file_path.relative_to(media_root)),
                    "size": file_size
                })
                files_deleted += 1
            except OSError as e:
                continue
        
        total_size_deleted = sum(f["size"] for f in deleted_files)
        
        return Response({
            "deleted_count": files_deleted,
            "deleted_size": total_size_deleted,
            "deleted_size_mb": round(total_size_deleted / (1024 * 1024), 2),
            "deleted_files": deleted_files
        })


class TripFileStatsView(APIView):
    """Get file statistics for a specific trip."""

    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            trip = models.Trip.objects.get(id=pk)
        except models.Trip.DoesNotExist:
            return Response(
                {"detail": "Trip not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Count payment proof files for this trip
        user_trips = trip.user_trips.all()
        payment_proofs_count = 0
        payment_proofs_size = 0
        
        for user_trip in user_trips:
            if user_trip.payment_proof:
                try:
                    file_path = user_trip.payment_proof.path
                    if os.path.exists(file_path):
                        payment_proofs_count += 1
                        payment_proofs_size += os.path.getsize(file_path)
                except (ValueError, OSError):
                    continue
        
        # Count place photos for this trip's place
        place_photos_count = 0
        place_photos_size = 0
        
        for photo in trip.place.photos.all():
            try:
                file_path = photo.image.path
                if os.path.exists(file_path):
                    place_photos_count += 1
                    place_photos_size += os.path.getsize(file_path)
            except (ValueError, OSError):
                continue
        
        total_count = payment_proofs_count + place_photos_count
        total_size = payment_proofs_size + place_photos_size
        
        return Response({
            "trip_id": str(trip.id),
            "trip_title": trip.title,
            "payment_proofs": {
                "count": payment_proofs_count,
                "size": payment_proofs_size,
                "size_mb": round(payment_proofs_size / (1024 * 1024), 2)
            },
            "place_photos": {
                "count": place_photos_count,
                "size": place_photos_size,
                "size_mb": round(place_photos_size / (1024 * 1024), 2)
            },
            "total": {
                "count": total_count,
                "size": total_size,
                "size_mb": round(total_size / (1024 * 1024), 2)
            }
        })


class TripDeleteFilesView(APIView):
    """Delete all files associated with a trip."""

    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            trip = models.Trip.objects.get(id=pk)
        except models.Trip.DoesNotExist:
            return Response(
                {"detail": "Trip not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        deleted_files = []
        
        # Delete payment proof files
        for user_trip in trip.user_trips.all():
            if user_trip.payment_proof:
                try:
                    file_path = user_trip.payment_proof.path
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_files.append({
                            "type": "payment_proof",
                            "path": str(user_trip.payment_proof),
                            "size": file_size
                        })
                        # Clear the file field
                        user_trip.payment_proof = None
                        user_trip.save()
                except (ValueError, OSError):
                    continue
        
        # Delete place photos
        for photo in trip.place.photos.all():
            try:
                file_path = photo.image.path
                if os.path.exists(file_path):
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    deleted_files.append({
                        "type": "place_photo",
                        "path": str(photo.image),
                        "size": file_size
                    })
                    # Delete the photo record
                    photo.delete()
            except (ValueError, OSError):
                continue
        
        total_size_deleted = sum(f["size"] for f in deleted_files)
        
        return Response({
            "trip_id": str(trip.id),
            "trip_title": trip.title,
            "deleted_count": len(deleted_files),
            "deleted_size": total_size_deleted,
            "deleted_size_mb": round(total_size_deleted / (1024 * 1024), 2),
            "deleted_files": deleted_files
        })


class SettingsViewSet(viewsets.ModelViewSet):
    """CRUD operations for application settings."""

    queryset = models.Settings.objects.all()
    serializer_class = serializers.SettingsSerializer
    permission_classes = [permissions.IsStaffOrBotReadOnly]

    def get_object(self):
        """Get or create the single settings instance."""
        settings_obj, created = models.Settings.objects.get_or_create(
            defaults={
                'payment_instructions': 'Send payment screenshot to the bot.',
                'support_contacts': ''
            }
        )
        return settings_obj

    def list(self, request, *args, **kwargs):
        """Return the single settings instance."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Return the single settings instance."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        """Update the single settings instance."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """Partially update the single settings instance."""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Prevent creating new settings instances."""
        return Response(
            {"detail": "Settings instance already exists. Use PUT to update."},
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Prevent deleting the settings instance."""
        return Response(
            {"detail": "Settings instance cannot be deleted."},
            status=status.HTTP_400_BAD_REQUEST
        )


class SettingsUpdateView(APIView):
    """Custom view to handle PUT requests to the settings list endpoint."""
    
    permission_classes = [IsAdminUser]
    
    def put(self, request):
        """Update the settings instance."""
        settings_obj, created = models.Settings.objects.get_or_create(
            defaults={
                'payment_instructions': 'Send payment screenshot to the bot.',
                'support_contacts': ''
            }
        )
        serializer = serializers.SettingsSerializer(settings_obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
