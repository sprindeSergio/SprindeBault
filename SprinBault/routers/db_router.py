from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import get_connection_monedero
from security import hash_password, encrypt_password, decrypt_password, verify_password
from pydantic import BaseModel
from routers.db_queries import get_all_users, get_all_hardware, get_hardware_types, get_hardware_types, insert_hardware, get_hardware_password, get_normal_password

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

class MasterPasswordRequest(BaseModel):
    password: str
    hardware_id: int

# Endpoint para mostrar la página de usuarios con datos en tabla
@router.get("/users")
async def fetch_users(request: Request):
    users = get_all_users()
    return templates.TemplateResponse("users.html", {"request": request, "users": users})


@router.get("/get_passwords")
async def get_passwords():
    """Devuelve la lista de usuarios con sus emails"""
    users = get_all_users()  # Obtener usuarios de la base de datos
    return users  # Retornar lista como JSON


@router.post("/create_password")
async def create_password(
    request: Request, 
    password: str = Form(...), 
    confirm_password: str = Form(...)
):
    """Crea una nueva contraseña para el usuario logueado"""

    # Verificar que las contraseñas coincidan
    if password != confirm_password:
        return RedirectResponse(url="/crud_user?error=password_mismatch", status_code=303)

    # Obtener el usuario logueado desde la cookie
    user_email = request.cookies.get("user_email")
    if not user_email:
        return {"error": "No estás autenticado"}

    # Cifrar la contraseña antes de guardarla
    from security import hash_password  # Asegúrate de importar la función
    hashed_password = hash_password(password)

    # Guardar en la base de datos (debes crear esta función en `db_queries.py`)
    from routers.db_queries import save_password_for_user
    save_password_for_user(user_email, hashed_password)

    return RedirectResponse(url="/crud_user", status_code=303)


# Endpoint para eliminar una contraseña de hardware"
@router.post("/delete_password")
def delete_hardware_password(delete_hardware_id: int = Form(...)):
    with get_connection_monedero() as connection:  # SIN "closing()"
        try:
            with connection.cursor() as cursor:
                query = "UPDATE hardware SET password_hash = '' WHERE id = %s"
                cursor.execute(query, (delete_hardware_id,))
                connection.commit()
            return {"message": "Contraseña eliminada correctamente"}
        except Exception as e:
            connection.rollback()
            return {"error": str(e)}


@router.post("/manage_passwords")
async def update_hardware_password(
    request: Request,
    hardware_id: int = Form(...),
    new_password: str = Form(...),
    confirm_new_password: str = Form(...),
):
    is_admin = request.cookies.get("is_admin", "0")
    if is_admin != "1":
        return {"error": "No tienes permisos para actualizar contraseñas"}

    if new_password != confirm_new_password:
        return RedirectResponse(url="/insert?error=password_mismatch", status_code=303)

    encrypted_password = hash_password(new_password)

    query = "UPDATE hardware SET password_hash = %s WHERE id = %s"
    with get_connection_monedero() as db:
        with db.cursor() as cursor:
            cursor.execute(query, (encrypted_password, hardware_id))
        db.commit()

    return RedirectResponse(url="/insert", status_code=303)


# Endpoint para mostrar la página de hardware con datos en tabla
@router.get("/hardware")
async def fetch_hardware(request: Request):
    hardware = get_all_hardware()
    return templates.TemplateResponse("hardware.html", {"request": request, "hardware": hardware})


# Endpoint para verificar la contraseña maestra
@router.post("/verify-master-password")
async def verify_master_password(data: dict):
    password = data.get("password")  # Obtiene la contraseña ingresada por el usuario
    hardware_id = data.get("hardware_id")  # Obtiene el ID del hardware

    # Obtiene la contraseña maestra hasheada desde la base de datos
    stored_hashed_password = get_normal_password()

    if not stored_hashed_password:
        raise HTTPException(status_code=500, detail="Error interno: No se encontró la contraseña maestra en la base de datos.")

    # Verifica la contraseña ingresada con bcrypt
    if not verify_password(password, stored_hashed_password['key_value']):
        raise HTTPException(status_code=401, detail="Contraseña maestra incorrecta")

    # Obtiene la contraseña encriptada del hardware
    hardware_password = get_hardware_password(hardware_id)

    if hardware_password is not None:
        # Si existe la contraseña de hardware, desencriptamos la contraseña
        decrypted_password = decrypt_password(hardware_password['password_hash'])

        # Retorna la contraseña desencriptada
        return {"message": "Contraseña maestra correcta", "hardware_password": decrypted_password}
    else:
        # Si no se encuentra el hardware, lanza un error 404
        raise HTTPException(status_code=404, detail="Hardware no encontrado")


# Endpoint para mostrar la página de tipos de hardware con datos en tabla
@router.get("/hardware-types")
async def fetch_hardware_types(request: Request):
    hardware_types = get_hardware_types()
    return templates.TemplateResponse("hardware_types.html", {"request": request, "hardware_types": hardware_types})


# Endpoint para mostrar la página de insertar hardware
@router.get("/insert", response_class=HTMLResponse)
async def insert_hardware_page(request: Request):
    hardware_types = get_hardware_types()
    hardware = get_all_hardware()
    is_admin = request.cookies.get("is_admin", "0")  # Obtiene el rol del usuario
    return templates.TemplateResponse(
        "insert_hardware.html", 
        {"request": request, "hardware_types": hardware_types, "hardware": hardware, "is_admin": is_admin}
    )


# Endpoint para insertar un nuevo hardware en la base de datos
@router.post("/insert")
async def insert_hardware_data(
    id: int = Form(...),
    codeName: str = Form(...),
    IP: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    hardware_type_id: int = Form(...),
    localizacion: str = Form(...),
):
    if password != confirm_password:
        return RedirectResponse(url="/insert?error=password_mismatch", status_code=303)

    encrypted_password = encrypt_password(password)

    # ✅ Usamos correctamente get_connection_monedero()
    with get_connection_monedero() as db:
        insert_hardware(db, id, codeName, IP, encrypted_password, hardware_type_id, localizacion)

    return RedirectResponse(url="/dashboard", status_code=303)