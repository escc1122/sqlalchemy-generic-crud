from sqlalchemy_generic_crud.models.base import Base


def get_models() -> dict[str, type]:
    """
    從 Base.registry 取出所有 model，回傳「表名 → model class」。

    只包含已經被 import 過的 model（SQLAlchemy 在定義 class 時才註冊進 registry）。
    """
    return {mapper.class_.__tablename__: mapper.class_ for mapper in Base.registry.mappers}


def get_model(table_name: str) -> type | None:
    """
    依表名取得 model class，找不到回傳 None。
    """
    return get_models().get(table_name)


def get_columns(model_class: type) -> list[str]:
    """
    取得 model 的欄位名稱（依定義順序）。
    """
    return [column.name for column in model_class.__table__.columns]
