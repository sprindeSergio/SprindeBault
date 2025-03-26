from fastapi import FastAPI, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers.db_queries import insert_user, get_user_by_email
from security import hash_password, verify_password
from routers.db_router import router as db_router
from pydantic import EmailStr

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(db_router)

# Rutas de la aplicación

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register_user(
    request: Request, email: EmailStr = Form(...), 
    password: str = Form(...), confirm_password: str = Form(...)
):
    if password != confirm_password:
        return RedirectResponse(url="/register?error=password_mismatch", status_code=303)

    hashed_password = hash_password(password)

    try:
        insert_user(email, hashed_password)
        return RedirectResponse(url="/", status_code=303)  # Redirigir a login
    except Exception as e:
        return {"error": str(e)}

@app.post("/login")
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

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/crud_user", response_class=HTMLResponse)
async def crud_user_page(request: Request):
    return templates.TemplateResponse("crud_user.html", {"request": request})

@app.get("/crud_admin", response_class=HTMLResponse)
async def crud_admin_page(request: Request):
    return templates.TemplateResponse("crud_admin.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)