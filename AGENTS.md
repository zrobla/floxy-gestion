# Repository Guidelines

## Project Structure & Module Organization
This is a Django project. The project root contains `manage.py`, `pyproject.toml`, and `requirements.txt`. The main Django settings live in `floxy/`. Each business domain is a Django app at the top level (examples: `accounts/`, `crm/`, `operations/`, `wigs/`, `inventory/`, `tasks/`, `content/`, `integrations/`, `reporting/`). Shared templates are in `templates/`, static assets are in `static/`, and collected assets in `staticfiles/`. Local data uses SQLite by default (`db.sqlite3`).

## Build, Test, and Development Commands
Typical local setup:
```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Optional seeds:
```bash
python manage.py seed_initial_users
python manage.py seed_social_tasks
python manage.py seed_content_examples
```
Docker workflow:
```bash
docker compose up --build
docker compose exec web python manage.py migrate
```
Quality tools:
```bash
ruff check .
black .
```

## Coding Style & Naming Conventions
- Python 3.11, 4-space indentation.
- Format with Black (line length 88). Lint with Ruff (`E`, `F`, `I` rules; `E501` ignored).
- Keep code identifiers in English; UI copy is in French.
- Follow Django conventions: `snake_case` for modules/functions, `CamelCase` for classes, and app names as simple lowercase nouns.

## Testing Guidelines
Tests run with either Django or pytest:
```bash
python manage.py test
pytest
```
Pytest is configured with `DJANGO_SETTINGS_MODULE=floxy.settings`. Test files follow `tests.py`, `test_*.py`, or `*_tests.py`. There is no stated coverage gate, so add focused tests for new models, views, and API endpoints.

## Commit & Pull Request Guidelines
No git history is available in this checkout, so commit conventions cannot be inferred. Prefer short, imperative commit subjects (optionally include a scope), and keep commits focused.
PRs should include:
- A brief description of the change and rationale.
- Linked issues or tickets if applicable.
- Screenshots for UI changes (dashboard, activities, tasks, content, etc.).
- Notes on migrations, seeds, or configuration changes.

## Configuration & Secrets
Copy `.env.example` to `.env` and set values such as `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, and `SQLITE_PATH`. Avoid committing secrets and document any new environment variables.
