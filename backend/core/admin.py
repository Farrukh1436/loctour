"""Admin registrations for core models."""
from __future__ import annotations

from django.contrib import admin

from . import models


@admin.register(models.Traveler)
class TravelerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone_number", "telegram_handle", "telegram_id")
    search_fields = ("first_name", "last_name", "phone_number", "telegram_handle", "telegram_id")
    ordering = ("first_name", "last_name")


class PlacePhotoInline(admin.TabularInline):
    model = models.PlacePhoto
    extra = 0


@admin.register(models.Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude", "rating", "created_at")
    search_fields = ("name",)
    inlines = [PlacePhotoInline]


class ExpenseInline(admin.TabularInline):
    model = models.Expense
    extra = 0


@admin.register(models.Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "place",
        "trip_start",
        "trip_end",
        "status",
        "max_capacity",
        "default_price",
        "group_chat_id",
    )
    search_fields = ("title", "place__name")
    list_filter = ("status", "trip_start", "trip_end")
    inlines = [ExpenseInline]


@admin.register(models.UserTrip)
class UserTripAdmin(admin.ModelAdmin):
    list_display = (
        "traveler",
        "trip",
        "status",
        "payment_status",
        "quoted_price",
        "paid_amount",
        "group_joined_at",
        "created_at",
    )
    search_fields = ("traveler__first_name", "traveler__last_name", "trip__title")
    list_filter = ("status", "payment_status")
    readonly_fields = ("group_joined_at", "group_join_error")


@admin.register(models.Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("trip", "amount", "category", "incurred_at", "recorded_by")
    list_filter = ("category", "incurred_at")
    search_fields = ("trip__title",)


@admin.register(models.PlacePhoto)
class PlacePhotoAdmin(admin.ModelAdmin):
    list_display = ("place", "created_at")
    search_fields = ("place__name",)


@admin.register(models.TripAnnouncement)
class TripAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("trip", "sent_at", "delivered")
    search_fields = ("trip__title",)
    list_filter = ("delivered",)


@admin.register(models.BotToken)
class BotTokenAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    search_fields = ("name", "token")
    list_filter = ("is_active",)
