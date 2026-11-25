import configparser

__all__ = ["load_mysql_config"]

DEFAULT_CONFIG_PATH = "config.ini"


def load_mysql_config(path: str = DEFAULT_CONFIG_PATH) -> dict:
    """
    讀取設定檔中的 MySQL 登入資訊。

    在程式啟動時呼叫，不在 import 時讀檔：只 import 這個模組（例如測試）不需要 config.ini。

    Raises:
        FileNotFoundError: 設定檔不存在或無法讀取。
        KeyError: 設定檔缺少 [mysql] 區段。
    """
    config = configparser.ConfigParser()
    if not config.read(path):
        raise FileNotFoundError(f"讀不到設定檔：{path}")

    mysql = config["mysql"]
    return {
        "host": mysql.get("host", "localhost"),
        "user": mysql.get("user", "root"),
        "password": mysql.get("password", ""),
        "database": mysql.get("database", ""),
        "port": mysql.getint("port", 3306),
    }
