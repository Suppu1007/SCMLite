from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routes.auth import router as auth_router
from app.routes.home import router as home_router
from app.routes.profile import router as profile_router
from app.routes.shipments import router as shipments_router
from app.routes.streams import router as streams_router
from app.routes.admin import router as admin_router
from app.routes.users import router as users_router

from app.core.config import ensure_default_admin

app = FastAPI(title="SCMLite")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Routers
app.include_router(auth_router)
app.include_router(home_router)
app.include_router(profile_router)
app.include_router(shipments_router)
app.include_router(streams_router)
app.include_router(admin_router)
app.include_router(users_router)


@app.on_event("startup")
def startup_event():
    try:
        ensure_default_admin()
    except Exception as e:
        print("Admin creation failed:", e)
