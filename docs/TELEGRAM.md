# Telegram Bot Integration

## Bot Tokens

1. Create a bot via BotFather.
2. In Django admin > Bot tokens, create a new entry and paste a secure random token (64+ chars). Keep this token private.
3. Configure your bot application to include the header `X-Bot-Token: <token>` for every API request.

## Registration Flow Outline

1. **/start** – greet user, request contact share, collect first/last name, optional additional info.
2. POST traveler to `/api/travelers/`.
3. Fetch open trips: `GET /api/trips/?status=registration`. For deep links, parse `/start trip_<uuid>` arguments to load a specific trip.
4. When user confirms join:
   - POST `/api/user-trips/` with `trip`, `traveler`, `quoted_price`, `payment_note`.
   - Respond with payment instructions (pull from admin Settings page or store in bot config).
5. User uploads payment proof → send multipart PATCH to `/api/user-trips/{id}/` with `payment_proof` and optional comment.
6. Poll `/api/user-trips/?payment_status=confirmed&traveler=<uuid>` to show history.

## Admin Broadcast Bot

- Poll `/api/trips/?status=registration&announce_in_channel=true` for eligible trips.
- Compose broadcast message using `trip.custom_announcement_text` fallback to default template.
- Send to Telegram channel with inline `Register` button linking to `https://t.me/<botname>?start=trip_<uuid>`.
- Optionally POST `/api/announcements/` to log messages.

## Error Handling

- 401 Unauthorized → invalid or missing bot token.
- 400 Bad Request → validation error (duplicate registration, invalid price, etc.).
- 409 Conflict (future enhancement) could be returned if capacity exceeded (implement check before confirming).

## Rate Limiting

Rest API currently relies on infrastructure-level rate limiting (reverse proxy or API gateway). Apply Telegram recommended rate-limits (no more than 30 messages per second) when broadcasting.
