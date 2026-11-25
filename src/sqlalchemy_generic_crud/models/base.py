from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 model 的基底類別；Base.registry 會記錄所有繼承它的 model（table_reflection 靠它依表名找 model）。"""
