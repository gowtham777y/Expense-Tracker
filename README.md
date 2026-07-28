# Expense Tracker API

A multi-user expense and budget tracking REST API — originally built as a monolith with FastAPI, and since split into independent microservices to practice service-to-service authentication, ownership boundaries, and distributed system design. Users can sign up, log in, organize spending into custom categories, log expenses, set monthly budgets per category, and get spending summaries and budget-vs-actual reports.

## Architecture

This project is split into two independent services, each with its own codebase, database, and process:

- **`auth-service`** (port `8001`) — owns user identity. Handles signup, login, password hashing, and JWT issuance.
- **`expense-service`** (port `8002`) — owns expenses, categories, and budgets. Has no knowledge of user records — it independently verifies JWTs issued by `auth-service` using a shared signing secret, and trusts the `user_id` embedded in the token payload.

There is **no shared database** between the two services and **no synchronous service-to-service call** on the request path — `expense-service` never calls `auth-service` to validate a request. Trust is established entirely through the JWT's signature, which both services can verify independently since they share the same `SECRET_KEY`.

```
┌────────────────┐         JWT (signed)         ┌──────────────────┐
│  auth-service    │ ──────────────────────────▶ │  expense-service   │
│  :8001            │                              │  :8002              │
│  - signup/login   │                              │  - expenses          │
│  - users.db        │                              │  - categories         │
│                    │                              │  - budgets             │
│                    │                              │  - expense_service.db   │
└────────────────┘                              └──────────────────┘
```

## Features

- **Authentication** (auth-service) — JWT-based signup/login, passwords hashed with bcrypt
- **Categories, Expenses, Budgets** (expense-service) — full CRUD, all scoped to the requesting user via the JWT's embedded `user_id`
- **Filtering & pagination** on expenses (by category, date range)
- **Reporting** — monthly spend summary by category, and a budget-vs-actual balance report
- **Validation** — request-level validation via Pydantic (e.g. amounts must be positive, dates can't be in the future)
- **Cross-service auth** — expense-service independently verifies tokens it never issued, using a shared JWT signing secret — no session store, no auth service round-trip per request

## Tech Stack

- **FastAPI** — web framework (one instance per service)
- **SQLAlchemy** — ORM, backed by SQLite (one database per service)
- **Pydantic** — request/response validation
- **python-jose** — JWT creation (auth-service) and verification (both services)
- **passlib (bcrypt)** — password hashing (auth-service only)
- **python-dotenv** — environment-based configuration, per service

## Project Structure

```
.
├── auth-service/
│   ├── main.py
│   ├── database/
│   │   ├── database.py       # engine, session, get_db
│   │   └── models.py          # UserModel
│   ├── router/
│   │   └── users.py            # /signup, /login
│   └── auth/
│       └── auth.py              # password hashing, JWT creation, SECRET_KEY, ALGORITHM
│
└── expense-service/
    ├── main.py
    ├── database/
    │   ├── database.py       # engine, session, get_db (separate DB file)
    │   └── models.py          # ExpenseModel, CategoryModel, BudgetModel — no UserModel
    ├── router/
    │   ├── expenses.py         # /expenses, /expenses/summary
    │   ├── categories.py       # /category
    │   └── budgets.py           # /budgets, /budgets/status
    └── auth/
        └── auth.py              # JWT verification only — no hashing, no token creation
```

## Setup

Each service is run independently, in its own terminal, with its own virtual environment.

### 1. Clone the repo

```bash
git clone https://github.com/gowtham777y/Expense-Tracker.git
cd Expense-Tracker
```

### 2. Set up `auth-service`

```bash
cd auth-service
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file inside `auth-service/`:
```
SECRET_KEY=your-random-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=15
```

Run it:
```bash
uvicorn main:app --port 8001 --reload
```

### 3. Set up `expense-service`

In a **separate terminal**:

```bash
cd expense-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file inside `expense-service/` — **`SECRET_KEY` must match `auth-service`'s exactly**, or token verification will fail:
```
SECRET_KEY=your-random-secret-key-here
```

Run it:
```bash
uvicorn main:app --port 8002 --reload
```

### 4. Both services must be running at the same time

- `auth-service` → `http://127.0.0.1:8001/docs`
- `expense-service` → `http://127.0.0.1:8002/docs`

Get a token from `auth-service`'s `/login`, then use it to authorize on `expense-service`'s `/docs` — it will verify the token independently without calling back to `auth-service`.

## API Overview

**auth-service** (`:8001`)

| Method | Endpoint  | Description                | Auth required |
|--------|-----------|------------------------------|----------------|
| POST   | `/signup` | Create a new user           | No             |
| POST   | `/login`  | Log in, get an access token | No             |

**expense-service** (`:8002`)

| Method | Endpoint             | Description                                        | Auth required |
|--------|-----------------------|-------------------------------------------------------|----------------|
| GET    | `/category`           | List the current user's categories                   | Yes            |
| POST   | `/category`           | Create a new category                                 | Yes            |
| POST   | `/expenses`           | Log a new expense                                     | Yes            |
| GET    | `/expenses`           | List expenses (filter by category/date, paginated)   | Yes            |
| PUT    | `/expenses`           | Update an expense                                     | Yes            |
| DELETE | `/expenses`           | Delete an expense                                     | Yes            |
| GET    | `/expenses/summary`   | Total spend per category for a given month            | Yes            |
| POST   | `/budgets`             | Set a budget for a category/month                     | Yes            |
| GET    | `/budgets`             | List budgets for a given month                        | Yes            |
| PUT    | `/budgets`             | Update a budget                                        | Yes            |
| DELETE | `/budgets`             | Delete a budget                                        | Yes            |
| GET    | `/budgets/status`      | Budget vs. actual spend for a given month              | Yes            |

## Example Usage

```bash
# Sign up (auth-service, :8001)
curl -X POST http://127.0.0.1:8001/signup \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane", "age": 28, "email": "jane@example.com", "password": "secret123"}'

# Log in (auth-service, :8001)
curl -X POST http://127.0.0.1:8001/login \
  -d "username=jane@example.com&password=secret123"

# Create a category (expense-service, :8002 — use the access_token from login)
curl -X POST http://127.0.0.1:8002/category \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Food"}'

# Log an expense (expense-service, :8002)
curl -X POST http://127.0.0.1:8002/expenses \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Lunch", "category": "Food", "description": "Team lunch", "expense_date": "2026-07-15", "amount": 250}'
```

## Notes

- Each service has its own SQLite database file, created automatically on first run — there is deliberately no shared database.
- Since services can't share foreign keys across databases, `expense-service` stores `user_id` as a plain integer column (no `ForeignKey`, no SQLAlchemy `relationship()`) — referential integrity between `users` and `expenses` is enforced by application logic and the JWT payload, not by the database.
- CORS is enabled on `auth-service` to allow Swagger UI on `expense-service`'s `/docs` to call its `/login` endpoint during local testing.

## Possible Future Improvements

- Introduce a message broker (e.g. RabbitMQ/Kafka) for async, event-driven communication between services — e.g. a `user.deleted` event that `expense-service` listens for, instead of relying purely on convention
- API Gateway in front of both services, instead of calling each by its own port directly
- Refresh tokens for longer sessions without re-login
- Automated tests with pytest, per service
- Deployment with a hosted Postgres database (one per service) and containerization (Docker) for each service
- Recurring expenses
