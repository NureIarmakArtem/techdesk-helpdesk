МАТРИЦЯ ВИЯВЛЕННЯ МУТАЦІЙ (T0 / T1 x M1-M3)

Базовий код R0 (lab02-implemented): 54b781a
Зафіксований набір тестів T1: 9fc642e

| Версія | Хеш мутації | Виявив T0 | Виявив T1 | Доказ у протоколі |
|--------|-------------|-----------|-----------|-------------------|
| M1. Повторне відкриття CLOSED -> OPEN | ee5e2cc | Так | Так | T0: test_t09_t10_status_transitions (200 замість 409, GET повертає OPEN). T1: додатково test_lr3_all_nine_status_transitions[CLOSED-OPEN-409]. Логи: m1-t0.log, m1-t1.log |
| M2. Частковий PATCH (priority + assignee_id=999) | 78fa460 | Ні | Так | T0: 15 passed (пропущено). T1: test_lr3_patch_atomicity_priority_and_unknown_assignee (PATCH дав 422, але повторний GET повернув priority=high замість medium при assignee_id=1). Логи: m2-t0.log, m2-t1.log |
| M3. Небезпечна підстановка title у SQL (O'Brien) | c67cbaa | Ні | Так | T0: 15 passed (пропущено). T1: test_lr3_title_with_apostrophe_saved_exact[O'Brien] впав із sqlite3.OperationalError. Bandit (bandit-m3.json) виявив B608. Логи: m3-t0.log, m3-t1.log |

Метрика контрольованого mutation score:
- MS(T0) = 1 / 3 * 100% = 33.3%
- MS(T1) = 3 / 3 * 100% = 100.0%