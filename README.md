# Personal Expense & Budget Management Web Application

## Overview
A web application where each user records income and expenses, organises them
into categories, and sets monthly budgets. All amounts are in Indian Rupees (₹).

## Aim
Learn Python full-stack development by building a real, well-structured Django
application step by step.

## Current milestone: 1 — Foundation and database models
Implemented: Django project config, `accounts` and `tracker` apps, models
(Category, Transaction, Budget), migration, admin registration, template/static
structure, and a placeholder home page.

Not implemented yet: login/registration UI, forms, CRUD, dashboard, REST API.

## Technology stack
Python 3.14 · Django 5.2 LTS · Django Templates · HTML/CSS/JavaScript ·
SQLite (development) → MySQL (final). Django REST Framework and Git/GitHub later.

## Project structure
```
expense_tracker/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── config/      # settings, root URLs, WSGI/ASGI
├── accounts/    # authentication foundation (built-in User)
├── tracker/     # models, admin, home view
├── templates/   # base.html, tracker/home.html
├── static/      # css/, js/
└── docs/        # architecture.md, database.md
```

## Database model overview
- **Category** — user, name, type (income/expense). Unique per user + name + type.
- **Transaction** — user, category, type, amount, date, description.
- **Budget** — user, optional category (empty = overall budget), amount, month (first day).

Details: `docs/database.md`.

## Setup (Windows, PowerShell or Command Prompt)
```
cd expense_tracker
py -3.14 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
Edit `.env` and set `DJANGO_SECRET_KEY`. Generate one with:
```
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

## Migrations
```
python manage.py makemigrations --check
python manage.py migrate
python manage.py createsuperuser
```
`makemigrations --check` confirms the included migration matches the models.
If it reports changes, delete `tracker/migrations/0001_initial.py` and run
`python manage.py makemigrations tracker`.

## Run the development server
```
python manage.py runserver
```
Open http://127.0.0.1:8000/ (home page) and http://127.0.0.1:8000/admin/.

## Next milestone
Authentication UI (register, login, logout) and Category CRUD, with forms that
validate ownership and type rules, plus first automated tests.
