from app.config import settings
from contextlib import contextmanager

from psycopg2 import pool

#Выбран, чтобы избегать гонку данных, SimpleConnectionPull не синхронизирует доступ
#11 одновременный запрос выкинет ошибку, минус синхронности
connection_pool = pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=10,
    dsn=settings.database_url,
)


@contextmanager
def _borrowed_connection():
    """
    Контекстный менеджер, который отдаёт свободное соединение и после кладёт его обратно.
    """
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)


def get_db():
    """
    всё, что происходит в эндпоинте, заходит в одну транзакцию.

    Либо всё удачно коммитится, либо откатывается до начала транзакции. 
    """
    with _borrowed_connection() as conn:
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
