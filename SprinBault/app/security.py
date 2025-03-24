from cryptography.fernet import Fernet
import bcrypt
import os

# Generar una clave de cifrado para AES (asegúrate de almacenarla de forma segura)
KEY = os.getenv("ENCRYPTION_KEY") or Fernet.generate_key()
cipher = Fernet(KEY)

def encrypt_password(password: str) -> str:
    return cipher.encrypt(password.encode()).decode()

def hash_password(password: str) -> str:
    """Hashea la contraseña usando bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica una contraseña hasheada."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())