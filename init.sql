-- init.sql
-- Простая "миграция" без Alembic: этот файл автоматически исполняется
-- официальным Postgres-образом при первом старте контейнера, так как
-- лежит в /docker-entrypoint-initdb.d/ (см. docker-compose.yml).
-- Все CREATE снабжены IF NOT EXISTS, чтобы файл можно было безопасно
-- прогнать вручную повторно (например, локально без docker).

CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    email       TEXT NOT NULL UNIQUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS payments (
    id          SERIAL PRIMARY KEY,
    payment_id  TEXT NOT NULL UNIQUE,   -- ключ идемпотентности от банка
    user_id     INTEGER NOT NULL REFERENCES users(id),
    amount      INTEGER NOT NULL,
    status      TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);

CREATE TABLE IF NOT EXISTS subscriptions (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL UNIQUE REFERENCES users(id), -- одна подписка на юзера -> удобно для UPSERT
    status      TEXT NOT NULL DEFAULT 'inactive',
    expires_at  TIMESTAMPTZ
);

-- В ТЗ (п.4) сказано "считай, что такая таблица есть" — создаём её здесь
-- же, чтобы query.sql можно было проверить локально на реальных данных.
CREATE TABLE IF NOT EXISTS meetings_attendance (
    user_id  INTEGER NOT NULL REFERENCES users(id),
    date     DATE NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_meetings_attendance_user_date
    ON meetings_attendance(user_id, date);

-- Тестовый пользователь с id=42, чтобы пример из ТЗ
-- ({"user_id": 42, ...}) можно было отправить сразу после старта.
INSERT INTO users (id, email) VALUES (42, 'test@example.com')
ON CONFLICT (id) DO NOTHING;

-- Подтягиваем sequence users_id_seq после ручной вставки с id=42,
-- иначе следующий INSERT с автогенерацией id может словить конфликт.
SELECT setval('users_id_seq', GREATEST((SELECT MAX(id) FROM users), 1));
