API-КОНТРАКТ - TechDesk (Mini IT Helpdesk)

Базовий URL: http://127.0.0.1:8000
Формат: application/json (UTF-8)
Усі правила валідації, матриця переходів 3x3 і правила PATCH описані в docs/requirements.md (розд. 5).

1. Політика HTTP-кодів помилок

| Код | Умова |
|-----|-------|
| 404 Not Found | Тікет із вказаним {id} не існує. |
| 409 Conflict | Редагування тікета CLOSED або заборонений перехід статусу (IN_PROGRESS -> OPEN, CLOSED -> OPEN, CLOSED -> IN_PROGRESS). |
| 422 Unprocessable Entity | Помилка валідації полів, невідомий assignee_id/author_id, null там де заборонено, порожнє тіло {} або зайве поле в PATCH, невалідний query-фільтр. |
| 503 Service Unavailable | Лише ЛР4: LLM-провайдер недоступний при виклику AI-рекомендації. |

2. Перелік маршрутів

| № | Метод і шлях | Призначення | Успіх | Помилки |
|---|--------------|-------------|-------|---------|
| 1 | GET /health | Перевірка запуску сервісу | 200 | - |
| 2 | GET /users | Список двох тестових користувачів | 200 | - |
| 3 | POST /tickets | Створення тікета (FR-01) | 201 | 422 |
| 4 | GET /tickets | Список тікетів; опціональні status і priority (AND) (FR-02) | 200 | 422 |
| 5 | GET /tickets/{id} | Один тікет за ID (FR-02) | 200 | 404, 422 |
| 6 | PATCH /tickets/{id} | Часткове оновлення title, description, priority, assignee_id (FR-03, FR-05) | 200 | 404, 409, 422 |
| 7 | PATCH /tickets/{id}/status | Зміна статусу за матрицею 3x3 (FR-04) | 200 | 404, 409, 422 |
| 8 | POST /tickets/{id}/comments | Додавання коментаря (FR-06) | 201 | 404, 422 |
| 9 | GET /tickets/{id}/comments | Коментарі тікета в порядку створення (FR-06) | 200 | 404, 422 |
| 10 | POST /tickets/{id}/ai-recommendation | Зарезервовано для ЛР4 (FR-08) | 200 | 404, 503 |

3. Опис операцій та приклади

3.1. GET /health
Відповідь 200:
{"status": "ok"}

3.2. GET /users
Відповідь 200:
[
  {"id": 1, "name": "Agent A"},
  {"id": 2, "name": "Agent B"}
]

3.3. POST /tickets
Body: title (обов'язково), description (опц.), priority (опц.), assignee_id (опц.).
Приклад запиту:
{
  "title": "  Не підключається корпоративний VPN  ",
  "description": "Під час входу видає помилку таймауту.",
  "priority": "high",
  "assignee_id": 1
}
Відповідь 201:
{
  "id": 1,
  "title": "Не підключається корпоративний VPN",
  "description": "Під час входу видає помилку таймауту.",
  "status": "OPEN",
  "priority": "high",
  "assignee_id": 1,
  "created_at": "2026-11-25T09:30:00Z"
}
Приклад помилки 422 (короткий title після trim):
{
  "detail": "title must contain between 3 and 120 characters after trimming"
}

3.4. GET /tickets
Query (опціонально): status (OPEN|IN_PROGRESS|CLOSED), priority (low|medium|high). Разом - логічне AND.
Приклад запиту: GET /tickets?status=OPEN&priority=high
Відповідь 200 (упорядковано за створенням; при відсутності збігів - []):
[
  {
    "id": 1,
    "title": "Не підключається корпоративний VPN",
    "description": "Під час входу видає помилку таймауту.",
    "status": "OPEN",
    "priority": "high",
    "assignee_id": 1,
    "created_at": "2026-11-25T09:30:00Z"
  }
]

3.5. GET /tickets/{id}
Path: id (integer).
Відповідь 200:
{
  "id": 1,
  "title": "Не підключається корпоративний VPN",
  "description": "Під час входу видає помилку таймауту.",
  "status": "OPEN",
  "priority": "high",
  "assignee_id": 1,
  "created_at": "2026-11-25T09:30:00Z"
}

3.6. PATCH /tickets/{id}
Body: 1..4 поля з {title, description, priority, assignee_id}. Правила в docs/requirements.md (п. 5.3).
Приклад запиту:
{
  "priority": "medium",
  "assignee_id": null
}
Відповідь 200:
{
  "id": 1,
  "title": "Не підключається корпоративний VPN",
  "description": "Під час входу видає помилку таймауту.",
  "status": "OPEN",
  "priority": "medium",
  "assignee_id": null,
  "created_at": "2026-11-25T09:30:00Z"
}

3.7. PATCH /tickets/{id}/status
Body: {"status": "OPEN" | "IN_PROGRESS" | "CLOSED"}. Правила в docs/requirements.md (п. 5.2).
Приклад запиту:
{
  "status": "IN_PROGRESS"
}
Відповідь 200:
{
  "id": 1,
  "title": "Не підключається корпоративний VPN",
  "description": "Під час входу видає помилку таймауту.",
  "status": "IN_PROGRESS",
  "priority": "medium",
  "assignee_id": null,
  "created_at": "2026-11-25T09:30:00Z"
}
Приклад помилки 409 (CLOSED -> OPEN):
{
  "detail": "Invalid status transition from CLOSED to OPEN"
}

3.8. POST /tickets/{id}/comments
Body: author_id (1 або 2), body (1..1000 символів після trim). Дозволено і для CLOSED.
Приклад запиту:
{
  "author_id": 2,
  "body": "Перезапустили VPN-шлюз, перевірте підключення."
}
Відповідь 201:
{
  "id": 10,
  "ticket_id": 1,
  "author_id": 2,
  "body": "Перезапустили VPN-шлюз, перевірте підключення.",
  "created_at": "2026-11-25T09:45:12Z"
}
Приклад помилки 422 (невідомий автор):
{
  "detail": "Unknown author_id: 99. Allowed values: 1, 2."
}

3.9. GET /tickets/{id}/comments
Відповідь 200 (в порядку створення або []):
[
  {
    "id": 10,
    "ticket_id": 1,
    "author_id": 2,
    "body": "Перезапустили VPN-шлюз, перевірте підключення.",
    "created_at": "2026-11-25T09:45:12Z"
  }
]

3.10. POST /tickets/{id}/ai-recommendation (ЛР4)
Відповідь 200:
{
  "ticket_id": 1,
  "suggested_category": "network",
  "suggested_priority": "high",
  "summary": "Збій підключення до корпоративного VPN через таймаут."
}