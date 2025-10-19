"""Ensure group onboarding fields exist in legacy databases."""
from __future__ import annotations

from django.db import migrations, models


def _get_column_names(connection, table_name: str) -> set[str]:
    with connection.cursor() as cursor:
        description = connection.introspection.get_table_description(cursor, table_name)
    return {col.name for col in description}


def _add_char_like_field(schema_editor, model, field_name: str, *, max_length: int, help_text: str = "") -> None:
    field_with_default = models.CharField(
        max_length=max_length,
        blank=True,
        default="",
        help_text=help_text,
    )
    field_with_default.set_attributes_from_name(field_name)
    schema_editor.add_field(model, field_with_default)

    field_without_default = models.CharField(
        max_length=max_length,
        blank=True,
        help_text=help_text,
    )
    field_without_default.set_attributes_from_name(field_name)
    schema_editor.alter_field(model, field_with_default, field_without_default, strict=False)


def _add_url_field(schema_editor, model, field_name: str, *, help_text: str = "") -> None:
    field_with_default = models.URLField(blank=True, default="", help_text=help_text)
    field_with_default.set_attributes_from_name(field_name)
    schema_editor.add_field(model, field_with_default)

    field_without_default = models.URLField(blank=True, help_text=help_text)
    field_without_default.set_attributes_from_name(field_name)
    schema_editor.alter_field(model, field_with_default, field_without_default, strict=False)


def _add_text_field(schema_editor, model, field_name: str, *, blank: bool = True) -> None:
    field_with_default = models.TextField(blank=blank, default="")
    field_with_default.set_attributes_from_name(field_name)
    schema_editor.add_field(model, field_with_default)

    field_without_default = models.TextField(blank=blank)
    field_without_default.set_attributes_from_name(field_name)
    schema_editor.alter_field(model, field_with_default, field_without_default, strict=False)


def add_missing_group_fields(apps, schema_editor) -> None:
    connection = schema_editor.connection

    Trip = apps.get_model("core", "Trip")
    trip_table = Trip._meta.db_table
    trip_columns = _get_column_names(connection, trip_table)

    if "group_chat_id" not in trip_columns:
        _add_char_like_field(
            schema_editor,
            Trip,
            "group_chat_id",
            max_length=128,
            help_text="Telegram chat identifier (e.g. -1001234567890) where confirmed travelers should be added.",
        )

    if "group_invite_link" not in trip_columns:
        _add_url_field(
            schema_editor,
            Trip,
            "group_invite_link",
            help_text="Optional static invite link shared with travelers after payment confirmation.",
        )

    UserTrip = apps.get_model("core", "UserTrip")
    user_trip_table = UserTrip._meta.db_table
    user_trip_columns = _get_column_names(connection, user_trip_table)

    if "group_joined_at" not in user_trip_columns:
        field = models.DateTimeField(blank=True, null=True)
        field.set_attributes_from_name("group_joined_at")
        schema_editor.add_field(UserTrip, field)

    if "group_join_error" not in user_trip_columns:
        _add_text_field(schema_editor, UserTrip, "group_join_error", blank=True)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_alter_place_rating_alter_usertrip_paid_amount"),
    ]

    operations = [
        migrations.RunPython(add_missing_group_fields, migrations.RunPython.noop),
    ]

