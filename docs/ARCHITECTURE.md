# Architecture & Flows

## Core Components

| Component | Responsibility |
| --- | --- |
| Django backend | REST APIs, persistence, business rules, payment tracking |
| PostgreSQL | Primary relational datastore |
| React admin UI | Operational dashboard and CRUD tooling for organizers |
| Telegram bots (external) | Traveler onboarding, trip registration, notifications |

```
Telegram Bot  -->  Django API  <--  React Admin
      |                |                 |
      |                |                 |
  PostgreSQL <----- Business logic ----> Filesystem storage
```

## Data Model Highlights

- **Traveler** objects are immutable identifiers for Telegram users (unique `telegram_id`).
- **Trip** controls registration windows, capacity, price, and optional bonus message text displayed to travelers.
- **UserTrip** captures each registration, payment amount, proof file, and admin confirmation metadata.
- **Expense** records track spending categories per trip to surface net revenue.

## Telegram Bot Lifecycle

1. User starts bot → bot sends `/api/travelers/` POST with contact info.
2. Bot lists open trips via `/api/trips/?status=registration`.
3. User chooses trip → bot POSTs `/api/user-trips/` with quoted price and note.
4. Bot instructs manual payment and collects screenshot; uploads via multipart PATCH to `/api/user-trips/{id}/`.
5. Background worker polls `/api/user-trips/?payment_status=pending` for reminders.

## Admin Workflow

1. Admin panel dashboard shows financial KPIs via `/api/metrics/overview/`.
2. Trip table lists all trips; creation modal reuses places and sets registration windows.
3. Trip detail page fetches `/api/trips/{id}/` and participants to approve payments.
4. Expense module logs spending for each trip.
5. When toggling announcements, admin triggers `/api/trips/{id}/toggle-announcement/`; bot service picks up `announce_in_channel=true` trips and broadcasts to channel.

## File Storage

Payment proofs and place photos are stored in `MEDIA_ROOT` (`backend/media/`). The backend exposes files at `/media/...` in development; configure a CDN or object store in production.

## Security & Permissions

- Staff users authenticate via Django sessions or DRF tokens; only staff can mutate core resources.
- Telegram bots authenticate with `core.BotToken` tokens passed in `X-Bot-Token` header; allowed to create travelers and registration requests.
- CSRF protection is active for session-authenticated requests; configure trusted origins in environment.

## Deployment Notes

- Run migrations on release: `python manage.py migrate`.
- Create staff superuser for admin site.
- Use `gunicorn` + reverse proxy (nginx) for backend.
- Serve frontend static build via CDN or nginx.
- Schedule regular backups for PostgreSQL and `media/` files.
