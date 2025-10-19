# LocTur Manager API Reference

Base URL: `/api/`
Authentication:
- Staff users: session or token auth (DRF token).
- Telegram bots: send `X-Bot-Token: <token>` header from `core.BotToken`.

Pagination: default page size 20 (DRF page number pagination). Responses return `{ count, next, previous, results }` for list endpoints.

## Travelers

### `GET /travelers/`
List travelers. Supports `search` (first/last name, phone, handle) and `telegram_id` filters.

### `POST /travelers/`
Create traveler (bot-friendly).

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+77001112233",
  "telegram_handle": "@jdoe",
  "telegram_id": "12345",
  "extra_info": "second phone..."
}
```

### `PATCH /travelers/{id}/`
Update details (staff or bot token that created the entry).

## Places

| Endpoint | Methods | Notes |
| --- | --- | --- |
| `/places/` | GET, POST | Admin CRUD; GET supports search. |
| `/places/{id}/` | GET, PATCH, DELETE | Delete cascades related photos. |
| `/place-photos/` | POST, DELETE | Upload images (multipart) with `place` UUID. |

## Trips

### `GET /trips/`
Query params: `status`, `place`, `start_date`, `end_date`, `search`, `ordering`.

### `POST /trips/`
Create trip.

```json
{
  "place": "<uuid>",
  "title": "Weekend in Almaty",
  "description": "...",
  "registration_start": "2024-04-01",
  "registration_end": "2024-04-10",
  "trip_start": "2024-04-15",
  "trip_end": "2024-04-18",
  "default_price": "45000.00",
  "max_capacity": 15,
  "status": "registration",
  "bonus_message": "Bring a friend and get 10% off"
}
```

### `PATCH /trips/{id}/`
Update status, description, pricing, etc.

### `DELETE /trips/{id}/`
Soft delete not implemented – removing trip deletes related registrations.

### `GET /trips/{id}/participants/`
Lists `UserTrip` objects for the trip. Each entry includes traveler info, payment status, amounts, proof URL, and admin comments.

### `POST /trips/{id}/toggle-announcement/`
Flips `announce_in_channel` boolean; can be polled by bot workers to decide whether to broadcast.

## User Trips (registrations)

### `GET /user-trips/`
Filters: `status`, `payment_status`, `trip`, `traveler`, `ordering`.

### `POST /user-trips/`
Used by bots when a traveler joins a trip.

```json
{
  "trip": "<trip_uuid>",
  "traveler": "<traveler_uuid>",
  "quoted_price": "45000.00",
  "paid_amount": "0.00",
  "payment_note": "Will pay tonight",
  "custom_bonus_message": "Early bird"
}
```

Uploading proof: send multipart PATCH to `/user-trips/{id}/` with `payment_proof` file.

### `PATCH /user-trips/{id}/`
Admin confirms payment, adjusts `paid_amount`, sets `payment_status`, and optionally `status`.

## Expenses

CRUD endpoints for trip expenses. Required fields: `trip`, `amount`, `category`, `incurred_at`.

## Metrics

### `GET /metrics/overview/?range=30d`
Returns aggregated stats:

```json
{
  "range_days": 30,
  "income_total": "120000.00",
  "expenses_total": "45000.00",
  "net": "75000.00",
  "outstanding_total": "20000.00",
  "active_registrations": [
    { "id": "...", "title": "Weekend in Almaty", "signups": 8, "default_price": "45000.00" }
  ]
}
```

## Bot Tokens

`/bot-tokens/` endpoints let staff provision API keys for Telegram bots. The token string is stored as-is; rotate regularly and mark `is_active=false` when revoking.
