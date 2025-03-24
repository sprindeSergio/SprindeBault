from database import get_connection_sprinde, get_connection_monedero

try:
    with get_connection_sprinde() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            print("Conexión exitosa a la base de datos SprindeUserAuthDatabase:", db_name["DATABASE()"])
except Exception as e:
    print("Error al conectar a SprindeUserAuthDatabase:", e)

try:
    with get_connection_monedero() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()
            print("Conexión exitosa a la base de datos MonederoPW:", db_name["DATABASE()"])
except Exception as e:
    print("Error al conectar a MonederoPW:", e)