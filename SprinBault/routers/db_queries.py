from database import get_connection_sprinde, get_connection_monedero
from database import get_connection_monedero
from sqlalchemy.orm import Session

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
        
def save_password_for_user(email, hashed_password):
    """Guarda una contraseña cifrada para un usuario en la base de datos."""
    query = "UPDATE users SET password_hash = %s WHERE email = %s"
    with get_connection_sprinde() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (hashed_password, email))
        conn.commit()

def get_user_by_email(email):
    """Obtiene un usuario por su email."""
    query = "SELECT * FROM users WHERE email = %s"
    with get_connection_sprinde() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (email,))
            return cursor.fetchone()

def get_all_users():
    """Obtiene todos los usuarios de la tabla users en SprindeUserAuthDatabase"""
    with get_connection_sprinde() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, email, created_at FROM users")
            return cursor.fetchall()

def get_all_hardware():
    """Obtiene todos los dispositivos de la tabla hardware en MonederoPW"""
    with get_connection_monedero() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, codeName, IP, Localizacion, Hardware_type_Id FROM hardware")
            return cursor.fetchall()

def get_hardware_types():
    """Obtiene todos los tipos de hardware de la tabla hardwaretypes en MonederoPW"""
    with get_connection_monedero() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT type_id, type_name FROM hardwaretypes")
            return cursor.fetchall()
        
def insert_hardware(db, id, codeName, IP, password, hardware_type_id, localizacion):
    """Inserta un nuevo hardware en la base de datos usando SQL puro."""
    query = """
    INSERT INTO hardware (id, CodeName, IP, password_hash, Hardware_type_Id, Localizacion) 
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    with db.cursor() as cursor:  # db ya es la conexión, no hay que llamarla como función
        cursor.execute(query, (id, codeName, IP, password, hardware_type_id, localizacion))
    db.commit()