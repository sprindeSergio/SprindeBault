import os
from contextlib import contextmanager
import pymysql
from pymysql.cursors import DictCursor

# Conexión a la base de datos SprindeUserAuthDatabase
@contextmanager
def get_connection_sprinde():
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "1234"),
            db="SprindeUserAuthDatabase",
            autocommit=True,
            cursorclass=DictCursor,
        )
        yield connection
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()

# Conexión a la base de datos MonederoPW
@contextmanager
def get_connection_monedero():
    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "1234"),
            db="MonederoPW",
            autocommit=True,
            cursorclass=DictCursor,
        )
        yield connection
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()