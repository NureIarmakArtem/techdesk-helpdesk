Зрізи TechDesk (Mini IT Helpdesk)

A. Створення й читання
Код (app/): schemas.py, services.py, routes.py, database.py
Тести (tests/): conftest.py, test_tickets.py
Читати: docs/api-contract.md (GET /health, GET /users, POST /tickets, GET /tickets, GET /tickets/{id})
Критерії: docs/requirements.md (US-01, US-02, US-07; AC-01-01..02, AC-02-03, AC-07-01..03)
Сценарії: T01, T02, T03, T13

B. Зміни й стани
Код (app/): schemas.py, services.py, routes.py
Тести (tests/): test_tickets.py
Читати: docs/api-contract.md (PATCH /tickets/{id}, PATCH /tickets/{id}/status); docs/requirements.md (розд. 5.2, 5.3)
Критерії: docs/requirements.md (US-03, US-04, US-05; AC-03-01..03, AC-04-01..03, AC-05-01..02)
Сценарії: T07, T08, T09, T10, T14

C. Коментарі
Код (app/): schemas.py, services.py, routes.py, database.py
Тести (tests/): test_comments.py
Читати: docs/api-contract.md (POST /tickets/{id}/comments, GET /tickets/{id}/comments)
Критерії: docs/requirements.md (US-06; AC-06-01..03)
Сценарії: T11, T12

D. Фільтри
Код (app/): services.py, routes.py
Тести (tests/): test_tickets.py
Читати: docs/api-contract.md (GET /tickets, параметри status і priority)
Критерії: docs/requirements.md (US-02; AC-02-01, AC-02-02)
Сценарії: T04, T05, T06