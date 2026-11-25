from functools import partial

import pytest
from sqlalchemy import create_engine

from sqlalchemy_generic_crud import db
from sqlalchemy_generic_crud.models import Base


@pytest.fixture
def engine():
    # 每個測試一個新的 in-memory SQLite，測試之間資料不互相影響
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def get_mock_session(engine):
    # db.get_session 直接吃 engine，不必連 MySQL
    return partial(db.get_session, engine)
