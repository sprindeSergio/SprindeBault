from security import hash_password, encrypt_password
from database import get_connection_monedero

# Claves a insertar
NORMAL_PASSWORD = "Abcd1234"  # Esta es la contraseña maestra que se guardará hasheada
MASTER_TEST = "TuClaveDe32BytesAquiTuClaveDe32B"  # Esta es la clave que se guardará encriptada

def insert_keys():
    """Inserta NORMAL_PASSWORD (hasheada) y MASTER_TEST (encriptada) en la tabla normal_keys."""

    # Hashear la NORMAL_PASSWORD con bcrypt
    hashed_password = hash_password(NORMAL_PASSWORD)

    # Encriptar la MASTER_TEST con AES-256
    encrypted_master_test = encrypt_password(MASTER_TEST)

    # Query para insertar en la base de datos
    query = """
        INSERT INTO normal_keys (key_name, key_value, created_at)
        VALUES (%s, %s, NOW()), (%s, %s, NOW())
    """

    try:
        with get_connection_monedero() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, ("NORMAL_PASSWORD", hashed_password, "MASTER_TEST", encrypted_master_test))
                conn.commit()
                print("✅ Claves insertadas correctamente en la base de datos.")

    except Exception as e:
        print(f"❌ Error al insertar claves: {e}")

# Ejecutar el script
if __name__ == "__main__":
    insert_keys()