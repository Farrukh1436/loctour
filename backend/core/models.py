"""Database models for the LocTur backend."""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model that adds created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Traveler(TimeStampedModel):
    """Represents a traveler sourced from the Telegram bot."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=32)
    telegram_handle = models.CharField(max_length=150, blank=True)
    telegram_id = models.CharField(max_length=150, unique=True)
    extra_info = models.TextField(blank=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class BotToken(TimeStampedModel):
    """Simple API token for Telegram bot integrations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, unique=True)
    token = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        status = "active" if self.is_active else "disabled"
        return f"{self.name} ({status})"


class Place(TimeStampedModel):
    """Catalog entry for travel destinations."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.0")), MaxValueValidator(Decimal("5.0"))],
        null=True,
        blank=True,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="places",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class PlacePhoto(TimeStampedModel):
    """Photo gallery for places."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="place_photos/")
    caption = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Photo for {self.place.name}"


class Trip(TimeStampedModel):
    """Trip definition created by admins."""

    STATUS_DRAFT = "draft"
    STATUS_REGISTRATION = "registration"
    STATUS_UPCOMING = "upcoming"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_REGISTRATION, "Registration"),
        (STATUS_UPCOMING, "Upcoming"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    place = models.ForeignKey(Place, on_delete=models.PROTECT, related_name="trips")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    registration_start = models.DateField()
    registration_end = models.DateField()
    trip_start = models.DateField()
    trip_end = models.DateField()
    default_price = models.DecimalField(max_digits=10, decimal_places=2)
    max_capacity = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    announce_in_channel = models.BooleanField(default=True)
    bonus_message = models.CharField(max_length=255, blank=True)
    custom_announcement_text = models.TextField(blank=True)
    group_chat_id = models.CharField(
        max_length=128,
        blank=True,
        help_text=(
            "Telegram chat identifier (e.g. -1001234567890) where confirmed travelers should be added."
        ),
    )
    group_invite_link = models.URLField(
        blank=True,
        help_text="Optional static invite link shared with travelers after payment confirmation.",
    )

    class Meta:
        ordering = ["-trip_start"]

    def __str__(self) -> str:
        return self.title

    @property
    def is_registration_open(self) -> bool:
        today = date.today()
        return self.registration_start <= today <= self.registration_end

    def participants_count(self) -> int:
        return (
            self.user_trips.filter(
                status=UserTrip.STATUS_CONFIRMED,
            ).count()
        )

    def total_income(self) -> Decimal:
        return (
            self.user_trips.filter(
                status=UserTrip.STATUS_CONFIRMED,
            ).aggregate(total=models.Sum("paid_amount"))["total"]
            or Decimal("0.00")
        )

    def total_expenses(self) -> Decimal:
        return self.expenses.aggregate(total=models.Sum("amount"))["total"] or Decimal("0.00")


class TripAnnouncement(TimeStampedModel):
    """Tracks announcement requests for trips."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="announcements")
    message = models.TextField()
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trip_announcements",
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self) -> str:
        return f"Announcement for {self.trip.title}"


class UserTrip(TimeStampedModel):
    """Join request made by a traveler."""

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_REJECTED = "rejected"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    PAYMENT_PENDING = "pending"
    PAYMENT_CONFIRMED = "confirmed"
    PAYMENT_REJECTED = "rejected"
    PAYMENT_CHOICES = [
        (PAYMENT_PENDING, "Pending"),
        (PAYMENT_CONFIRMED, "Confirmed"),
        (PAYMENT_REJECTED, "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="user_trips")
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE, related_name="user_trips")
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    payment_status = models.CharField(
        max_length=16, choices=PAYMENT_CHOICES, default=PAYMENT_PENDING
    )
    quoted_price = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    payment_note = models.TextField(blank=True)
    payment_proof = models.FileField(upload_to="payment_proofs/", blank=True)
    payment_proof_uploaded_at = models.DateTimeField(null=True, blank=True)
    custom_bonus_message = models.CharField(max_length=255, blank=True)
    admin_comment = models.TextField(blank=True)
    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="confirmed_user_trips",
        null=True,
        blank=True,
    )
    confirmed_at = models.DateTimeField(null=True, blank=True)
    group_joined_at = models.DateTimeField(null=True, blank=True)
    group_join_error = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("trip", "traveler")

    def __str__(self) -> str:
        return f"{self.traveler} -> {self.trip}"


class Expense(TimeStampedModel):
    """Tracks trip expenses for financial reporting."""

    CATEGORY_CHOICES = [
        ("transport", "Transport"),
        ("accommodation", "Accommodation"),
        ("food", "Food"),
        ("activity", "Activity"),
        ("other", "Other"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="expenses")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default="other")
    description = models.TextField(blank=True)
    incurred_at = models.DateField()
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recorded_expenses",
    )

    class Meta:
        ordering = ["-incurred_at", "-created_at"]

    def __str__(self) -> str:
        return f"{self.trip.title} - {self.amount}"
