import base64

def check_master_test_size():
    encrypted_key = "VHVDbGF2ZURlMzJCeXRlc0FxdWlUdUNsYXZlRGUzMkI="
    
    try:
        decoded_key = base64.b64decode(encrypted_key)
        print(f"🔹 Clave decodificada (bytes): {decoded_key}")
        print(f"📏 Tamaño de la clave: {len(decoded_key)} bytes")
        
    except Exception as e:
        print(f"❌ Error al decodificar Base64: {e}")

check_master_test_size()
