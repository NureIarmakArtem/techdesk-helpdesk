ЗВІТ ІЗ ЛАБОРАТОРНОЇ РОБОТИ 2
Тема: Реалізація функціональності з AI-асистентом
Проєкт: TechDesk (Mini IT Helpdesk)
Виконавець: Ярмак Артем Миколайович

1. Реалізована функціональність (FR-01..FR-07)
Реалізовано всі 9 обов'язкових маршрутів з docs/api-contract.md:
- GET /health, GET /users
- POST /tickets, GET /tickets (з фільтрами status, priority та логічним AND), GET /tickets/{id}
- PATCH /tickets/{id} (часткове оновлення, атомарність, призначення/зняття виконавця)
- PATCH /tickets/{id}/status (матриця переходів 3x3)
- POST /tickets/{id}/comments, GET /tickets/{id}/comments
FR-08 не реалізовувався згідно з межами ЛР 2. Дані зберігаються у SQLite (data/app.db) і переживають перезапуск.

2. Результати перевірок (pytest та Ruff)
- pytest -q: 15 passed (усі сценарії T01-T14, перевірки health/users та предикатів пройдено успішно на ізольованій тимчасовій базі tmp_path; робоча БД data/app.db не зачіпається).
- ruff check app tests --select E4,E7,E9,F,I: All checks passed (0 попереджень після автовиправлення сортування імпортів у app/services.py).

3. Skill tracker-slice (Крок 0, використання та оновлення v0 -> v1)
Режим роботи: чат-асистент (Gemini Web) із ручним передаванням SKILL.md і потрібних розділів docs/; автоматичний вибір Skill і запуск тестів агентом у цьому режимі обмежені та виконувалися вручну студентом.

Результати перевірки опису Skill (Крок 0, 4 запити):
1. "Додай PATCH /tickets/{id}/status за матрицею станів" -> очікування: Skill спрацьовує -> факт: відповідає description.
2. "Тест T10 падає: CLOSED -> OPEN повертає 200" -> очікування: Skill спрацьовує -> факт: відповідає description.
3. "Онови README з командами запуску" -> очікування: Skill не спрацьовує -> факт: виключено в description.
4. "Поясни різницю між 409 та 422 у REST" -> очікування: Skill не спрацьовує -> факт: виключено в description.

AI-патч зі Skill (Зріз B):
Згенеровано первинний патч для PATCH /tickets/{id} і PATCH /tickets/{id}/status (тег lab02-ai-draft, commit 0a9fcd4). Перевірено вручну: параметризований SQL, заборона extra="forbid", розмежування відсутнього поля та null, атомарність валідації до запису в БД.

Оновлення Skill v0 -> v1:
У references/slices.md для зрізу B додано app/database.py до списку дозволених файлів (commit 337b8cc). Причина: під час реалізації зрізу B знадобилася функція update_ticket_fields у database.py, якої не було у початковому переліку v0.

4. Мікроексперимент (matches_status без AI vs matches_priority з AI)
Детальний протокол: docs/experiment-lr2.csv.
- matches_status (без AI): 6 хв, 3/3 тестів з першого разу, 0 правок.
- matches_priority (AI + Skill): 5 хв, 3/3 тестів з першого разу, 0 правок, 1 звернення.
Обмеження висновків: роботу виконував один учасник послідовно (на другому завданні вже був відомий точний шаблон), задачі мінімальні, тому статистичних висновків про перевагу AI робити не можна.

5. Посилання на артефакти та Git-версії
- .agents/skills/tracker-slice/SKILL.md, references/slices.md
- app/, tests/, README.md, requirements-lock.txt
- docs/experiment-lr2.csv, docs/ai-log.md, docs/traceability.csv
- lab02-skill-v0: 3fa1cc3
- lab02-ai-draft: 0a9fcd4
- skill v1 commit: 337b8cc
- lab02-implemented: фінальний коміт ЛР 2