"""Filter sets for API endpoints."""
from __future__ import annotations

import django_filters

from . import models


class TripFilter(django_filters.FilterSet):
    start_date = django_filters.DateFilter(field_name="trip_start", lookup_expr="gte")
    end_date = django_filters.DateFilter(field_name="trip_end", lookup_expr="lte")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    place = django_filters.UUIDFilter(field_name="place_id")

    class Meta:
        model = models.Trip
        fields = ["status", "place", "start_date", "end_date"]


class UserTripFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(lookup_expr="iexact")
    payment_status = django_filters.CharFilter(lookup_expr="iexact")
    trip = django_filters.UUIDFilter(field_name="trip_id")
    traveler = django_filters.UUIDFilter(field_name="traveler_id")
    group_joined = django_filters.BooleanFilter(method="filter_group_joined")

    class Meta:
        model = models.UserTrip
        fields = ["status", "payment_status", "trip", "traveler", "group_joined"]

    def filter_group_joined(self, queryset, name, value):
        if value:
            return queryset.filter(group_joined_at__isnull=False)
        return queryset.filter(group_joined_at__isnull=True)


class ExpenseFilter(django_filters.FilterSet):
    trip = django_filters.UUIDFilter(field_name="trip_id")
    category = django_filters.CharFilter(lookup_expr="iexact")
    date_from = django_filters.DateFilter(field_name="incurred_at", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="incurred_at", lookup_expr="lte")

    class Meta:
        model = models.Expense
        fields = ["trip", "category", "date_from", "date_to"]
