"""
證明「用表名反射出 model」可以跟 crud.select 組合使用：
只知道表名字串與條件 dict，就能撈出資料，不必在程式裡寫死 model class。

用 db.get_session 搭配 in-memory SQLite engine 開 session。
"""
import pytest
from sqlalchemy import Column, Integer, String

from sqlalchemy_generic_crud import db
from sqlalchemy_generic_crud.models import Base, Users
from sqlalchemy_generic_crud.repositories.crud import select
from sqlalchemy_generic_crud.repositories.table_reflection import get_columns, get_model, get_models


# 測試用的第二個 model：證明反射是動態找到所有 model，而不是只認得 Users
class Orders(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    item = Column(String)


@pytest.fixture
def session(engine):
    with db.get_session(engine) as s:
        s.add_all([
            Users(name="Alice", email="alice@example.com"),
            Users(name="Bob", email="bob@example.com"),
            Users(name="Alice", email="alice2@example.com"),
            Orders(user_id=1, item="book"),
            Orders(user_id=2, item="pen"),
        ])
        s.commit()
        yield s


def query_by_table_name(session, table_name: str, filters: dict, skip: int | None = None, limit: int | None = None):
    """組合使用：表名 → model class → 用條件建出 model 實例 → crud.select。"""
    model_class = get_model(table_name)
    return select(session, model_class(**filters), skip=skip, limit=limit)


# 反射要找得到所有已定義的 model；漏掉就代表某張表撈不到
def test_get_models_finds_all_defined_models():
    models = get_models()

    assert models["users"] is Users
    assert models["orders"] is Orders


# 不存在的表要回 None，呼叫端才能自己決定怎麼處理，而不是拋出 KeyError
def test_get_model_returns_none_for_unknown_table():
    assert get_model("no_such_table") is None


# 欄位清單要跟 model 定義一致（含順序），才能拿來決定要顯示 / 篩選哪些欄位
def test_get_columns_follows_model_definition():
    assert get_columns(Users) == ["id", "name", "email"]
    assert get_columns(Orders) == ["id", "user_id", "item"]


# 組合使用：只給表名與條件 dict，撈出的資料要跟直接用 Users(name="Alice") 查詢一樣
def test_query_by_table_name_with_filters(session):
    rows = query_by_table_name(session, "users", {"name": "Alice"})

    assert sorted(row.email for row in rows) == ["alice2@example.com", "alice@example.com"]
    assert all(isinstance(row, Users) for row in rows)


# 換一張表也能用同一段程式撈，證明沒有寫死 Users
def test_query_by_table_name_works_for_other_table(session):
    rows = query_by_table_name(session, "orders", {"item": "pen"})

    assert [(row.user_id, row.item) for row in rows] == [(2, "pen")]


# 不帶條件就是全撈；skip / limit 一樣能跟反射組合使用
def test_query_by_table_name_without_filters_and_with_paging(session):
    assert len(query_by_table_name(session, "users", {})) == 3
    assert len(query_by_table_name(session, "users", {}, skip=1, limit=1)) == 1


# 撈回來的 model 可以照 get_columns 的欄位轉成 dict，方便直接回傳給前端
def test_rows_can_be_converted_with_reflected_columns(session):
    model_class = get_model("users")
    rows = query_by_table_name(session, "users", {"email": "bob@example.com"})

    assert [{name: getattr(row, name) for name in get_columns(model_class)} for row in rows] == [
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
    ]
