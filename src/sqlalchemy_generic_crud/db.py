from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Connection, Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def mysql_url(config: dict) -> str:
    """
    把 MySQL 設定組成 SQLAlchemy 連線字串。

    Args:
        config: 含 user、password、host、port、database 的 dict（見 config.load_mysql_config）。
    """
    return (
        f"mysql+pymysql://{config['user']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{config['database']}"
    )


def create_mysql_engine(config: dict) -> Engine:
    """
    依 MySQL 設定建立 engine。程式啟動時建一次，之後把同一個 engine 傳給需要的地方。

    pool_pre_ping：每次從連線池取連線前先確認連線還活著，斷線會自動換新連線。
    """
    return create_engine(
        mysql_url(config),
        pool_size=10,  # 連接池大小
        max_overflow=20,  # 最大額外連接數
        pool_timeout=30,  # 連接超時時間（秒）
        pool_recycle=1800,  # 連接回收時間（秒）
        pool_pre_ping=True,
        echo=False,  # 設為 True 可啟用 SQL 查詢日誌（用於調試）
    )


@contextmanager
def get_session(engine: Engine) -> Iterator[Session]:
    """
    開一個綁在指定 engine 上的 Session，離開 with 區塊時自動關閉。

    engine 由呼叫端決定：正式環境傳 MySQL engine，測試可傳 SQLite engine。
    """
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def get_connection(engine: Engine) -> Iterator[Connection]:
    """
    開一條綁在指定 engine 上的 Connection，離開 with 區塊時自動關閉。
    """
    with engine.connect() as connection:
        yield connection
