from database import get_connection_monedero
from security import hash_password

# Claves a insertar
NORMAL_PASSWORD = "Abcd1234"  # Esta es la contraseña maestra que se guardará hasheada

def insert_keys():
    """Inserta NORMAL_PASSWORD (hasheada) y MASTER_TEST (encriptada) en la tabla normal_keys."""

    # Hashear la NORMAL_PASSWORD con bcrypt
    hashed_password = hash_password(NORMAL_PASSWORD)

    # Query para insertar en la base de datos
    query = """
        INSERT INTO normal_keys (key_name, key_value, created_at)
        VALUES (%s, %s, NOW())
    """

    try:
        with get_connection_monedero() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, ("NORMAL_PASSWORD", hashed_password))
                conn.commit()
                print("✅ Clave insertada correctamente en la base de datos.")

    except Exception as e:
        print(f"❌ Error al insertar clave: {e}")

# Ejecutar el script
if __name__ == "__main__":
    insert_keys()