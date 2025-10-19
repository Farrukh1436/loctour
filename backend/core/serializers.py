"""Serializers for LocTur backend APIs."""
from __future__ import annotations

from decimal import Decimal

from django.utils import timezone
from rest_framework import serializers

from . import models


class TravelerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Traveler
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "telegram_handle",
            "telegram_id",
            "extra_info",
            "created_at",
            "updated_at",
        ]


class BotTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BotToken
        fields = ["id", "name", "token", "is_active", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]


class PlacePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PlacePhoto
        fields = ["id", "place", "image", "caption", "created_at"]
        read_only_fields = ["id", "created_at"]


class PlaceSerializer(serializers.ModelSerializer):
    photos = PlacePhotoSerializer(many=True, read_only=True)

    class Meta:
        model = models.Place
        fields = [
            "id",
            "name",
            "description",
            "latitude",
            "longitude",
            "rating",
            "created_by",
            "created_at",
            "updated_at",
            "photos",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["created_by"] = request.user
        return super().create(validated_data)


class TripSerializer(serializers.ModelSerializer):
    place_detail = PlaceSerializer(source="place", read_only=True)
    participants_count = serializers.SerializerMethodField()
    total_income = serializers.SerializerMethodField()
    total_expenses = serializers.SerializerMethodField()
    net_income = serializers.SerializerMethodField()
    is_registration_open = serializers.ReadOnlyField()

    class Meta:
        model = models.Trip
        fields = [
            "id",
            "place",
            "place_detail",
            "title",
            "description",
            "registration_start",
            "registration_end",
            "trip_start",
            "trip_end",
            "default_price",
            "max_capacity",
            "status",
            "announce_in_channel",
            "bonus_message",
            "custom_announcement_text",
            "group_chat_id",
            "group_invite_link",
            "is_registration_open",
            "participants_count",
            "total_income",
            "total_expenses",
            "net_income",
            "created_at",
            "updated_at",
        ]

    def get_participants_count(self, obj: models.Trip) -> int:
        return obj.participants_count()

    def get_total_income(self, obj: models.Trip) -> Decimal:
        return obj.total_income()

    def get_total_expenses(self, obj: models.Trip) -> Decimal:
        return obj.total_expenses()

    def get_net_income(self, obj: models.Trip) -> Decimal:
        return obj.total_income() - obj.total_expenses()

    def validate(self, attrs):
        registration_start = attrs.get("registration_start", getattr(self.instance, "registration_start", None))
        registration_end = attrs.get("registration_end", getattr(self.instance, "registration_end", None))
        trip_start = attrs.get("trip_start", getattr(self.instance, "trip_start", None))
        trip_end = attrs.get("trip_end", getattr(self.instance, "trip_end", None))
        group_chat_id = attrs.get("group_chat_id", getattr(self.instance, "group_chat_id", ""))
        group_invite_link = attrs.get("group_invite_link", getattr(self.instance, "group_invite_link", ""))

        if registration_start and registration_end and registration_start > registration_end:
            raise serializers.ValidationError("Registration start must be before registration end.")
        if trip_start and trip_end and trip_start > trip_end:
            raise serializers.ValidationError("Trip start must be before trip end.")
        if registration_end and trip_start and registration_end > trip_start:
            raise serializers.ValidationError("Registration must end before trip starts.")

        group_chat_id = (group_chat_id or "").strip()
        if group_chat_id:
            try:
                int(group_chat_id)
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    {"group_chat_id": "Group chat ID must be a numeric identifier like -1001234567890."}
                )
        group_invite_link = (group_invite_link or "").strip()
        if group_invite_link and not group_invite_link.startswith("http"):
            raise serializers.ValidationError({"group_invite_link": "Invite link must be a valid URL."})
        return attrs


class TripListSerializer(TripSerializer):
    class Meta(TripSerializer.Meta):
        fields = [
            "id",
            "title",
            "place",
            "place_detail",
            "trip_start",
            "trip_end",
            "registration_start",
            "registration_end",
            "default_price",
            "max_capacity",
            "status",
            "participants_count",
            "is_registration_open",
        ]


class UserTripSerializer(serializers.ModelSerializer):
    traveler_detail = TravelerSerializer(source="traveler", read_only=True)
    trip_detail = TripSerializer(source="trip", read_only=True)

    class Meta:
        model = models.UserTrip
        fields = [
            "id",
            "trip",
            "trip_detail",
            "traveler",
            "traveler_detail",
            "status",
            "payment_status",
            "quoted_price",
            "paid_amount",
            "payment_note",
            "payment_proof",
            "payment_proof_uploaded_at",
            "custom_bonus_message",
            "admin_comment",
            "confirmed_by",
            "confirmed_at",
            "group_joined_at",
            "group_join_error",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "payment_proof_uploaded_at",
            "confirmed_by",
            "confirmed_at",
            "group_joined_at",
            "group_join_error",
            "created_at",
            "updated_at",
        ]

    def _set_payment_proof_timestamp(self, instance, validated_data):
        if validated_data.get("payment_proof"):
            validated_data["payment_proof_uploaded_at"] = timezone.now()

    def create(self, validated_data):
        self._set_payment_proof_timestamp(None, validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        request = self.context.get("request")
        if "paid_amount" in validated_data and validated_data["paid_amount"] < Decimal("0.00"):
            raise serializers.ValidationError({"paid_amount": "Cannot be negative."})

        self._set_payment_proof_timestamp(instance, validated_data)
        if request and request.user.is_authenticated:
            if "payment_status" in validated_data and validated_data["payment_status"] == models.UserTrip.PAYMENT_CONFIRMED:
                validated_data["confirmed_by"] = request.user
                validated_data["confirmed_at"] = timezone.now()
        return super().update(instance, validated_data)


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Expense
        fields = [
            "id",
            "trip",
            "amount",
            "category",
            "description",
            "incurred_at",
            "recorded_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["recorded_by", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["recorded_by"] = request.user
        return super().create(validated_data)


class TripAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TripAnnouncement
        fields = [
            "id",
            "trip",
            "message",
            "sent_by",
            "sent_at",
            "delivered",
            "delivered_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["sent_by", "sent_at", "delivered_at", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["sent_by"] = request.user
        return super().create(validated_data)
