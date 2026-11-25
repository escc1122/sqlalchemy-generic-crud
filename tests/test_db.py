"""
db / config 解耦後要保證的事：
- 只 import db、config 不需要 config.ini（設定在啟動時才讀）
- 連線來源由呼叫端傳入的 engine 決定，換成 SQLite 也能直接用
- 設定檔讀不到要明確報錯，不能像以前 print 一行後丟出看不懂的 KeyError
"""
import pytest
from sqlalchemy import text

from sqlalchemy_generic_crud import db
from sqlalchemy_generic_crud.config import load_mysql_config


# 傳入 SQLite engine 就能開 session 下查詢；壞了代表 db 又綁回固定的 MySQL
def test_get_session_uses_given_engine(engine):
    with db.get_session(engine) as session:
        assert session.execute(text("select 1")).scalar() == 1


# get_connection 要能用 with；以前少了 @contextmanager，with 會丟 AttributeError
def test_get_connection_uses_given_engine(engine):
    with db.get_connection(engine) as connection:
        assert connection.execute(text("select 1")).scalar() == 1


# 離開 with 後 session 要關閉、交易不留著；壞了連線會一直被佔住
def test_get_session_closes_session(engine):
    with db.get_session(engine) as session:
        session.execute(text("select 1"))
        assert session.in_transaction()

    assert not session.in_transaction()


# 設定檔內容要正確組成 MySQL 連線字串
def test_load_mysql_config_and_build_url(tmp_path):
    config_file = tmp_path / "config.ini"
    config_file.write_text(
        "[mysql]\nhost = db.local\nuser = app\npassword = secret\ndatabase = demo\nport = 3307\n"
    )

    config = load_mysql_config(str(config_file))

    assert db.mysql_url(config) == "mysql+pymysql://app:secret@db.local:3307/demo"


# 讀不到設定檔要明確報錯，並指出是哪個路徑
def test_load_mysql_config_missing_file_raises(tmp_path):
    missing = tmp_path / "nope.ini"

    with pytest.raises(FileNotFoundError, match="nope.ini"):
        load_mysql_config(str(missing))
