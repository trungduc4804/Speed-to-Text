from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from app.db import Base, engine
from app.api import auth, files, stt, minutes, pdf, signature, roles
from app.db import Base, engine, SessionLocal
from app.services.role_service import role_service

def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)
    
    # Initialize default roles and admin
    db = SessionLocal()
    try:
        role_service.init_default_roles(db)
        role_service.assign_first_user_as_admin(db)
    finally:
        db.close()
        
    app = FastAPI(title="Meeting Minutes STT", version="0.1.0")

    # Mount static files
    # Assuming frontend is at ../../frontend relative to this file?
    # backend/app/main.py
    # frontend is at backend/../frontend -> c:/TRUNGDUC/Do-An-TN/frontend
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
    UPLOADS_DIR = os.path.join(BASE_DIR, "backend", "uploads")
    
    app.mount("/static", StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")), name="static")
    # Mount uploads to serve audio/pdf files
    app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
    
    templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))

    # Routers grouped by domain.
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
    app.include_router(roles.router, prefix="/api/v1/roles", tags=["roles"])
    from app.api import users # Lazy import or add to top
    app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
    app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
    app.include_router(stt.router, prefix="/api/v1/stt", tags=["speech-to-text"])
    app.include_router(minutes.router, prefix="/api/v1/minutes", tags=["minutes"])
    app.include_router(pdf.router, prefix="/api/v1/pdf", tags=["pdf"])
    app.include_router(signature.router, prefix="/api/v1/signature", tags=["signature"])
    
    @app.get("/", response_class=HTMLResponse)
    async def read_root(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/login", response_class=HTMLResponse)
    async def login_page(request: Request):
        return templates.TemplateResponse("login.html", {"request": request})

    @app.get("/register", response_class=HTMLResponse)
    async def register_page(request: Request):
        return templates.TemplateResponse("register.html", {"request": request})
        
    @app.get("/meeting/{id}", response_class=HTMLResponse)
    async def meeting_detail(request: Request, id: int):
        return templates.TemplateResponse("meeting_detail.html", {"request": request, "id": id})

    @app.get("/admin", response_class=HTMLResponse)
    async def admin_page(request: Request):
        return templates.TemplateResponse("admin.html", {"request": request})

    return app


app = create_app()

