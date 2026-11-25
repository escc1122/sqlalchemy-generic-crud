# sqlalchemy-generic-crud

SQLAlchemy 2.0 的通用 CRUD 範例，有兩個重點：

1. **用 model 實例當查詢條件**：`select(session, Users(name="Alice"))`，有值的欄位就是等值條件。
2. **依表名反射撈資料**：只知道表名字串，也能從 `Base.registry` 找到 model，再搭配上面的 CRUD 撈資料，不必在程式裡寫死 model class。

DB 連線由呼叫端傳入 engine 決定，正式環境接 MySQL、測試直接用 in-memory SQLite，不必 mock。

## 結構

```
src/sqlalchemy_generic_crud/
  config.py                         # load_mysql_config()：啟動時讀 config.ini
  db.py                             # create_mysql_engine()、get_session(engine)、get_connection(engine)
  models/base.py                    # Base（DeclarativeBase）
  models/users.py                   # 範例 model
  repositories/crud.py              # create / select / select_from_pydantic / update / delete
  repositories/table_reflection.py  # get_models / get_model / get_columns
tests/                              # 全部用 in-memory SQLite
```

## 開始

```bash
uv sync
cp config.ini.example config.ini   # 填 MySQL 連線資訊（只有連 MySQL 時需要，測試不需要）
uv run pytest
```

## 用法

### 連線

```python
from sqlalchemy_generic_crud.config import load_mysql_config
from sqlalchemy_generic_crud.db import create_mysql_engine, get_session

engine = create_mysql_engine(load_mysql_config())   # 程式啟動時建一次

with get_session(engine) as session:
    ...
```

### CRUD

```python
from sqlalchemy_generic_crud.models import Users
from sqlalchemy_generic_crud.repositories.crud import create, delete, select

with get_session(engine) as session:
    create(session, Users(name="Alice", email="alice@example.com"))

    select(session, Users(name="Alice"))            # WHERE name = 'Alice'
    select(session, Users(), skip=0, limit=10)      # 不帶條件 + 分頁

    delete(session, Users(name="Alice"))            # 不帶任何條件會拋 DeleteException
```

### 依表名反射撈資料

```python
from sqlalchemy_generic_crud.repositories.crud import select
from sqlalchemy_generic_crud.repositories.table_reflection import get_columns, get_model

model_class = get_model("users")                    # 找不到回 None
rows = select(session, model_class(**{"name": "Alice"}))
data = [{c: getattr(row, c) for c in get_columns(model_class)} for row in rows]
```

### 測試時換成 SQLite

```python
from sqlalchemy import create_engine
from sqlalchemy_generic_crud.models import Base

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(bind=engine)

with get_session(engine) as session:
    ...
```

## 注意事項

- **值為 `None` 的欄位不會成為條件**，所以查不了 `IS NULL`。
- **條件值不會依欄位型別轉型**：SQLAlchemy 對 Integer / Date 等型別不轉型，字串 `"800"` 會原樣送給 DB（MySQL 會隱式轉換）；Boolean 欄位收到字串 `"true"` 會直接拋 `TypeError`。值來自使用者輸入時要自己先轉型。
- **反射只找得到已 import 過的 model**：model 在 class 定義時才註冊進 `Base.registry`。
- **建 model 實例當條件會觸發 model 的 `@validates`**：有寫入用驗證的欄位，查詢條件也會被驗證。
- 依表名反射若開放給外部使用，記得用白名單限制可查的表，並自行檢查欄位名稱。
- `create` / `update` / `delete` 會在函式內 commit，多個操作無法包成同一個交易。
