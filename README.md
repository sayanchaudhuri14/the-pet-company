# ThePetCompany

A pet grooming marketplace MVP. Customers discover and book groomers; groomers manage their profile and accept/reject bookings.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy, SQLite (PostgreSQL-ready) |
| Auth | JWT (python-jose) + bcrypt |
| Migrations | Alembic |
| Rate Limiting | slowapi |
| Logging | structlog (JSON) |
| Frontend | Plain HTML + JavaScript (no framework) |
| Tests | pytest, 77 tests |
| CI | GitHub Actions |
| Container | Docker |

---

## Project Structure

```
the-pet-company/
├── backend/
│   ├── app/
│   │   ├── core/          # config, dependencies, rate limiter, logging
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routes/        # API endpoints
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── services/      # auth helpers (JWT, bcrypt)
│   │   ├── database.py
│   │   └── main.py
│   ├── migrations/        # Alembic migration scripts
│   ├── tests/             # pytest test suite
│   ├── .env.example       # environment variable template
│   ├── Dockerfile
│   ├── alembic.ini
│   └── requirements.txt
└── frontend/
    └── index.html         # single-page app
```

---

## Running Locally

### 1. Clone the repo

```bash
git clone https://github.com/sayanchaudhuri14/the-pet-company.git
cd the-pet-company
```

### 2. Create and activate a virtual environment

```bash
cd backend
python -m venv venv

# Windows
source venv/Scripts/activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and set `SECRET_KEY` to a random 64-character hex string:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Paste the output as the value of `SECRET_KEY` in `.env`.

### 5. Apply database migrations

```bash
alembic upgrade head
```

### 6. Start the API server

```bash
uvicorn app.main:app --reload --port 8000
```

API is live at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

### 7. Open the frontend

Serve the frontend over HTTP (do **not** open `index.html` directly as a file):

```bash
cd ../frontend
python -m http.server 5500
```

Then open `http://127.0.0.1:5500` in your browser.

---

## Running with Docker

```bash
cd backend
docker build -t petcompany .
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=sqlite:///./petcompany.db \
  petcompany
```

---

## Running Tests

```bash
cd backend
pytest -v
```

All 77 tests use an isolated in-memory SQLite database — no setup needed.

---

## API Overview

### Public

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register/customer` | Register a customer account |
| POST | `/auth/register/groomer` | Register a groomer account |
| POST | `/auth/login` | Login, returns JWT token |
| GET | `/groomers` | List groomers (filterable) |
| GET | `/groomers/{id}` | Get a single groomer |

### Authenticated

| Method | Endpoint | Who | Description |
|---|---|---|---|
| GET | `/auth/me` | Any | Get current user info |
| PATCH | `/groomers/me` | Groomer | Update your profile |
| POST | `/bookings` | Customer | Create a booking |
| GET | `/bookings/mine` | Any | List your bookings |
| GET | `/bookings/{id}` | Any | Get a single booking |
| PATCH | `/bookings/{id}/status` | Groomer | Accept or reject a booking |

### Groomer filters

```
GET /groomers?pet_type=dog&max_price=800&min_experience=2&sort_by=price
```

| Param | Type | Description |
|---|---|---|
| `pet_type` | string | Filter by pet (e.g. `dog`, `cat`) |
| `max_price` | int ≥ 0 | Max price in ₹ |
| `min_experience` | int ≥ 0 | Minimum years of experience |
| `sort_by` | `price` or `experience` | Sort order |
| `skip` | int ≥ 0 | Pagination offset (default 0) |
| `limit` | 1–100 | Page size (default 20) |

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | Yes | — | JWT signing secret (min 32 chars) |
| `DATABASE_URL` | No | `sqlite:///./petcompany.db` | SQLAlchemy connection string |
| `ALLOWED_ORIGINS` | No | localhost ports | CORS whitelist (JSON array of URLs) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `30` | JWT lifetime |
| `ALGORITHM` | No | `HS256` | JWT algorithm |

---

## Git Branching Strategy

```
main        ← tagged releases only (v0.1.1, v0.2.0, ...)
develop     ← integration branch, always deployable
feature/*   ← one fix or feature per branch, cut from develop
release/*   ← release prep branches, merged to main + develop
```

---

## Security Hardening Applied

- `SECRET_KEY` required from environment — app refuses to start without it
- CORS restricted to configured origin whitelist
- Rate limiting: 10/min on login, 5/min on register
- SQL LIKE injection prevention on `pet_type` filter
- Passwords minimum 10 characters, bcrypt hashed
- JWT tokens expire after 30 minutes
- Account enumeration prevention — duplicate email returns generic 409
- Global exception handler — stack traces logged server-side only, never exposed to client
- Input validation: list length limits, non-negative prices, `price_max ≥ price_min`
- Booking validates pet type and service against groomer's actual offerings
- `SELECT FOR UPDATE` on booking status updates (race condition guard)
- XSS prevention on all dynamic frontend content
