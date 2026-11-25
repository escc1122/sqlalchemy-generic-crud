from functools import partial

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

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
    # crud 的 session 由呼叫端注入，測試直接開綁 SQLite 的 Session
    return partial(Session, engine)
