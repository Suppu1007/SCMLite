from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import threading

from app.routes.auth import router as auth_router
from app.routes.home import router as home_router
from app.routes.profile import router as profile_router
from app.routes.shipments import router as shipments_router
from app.routes.streams import router as streams_router
from app.routes.admin import router as admin_router
from app.routes.users import router as users_router
from app.routes.tracking import router as tracking_router

from app.core.config import ensure_default_admin
from app.services.tracking_service import start_tracking_engine

from fastapi import HTTPException
from fastapi.responses import RedirectResponse


app = FastAPI(title="SCMLite")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth_router)
app.include_router(home_router)
app.include_router(profile_router)
app.include_router(shipments_router)
app.include_router(streams_router)
app.include_router(admin_router)
app.include_router(users_router)
app.include_router(tracking_router)


@app.on_event("startup")
def startup_event():
    ensure_default_admin()

    # Start Tracking in Background Thread
    tracking_thread = threading.Thread(target=start_tracking_engine, daemon=True)
    tracking_thread.start()

    print("Shipment Tracking Engine Running...")


PUBLIC_PATHS = ["/", "/signup", "/static", "/favicon.ico"]

@app.middleware("http")
async def auth_redirect_middleware(request, call_next):
    path = request.url.path.lower()

    # allow public access paths
    if any(path.startswith(p) for p in PUBLIC_PATHS):
        return await call_next(request)

    try:
        return await call_next(request)
    except HTTPException as exc:
        if exc.status_code in (401, 403):
            return RedirectResponse("/", status_code=303)
        raise exc
