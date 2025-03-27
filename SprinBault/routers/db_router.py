from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import get_connection_monedero
from security import hash_password, encrypt_password, decrypt_password, verify_password
from pydantic import BaseModel, EmailStr
from routers.db_queries import get_all_users, get_all_hardware, get_hardware_types, get_hardware_types, insert_hardware, get_hardware_password, get_normal_password, get_user_by_email, insert_user, delete_user_by_id, insert_hardware_types

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

class MasterPasswordRequest(BaseModel):
    password: str
    hardware_id: int

# Endpoint para mostrar la página de login
@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


# Endpoint para procesar el login
@router.post("/login")
async def login(
    request: Request, email: EmailStr = Form(...), password: str = Form(...)
):
    user = get_user_by_email(email)
    
    if user and verify_password(password, user["password_hash"]):
        response = RedirectResponse(url="/dashboard", status_code=303)
        
        # Convertir is_admin a string "1" o "0"
        is_admin_str = "1" if user["is_admin"] else "0"
        
        # Guardar la cookie del email del usuario logueado
        response.set_cookie(key="user_email", value=email, httponly=False, samesite="Lax", path="/")
        response.set_cookie(key="is_admin", value=is_admin_str, httponly=False, samesite="Lax", path="/")

        return response
    else:
        return RedirectResponse(url="/?error=invalid_credentials", status_code=303)


# Endpoint para registrarse
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# Endpoint para procesar el registro
@router.post("/register")
async def register_user(
    request: Request, email: EmailStr = Form(...), 
    password: str = Form(...), confirm_password: str = Form(...)
):
    if password != confirm_password:
        return RedirectResponse(url="/register?error=password_mismatch", status_code=303)

    hashed_password = hash_password(password)

    try:
        insert_user(email, hashed_password)
        return RedirectResponse(url="/users", status_code=303)  # Redirigir a login
    except Exception as e:
        return {"error": str(e)}


# Endpoint para mostrar el dashboard
@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# Endpoint para mostrar la página de usuarios con datos en tabla
@router.get("/users")
async def fetch_users(request: Request):
    users = get_all_users()
    return templates.TemplateResponse("users.html", {"request": request, "users": users})


# Endpoint para eliminar un usuario por su ID
@router.post("/delete_user/{user_id}")
async def delete_user(request: Request, user_id: int):
    """Elimina un usuario por su ID y redirige a /users"""
    
    # Verificar si el usuario está autenticado
    user_email = request.cookies.get("user_email")

    if not user_email:
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requiere autenticación.")

    # Intentar eliminar al usuario
    success = delete_user_by_id(user_id)
    
    if success:
        # Redirigir a la página de usuarios después de eliminar
        return RedirectResponse(url="/users", status_code=303)
    else:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")


# Endpoint para eliminar usarios por ID
@router.post("/delete_hardware_type/{type_id}")
async def delete_hardware_type(request: Request, type_id: int):
    """Elimina un tipo de hardware por su ID y redirige a /hardware_types"""
    
    # Verificar si el usuario está autenticado
    user_email = request.cookies.get("user_email")

    if not user_email:
        raise HTTPException(status_code=403, detail="Acceso denegado. Se requiere autenticación.")
    
    try:
        # Eliminar el tipo de hardware
        with get_connection_monedero() as connection:
            with connection.cursor() as cursor:
                query = "DELETE FROM hardwaretypes WHERE type_id = %s"
                cursor.execute(query, (type_id,))
                connection.commit()
                
        # Redirigir a la página de tipos de hardware después de eliminar
        return RedirectResponse(url="/hardware_types", status_code=303)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar el tipo de hardware: {str(e)}")


# Endpoint para mostrar la página de cambiar contraseñas
@router.get("/modify_passwords", response_class=HTMLResponse)
async def modify_passwords_page(request: Request):
    # Obtener el usuario logueado desde la cookie
    user_email = request.cookies.get("user_email")
    error_message = request.query_params.get("error")
    success_message = request.query_params.get("success")

    if not user_email:
        return {"error": "No estás autenticado"}

    return templates.TemplateResponse("modify_passwords.html", {
        "request": request,
        "user_email": user_email,
        "error_message": error_message,
        "success_message": success_message
    })


# Endpoint para modificar contraseñas
@router.post("/modify_passwords")
async def create_password(
    request: Request, 
    password: str = Form(...), 
    confirm_password: str = Form(...)
):
    """Crea una nueva contraseña para el usuario logueado"""

    # Verificar que las contraseñas coincidan
    if password != confirm_password:
        return RedirectResponse(url="/modify_passwords?error=password_mismatch", status_code=303)

    # Obtener el usuario logueado desde la cookie
    user_email = request.cookies.get("user_email")
    if not user_email:
        return {"error": "No estás autenticado"}

    # Cifrar la contraseña antes de guardarla
    from security import hash_password  # Asegúrate de importar la función
    hashed_password = hash_password(password)

    # Guardar en la base de datos
    from routers.db_queries import save_password_for_user
    save_password_for_user(user_email, hashed_password)

    return RedirectResponse(url="/modify_passwords?success=password_changed", status_code=303)


# Endpoint para eliminar hardware
@router.post("/delete_hardware")
def delete_hardware(delete_hardware_id: int = Form(...)):
    with get_connection_monedero() as connection:
        try:
            with connection.cursor() as cursor:
                # Query para eliminar todo el hardware por su ID
                query = "DELETE FROM hardware WHERE id = %s"
                cursor.execute(query, (delete_hardware_id,))
                connection.commit()
            return {"message": "Hardware y contraseña eliminados correctamente"}
        except Exception as e:
            connection.rollback()
            return {"error": str(e)}


# Endpoint para actualizar o borrar contraseñas de hardware
@router.post("/manage_passwords")
async def update_hardware_password(
    request: Request,
    hardware_id: int = Form(...),
    new_password: str = Form(...),
    confirm_new_password: str = Form(...),
):

    if new_password != confirm_new_password:
        return RedirectResponse(url="/insert?error=password_mismatch", status_code=303)

    # Usamos la función de encriptación para la nueva contraseña
    encrypted_password = encrypt_password(new_password)

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
@router.get("/hardware_types")
async def fetch_hardware_types(request: Request):
    hardware_types = get_hardware_types()
    return templates.TemplateResponse("hardware_types.html", {"request": request, "hardware_types": hardware_types})


# Endpoint para mostrar la página de agregar tipos de hardware
@router.get("/insert_hardware_types", response_class=HTMLResponse)
async def add_hardware_type_page(request: Request):
    return templates.TemplateResponse("insert_hardware_types.html", {"request": request})


# Endpoint para insertar un nuevo tipo de hardware
@router.post("/insert_hardware_types")
async def add_hardware_type(type_id: int = Form(...), type_name: str = Form(...)):
    with get_connection_monedero() as db:
        success = insert_hardware_types(db, type_id, type_name)

    if success:
        return RedirectResponse(url="/insert_hardware_types?success=true", status_code=303)
    else:
        return RedirectResponse(url="/insert_hardware_types?error=exists", status_code=303)
    
    
# Endpoint para eliminar un tipo de hardware
@router.post("/delete_hardware_type")
def delete_hardware_type(type_id: int = Form(...)):
    with get_connection_monedero() as connection:
        try:
            with connection.cursor() as cursor:
                # Eliminar el tipo de hardware por su ID
                query = "DELETE FROM hardwaretypes WHERE type_id = %s"
                cursor.execute(query, (type_id,))
                connection.commit()
            # Redirigir a la página de hardware_types después de eliminar
            return RedirectResponse(url='/hardware_types', status_code=303)
        except Exception as e:
            connection.rollback()
            return {"error": str(e)}


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

    # Usamos correctamente get_connection_monedero()
    with get_connection_monedero() as db:
        insert_hardware(db, id, codeName, IP, encrypted_password, hardware_type_id, localizacion)

    # Redirigir con un mensaje de éxito
    return RedirectResponse(url="/insert?success=true", status_code=303)