import bcrypt
from Crypto.Cipher import AES
import base64
from routers.db_queries import get_master_test_key

# Función para hashear contraseñas
def hash_password(password: str) -> str:
    """Hashea la contraseña usando bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

# Función para verificar contraseñas hasheadas
def verify_password(password: str, hashed_password: str) -> bool:
    """Verifica una contraseña hasheada."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# Función para encriptar contraseñas de hardware
def encrypt_password(password: str) -> str:
    """Cifra la contraseña con AES-256 y la retorna en base64."""
    master_test_key = get_master_test_key()  # Obtener la clave MASTER_TEST desde la base de datos
    
    if not master_test_key:
        raise Exception("No se pudo obtener la clave MASTER_TEST desde la base de datos.")

    cipher = AES.new(master_test_key, AES.MODE_CBC)  # Modo CBC
    iv = cipher.iv  # Vector de inicialización de 16 bytes

    # Asegurar que el texto tenga múltiplo de 16 bytes con padding PKCS7
    pad_len = 16 - (len(password) % 16)
    padded_password = password + chr(pad_len) * pad_len

    ciphertext = cipher.encrypt(padded_password.encode())

    # Guardamos IV + ciphertext en base64
    encrypted_password = base64.b64encode(iv + ciphertext).decode('utf-8')
    return encrypted_password

# Función para desencriptar contraseñas de hardware
def decrypt_password(encrypted_text: str) -> str:
    """Desencripta una contraseña en base64 con AES-256."""
    try:
        master_test_key = get_master_test_key()  # Obtener la clave MASTER_TEST desde la base de datos
        
        if not master_test_key:
            raise Exception("No se pudo obtener la clave MASTER_TEST desde la base de datos.")
        
        encrypted_data = base64.b64decode(encrypted_text)
        iv = encrypted_data[:16]  # Extraer IV
        cipher = AES.new(master_test_key, AES.MODE_CBC, iv)

        decrypted_data = cipher.decrypt(encrypted_data[16:])

        # Eliminar padding PKCS7
        pad_len = decrypted_data[-1]
        decrypted_data = decrypted_data[:-pad_len]

        return decrypted_data.decode('utf-8')

    except Exception as e:
        print(f"⚠️ Error desencriptando: {e}")
        return "Error al desencriptar"