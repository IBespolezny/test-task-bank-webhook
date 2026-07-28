from app.config import settings
from contextlib import contextmanager

from psycopg2 import pool


# ThreadedConnectionPool — потому что uvicorn по умолчанию обслуживает
# синхронные path-функции в пуле потоков (run_in_threadpool), значит
# к пулу соединений может одновременно обращаться несколько потоков.
# SimpleConnectionPool для этого не потокобезопасен.
connection_pool = pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=settings.database_url,
)


@contextmanager
def _borrowed_connection():
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)


def get_db():
    """
    FastAPI-зависимость. Отдаёт соединение с открытой транзакцией
    (psycopg2 по умолчанию autocommit=False).

    Всё, что path-функция делает с этим соединением между `yield` и
    возвратом ответа, попадает в одну и ту же транзакцию:
      - если функция отработала без исключений -> conn.commit()
      - если было исключение -> conn.rollback(), состояние в БД
        остаётся таким, каким было до запроса.

    Это и есть гарантия из п.3 ТЗ: платёж и активация подписки
    коммитятся вместе или не коммитятся вовсе.
    """
    with _borrowed_connection() as conn:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
