TechDesk (Mini IT Helpdesk)

Локальний REST-сервіс обліку технічних звернень на базі FastAPI та SQLite.

Вимоги: Python 3.10+

Встановлення (Windows PowerShell):
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt

Запуск сервісу:
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1
Документація API (Swagger UI): http://127.0.0.1:8000/docs

Запуск тестів і лінтера:
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check app tests --select E4,E7,E9,F,I

Приклад створення тікета:
POST http://127.0.0.1:8000/tickets
Body: {"title": "Не працює VPN", "priority": "high", "assignee_id": 1}

Навчальні обмеження:
- Два наперед визначені користувачі (1 - Agent A, 2 - Agent B) без автентифікації.
- Локальний запуск без Docker і хмарного розгортання; FR-08 (AI-рекомендація) реалізується у ЛР4.
- Робоча БД зберігається у data/app.db (виключена з Git); тести використовують ізольовану tmp_path БД.