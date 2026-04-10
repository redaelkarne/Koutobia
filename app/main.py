from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
import os

from app.routes import data
from app.config import API_TITLE, API_VERSION, SESSION_SECRET, SESSION_COOKIE_NAME
from app.services.cache_manager import CacheManager
from app.services.auth_service import AuthService

# Create app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description="API pour gérer les données d'approvisionnement"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    session_cookie=SESSION_COOKIE_NAME,
    same_site="lax",
    https_only=False,
)


def is_authenticated(request: Request) -> bool:
    return bool(request.session.get("authenticated") is True)


def require_api_auth(request: Request):
    if not is_authenticated(request):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

# Include routers
app.include_router(data.router, dependencies=[Depends(require_api_auth)])

# Setup static files and templates
APP_DIR = Path(__file__).resolve().parent
BASE_DIR = APP_DIR.parent
static_dir = APP_DIR / "static"
static_dir.mkdir(exist_ok=True)

# Serve static files
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize cache on startup"""
    try:
        # Load data into cache on startup
        CacheManager.get_all_data(use_cache=False)
        print("✅ Initial data loaded into cache")
    except Exception as e:
        print(f"⚠️ Error loading initial data: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint - redirect to dashboard"""
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/login")
async def login_page(request: Request):
    if is_authenticated(request):
        return RedirectResponse(url="/dashboard", status_code=303)
    login_file = APP_DIR / "templates" / "login.html"
    return FileResponse(str(login_file), media_type="text/html")


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if not AuthService.authenticate(username, password):
        return RedirectResponse(url="/login?error=1", status_code=303)

    request.session["authenticated"] = True
    request.session["username"] = username
    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)

@app.get("/dashboard")
async def dashboard(request: Request):
    """Serve dashboard HTML"""
    if not is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    dashboard_file = APP_DIR / "templates" / "dashboard.html"
    if dashboard_file.exists():
        return FileResponse(str(dashboard_file), media_type="text/html")
    return {"error": "Dashboard not found"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    stats = CacheManager.get_cache_stats()
    return {
        "status": "healthy",
        "cache": stats
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
