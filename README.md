# LocTur Manager

LocTur Manager is a full-stack solution that helps trip organizers keep track of travelers, registrations, manual payments, and trip finances. The project includes:

- **Django REST backend (`backend/`)** – exposes RESTful APIs for admin UI, Telegram bots, and automations.
- **React admin frontend (`admin-frontend/`)** – provides dashboards and CRUD tools for organizers.
- **PostgreSQL database** – stores trips, travelers, expenses, and registration data.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or use Docker Compose)

### Clone & bootstrap

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install frontend dependencies
cd admin-frontend
npm install
```

### Environment configuration

Copy the example environment file and adjust as needed:

```bash
cp backend/.env.example backend/.env
```

Important variables:

- `DJANGO_SECRET_KEY`: random string for signing.
- `DATABASE_URL`: PostgreSQL connection string (`postgresql://user:pass@host:5432/dbname`).
- `CORS_ALLOWED_ORIGINS`: URLs allowed to call the API (e.g., `http://localhost:5173`).
- `CSRF_TRUSTED_ORIGINS`: Hosts permitted for CSRF-protected requests.

### Database setup

Apply migrations and create a superuser:

```bash
cd backend
python manage.py migrate
python manage.py createsuperuser
```

### Development servers

Backend API (http://localhost:8000):

```bash
cd backend
python manage.py runserver 0.0.0.0:8000
```

Frontend app (http://localhost:5173):

```bash
cd admin-frontend
npm run dev
```

Log in to Django admin (`/admin/`) to manage staff users, bot tokens, and data seed.

---

## Docker Compose

A convenience stack is provided for PostgreSQL, the Django backend, and the built frontend.

```bash
docker compose up --build
```

- Backend available at http://localhost:8000
- Frontend static build served at http://localhost:5173
- PostgreSQL exposed on port 5432 (`loctur`/`loctur` credentials)

Media uploads are persisted in the `backend_media` Docker volume.

---

## Backend Overview

### Tech stack

- Django 4.2, Django REST Framework, PostgreSQL
- Token-based auth for staff + custom bot token authentication (`X-Bot-Token` header)
- File storage on local filesystem (`MEDIA_ROOT`).

### Core models

- `Traveler`: Telegram-sourced traveler profile.
- `Place` & `PlacePhoto`: reusable catalog of destinations.
- `Trip`: trip definition with registration window, status, pricing, and bonus message.
- `UserTrip`: traveler registration with manual payment tracking.
- `Expense`: trip expenses for spending analytics.
- `BotToken`: API keys for Telegram bots.
- `TripAnnouncement`: audit trail for broadcast requests.

### Key endpoints

| Endpoint | Method(s) | Description |
| --- | --- | --- |
| `/api/travelers/` | GET, POST, PATCH | Manage traveler profiles (bots can POST via `X-Bot-Token`). |
| `/api/places/` | GET, POST, PATCH, DELETE | CRUD for places and metadata. |
| `/api/trips/` | GET, POST, PATCH, DELETE | Manage trips, pricing, capacity, status. |
| `/api/trips/{id}/participants/` | GET | Participant list with payment status. |
| `/api/user-trips/` | GET, POST, PATCH | Registration requests & payment confirmation. |
| `/api/expenses/` | GET, POST, PATCH, DELETE | Track trip expenses. |
| `/api/metrics/overview/?range=30d` | GET | Dashboard metrics (income, expense, net, outstanding). |
| `/api/trips/{id}/toggle-announcement/` | POST | Toggles auto-announcement flag. |
| `/api/bot-tokens/` | CRUD | Maintain Telegram bot API tokens. |

All write operations require staff users except where bots are explicitly allowed (traveler creation and user trip submissions).

### Bot integration hints

- Register Telegram users via `/api/travelers/` by sending `X-Bot-Token` in headers.
- Create trip join requests by POSTing to `/api/user-trips/` with `trip`, `traveler`, `quoted_price`, `paid_amount` (initially zero) and optional `payment_proof` upload.
- Payment proofs can be uploaded using multipart form data to `/api/user-trips/{id}/`.
- Trips can now store `group_chat_id` (Telegram chat id) and `group_invite_link` so bots know where to onboard confirmed travelers.

### Telegram bot service

- Configure environment variables in `backend/.env` (see `.env.example`) including `TELEGRAM_BOT_TOKEN`, `BACKEND_BOT_TOKEN`, and `BACKEND_API_BASE_URL`.
- Create an active bot token record in Django admin (`BotToken` model) and paste its value into `BACKEND_BOT_TOKEN`.
- Ensure each trip has its `group_chat_id` set to the target Telegram group where the bot has admin rights.
- Run the bot with `python -m telegram_bot.bot` (inside the `backend/` directory or project root with the virtualenv activated).
- The bot guides travelers through registration, uploads payment proofs, and notifies confirmed travelers with an invite link that triggers automatic approval once they request to join the group.

---

## Admin Frontend Overview

- Built with React + Ant Design, uses Vite dev server.
- Core pages: Dashboard, Trips list & detail, Places catalog, Travelers, Expenses, Settings.
- API client wraps Axios with `withCredentials` enabled; adjust proxy (`vite.config.js`) if backend served elsewhere.
- Payment management dialog streamlines confirming manual payments and logging admin comments.

### Running tests & linting

- Backend: `cd backend && python manage.py test`
- Frontend lint: `cd admin-frontend && npm run lint`

---

## Project Structure

```
.
├── backend/                # Django project
│   ├── config/             # settings, urls, asgi
│   ├── core/               # domain models, serializers, views
│   ├── manage.py
│   └── requirements.txt
├── admin-frontend/         # React admin console
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
└── README.md
```

---

## Next Steps

- Implement Telegram bot services consuming the exposed APIs.
- Expand automated test coverage (API integration tests, React component tests).
- Add role-based permissions and audit logs if multiple admins require granular access.
- Configure production-grade storage (S3) for media files when deploying beyond local filesystem.
