import base64
from database import get_connection_sprinde, get_connection_monedero

# Función para insertar un nuevo usuario en la base de datos con is_admin = 0 (usuario normal).
def insert_user(email, password_hash):
    """Inserta un nuevo usuario en la base de datos con is_admin = 0 (usuario normal)."""
    query = """
    INSERT INTO users (email, password_hash, created_at, is_admin)
    VALUES (%s, %s, NOW(), 0)
    """
    with get_connection_sprinde() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (email, password_hash))
        conn.commit()
        
# Función para guardar una contraseña cifrada para un usuario en la base de datos
def save_password_for_user(email, hashed_password):
    query = "UPDATE users SET password_hash = %s WHERE email = %s"
    with get_connection_sprinde() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (hashed_password, email))
        conn.commit()
        
# Función para obtener la contraseña (NORMAL_PASSWORD) hasheada desde la base de datos
def get_normal_password():
    query = "SELECT key_value FROM normal_keys WHERE key_name = 'NORMAL_PASSWORD'"
    
    with get_connection_monedero() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            
            print(result)
            
            if result:
                return result  # Devuelve la contraseña hasheada
            return None

def get_master_test_key():
    """Obtiene la clave MASTER_TEST desde la base de datos."""
    query = "SELECT key_value FROM normal_keys WHERE key_name = 'MASTER_TEST'"

    with get_connection_monedero() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()

            if result:
                encrypted_key = result["key_value"]  # Obtenemos la clave en Base64
                decoded_key = base64.b64decode(encrypted_key)  # Decodificamos a bytes

                if len(decoded_key) != 32:
                    raise ValueError(f"Clave AES incorrecta: {len(decoded_key)} bytes en lugar de 32.")

                return decoded_key  # Retornamos la clave de 32 bytes lista para AES
            return None

# Función para obtener un usuario por su email
def get_user_by_email(email):
    query = "SELECT * FROM users WHERE email = %s"
    with get_connection_sprinde() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (email,))
            return cursor.fetchone()

# Función para borrar usuarios por su ID
def delete_user_by_id(user_id: int):
    query = "DELETE FROM users WHERE id = %s"
    try:
        with get_connection_sprinde() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id,))
                conn.commit()
                return cursor.rowcount > 0  # Retorna True si se eliminó un usuario
    except Exception as e:
        print(f"Error al eliminar el usuario: {e}")
        return False

# Función para obtener todos los usuarios de la tabla users
def get_all_users():
    with get_connection_sprinde() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, email, created_at FROM users")
            return cursor.fetchall()

# Función para obtener todos los dispositivos de la tabla hardware
def get_all_hardware():
    with get_connection_monedero() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, codeName, IP, Localizacion, Hardware_type_Id FROM hardware")
            return cursor.fetchall()

# Función para obtener la contraseña de un hardware
def get_hardware_password(hardware_id):
    query = "SELECT password_hash FROM hardware WHERE id = %s"
    with get_connection_monedero() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (hardware_id,))
            result = cursor.fetchone()
            print(result)

            if result is None:
                return None  # Si no se encuentra el hardware, retorna None

            return result

# Función para obtener todos los tipos de hardware
def get_hardware_types():
    with get_connection_monedero() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT type_id, type_name FROM hardwaretypes")
            return cursor.fetchall()
        

def insert_hardware_types(db, type_id, type_name):
    # Verificar si ya existe el tipo de hardware
    query = "SELECT type_id FROM hardwaretypes WHERE type_id = %s"
    with db.cursor() as cursor:
        cursor.execute(query, (type_id,))
        result = cursor.fetchone()

        if result:  # Si ya existe, result no será None
            return False  # El tipo de hardware ya existe

        # Insertar nuevo tipo de hardware
        insert_query = "INSERT INTO hardwaretypes (type_id, type_name) VALUES (%s, %s)"
        cursor.execute(insert_query, (type_id, type_name))
        db.commit()
        return True

        
# Función para insertar un nuevo hardware en la base de datos
def insert_hardware(db, id, codeName, IP, password, hardware_type_id, localizacion):
    query = """
    INSERT INTO hardware (id, CodeName, IP, password_hash, Hardware_type_Id, Localizacion) 
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    with db.cursor() as cursor:
        cursor.execute(query, (id, codeName, IP, password, hardware_type_id, localizacion))
    db.commit()