from database import get_connection_monedero
import base64

# Creamos una clave de EXACTAMENTE 32 bytes
MASTER_TEST = b'TuClaveDe32BytesAquiTuClaveDe32B'  # Exactamente 32 bytes

def insert_key():
    """Inserta MASTER_TEST (en Base64) en la tabla normal_keys."""

    # Convertimos la clave a Base64 antes de guardarla
    master_test_b64 = base64.b64encode(MASTER_TEST).decode('utf-8')

    # Query para insertar en la base de datos
    query = """
        INSERT INTO normal_keys (key_name, key_value, created_at)
        VALUES (%s, %s, NOW())
    """

    try:
        with get_connection_monedero() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, ("MASTER_TEST", master_test_b64))
                conn.commit()
                print("✅ Clave insertada correctamente en la base de datos.")

    except Exception as e:
        print(f"❌ Error al insertar clave: {e}")

# Ejecutar el script
if __name__ == "__main__":
    insert_key()