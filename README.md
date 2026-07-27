# Expense Tracker API

A multi-user expense and budget tracking REST API built with FastAPI. Users can sign up, log in, organize spending into custom categories, log expenses, set monthly budgets per category, and get spending summaries and budget-vs-actual reports.

## Features

- **Authentication** — JWT-based signup/login, passwords hashed with bcrypt, protected routes via OAuth2 bearer tokens
- **Categories** — user-scoped, custom expense categories
- **Expenses** — full CRUD, filterable by category and date range, with pagination
- **Budgets** — set a monthly budget per category, compare budgeted vs. actual spend
- **Reporting** — monthly spend summary by category, and a budget balance report (budgeted / spent / remaining)
- **Validation** — request-level validation via Pydantic (e.g. amounts must be positive, dates can't be in the future)
- **Ownership enforcement** — every resource is scoped to its owner; users can only read or modify their own data

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy** — ORM, backed by SQLite
- **Pydantic** — request/response validation
- **python-jose** — JWT creation and verification
- **passlib (bcrypt)** — password hashing
- **python-dotenv** — environment-based configuration

## Project Structure

```
.
├── main.py                  # App entrypoint, wires up routers
├── date_ranges.py           # Helper for resolving a month name to a date range
├── authentication/
│   └── auth.py               # Password hashing, JWT creation/verification, get_current_user
├── database/
│   ├── database.py           # Engine, session, get_db dependency
│   └── models.py              # SQLAlchemy models: User, Expense, Category, Budget
└── router/
    ├── users.py               # /signup, /login
    ├── categories.py          # /category
    ├── expenses.py            # /expenses, /expenses/summary
    └── budgets.py             # /budgets, /budgets/status
```

## Setup

1. **Clone the repo and enter the folder**
   ```bash
   git clone https://github.com/gowtham777y/Expense-Tracker.git
   cd Expense-Tracker
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file inside `authentication/`:
   ```
   SECRET_KEY=your-random-secret-key-here
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   ```

5. **Run the server**
   ```bash
   uvicorn main:app --reload
   ```

6. **Explore the API**

   Open `http://127.0.0.1:8000/docs` for interactive Swagger docs — every endpoint can be tested directly from there, including authorizing with a token via the "Authorize" button.

## API Overview

| Method | Endpoint             | Description                                  | Auth required |
|--------|-----------------------|-----------------------------------------------|----------------|
| POST   | `/signup`             | Create a new user                             | No             |
| POST   | `/login`              | Log in, get an access token                   | No             |
| GET    | `/category`           | List the current user's categories            | Yes            |
| POST   | `/category`           | Create a new category                         | Yes            |
| POST   | `/expenses`           | Log a new expense                             | Yes            |
| GET    | `/expenses`           | List expenses (filter by category/date, paginated) | Yes       |
| PUT    | `/expenses`           | Update an expense                             | Yes            |
| DELETE | `/expenses`           | Delete an expense                             | Yes            |
| GET    | `/expenses/summary`   | Total spend per category for a given month    | Yes            |
| POST   | `/budgets`             | Set a budget for a category/month             | Yes            |
| GET    | `/budgets`             | List budgets for a given month                | Yes            |
| PUT    | `/budgets`             | Update a budget                               | Yes            |
| DELETE | `/budgets`             | Delete a budget                               | Yes            |
| GET    | `/budgets/status`      | Budget vs. actual spend for a given month     | Yes            |

## Example Usage

```bash
# Sign up
curl -X POST http://127.0.0.1:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"name": "Jane", "age": 28, "email": "jane@example.com", "password": "secret123"}'

# Log in
curl -X POST http://127.0.0.1:8000/login \
  -d "username=jane@example.com&password=secret123"

# Create a category (use the access_token from login)
curl -X POST http://127.0.0.1:8000/category \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Food"}'

# Log an expense
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Lunch", "category": "Food", "description": "Team lunch", "expense_date": "2026-07-15", "amount": 250}'
```

## Notes

- Data is stored in a local SQLite file (`app.db`), created automatically on first run.
- This project focuses on core backend fundamentals: authentication, ownership-scoped data, filtering/pagination, and SQL aggregation — deliberately kept to SQLite rather than a hosted database for simplicity.

## Possible Future Improvements

- Refresh tokens for longer sessions without re-login
- Automated tests with pytest
- Deployment with a hosted Postgres database
- Recurring expenses
