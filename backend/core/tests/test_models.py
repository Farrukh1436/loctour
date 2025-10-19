"""Model level tests for core app."""
from __future__ import annotations

from decimal import Decimal
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from core import models


class TripAggregationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(username="admin")
        self.place = models.Place.objects.create(name="Test Place")
        self.trip = models.Trip.objects.create(
            place=self.place,
            title="Trip A",
            description="desc",
            registration_start=date(2024, 1, 1),
            registration_end=date(2024, 1, 10),
            trip_start=date(2024, 1, 15),
            trip_end=date(2024, 1, 20),
            default_price=Decimal("100.00"),
            max_capacity=10,
        )
        self.traveler = models.Traveler.objects.create(
            first_name="John",
            last_name="Doe",
            phone_number="+123456789",
            telegram_id="12345",
        )

    def test_trip_income_and_participants(self):
        models.UserTrip.objects.create(
            trip=self.trip,
            traveler=self.traveler,
            status=models.UserTrip.STATUS_CONFIRMED,
            payment_status=models.UserTrip.PAYMENT_CONFIRMED,
            quoted_price=Decimal("100.00"),
            paid_amount=Decimal("100.00"),
        )

        self.assertEqual(self.trip.participants_count(), 1)
        self.assertEqual(self.trip.total_income(), Decimal("100.00"))

    def test_trip_expenses_sum(self):
        models.Expense.objects.create(
            trip=self.trip,
            amount=Decimal("40.50"),
            category="transport",
            description="bus",
            incurred_at=date(2024, 1, 12),
            recorded_by=self.user,
        )
        models.Expense.objects.create(
            trip=self.trip,
            amount=Decimal("10.00"),
            category="food",
            description="snacks",
            incurred_at=date(2024, 1, 13),
            recorded_by=self.user,
        )
        self.assertEqual(self.trip.total_expenses(), Decimal("50.50"))
