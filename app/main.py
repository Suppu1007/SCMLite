# app/main.py

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.openapi.utils import get_openapi
from fastapi.templating import Jinja2Templates

from app.core.security import decode_token
from app.core.config import ensure_default_admin

# app
app = FastAPI(
    title="SCMLite API",
    version="2.0.0",
    description="SCMLite backend with Cookie-Based UI Auth & JWT API Auth",
)

# Static Files & Templates
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# Custom Swagger JWT Auth Button
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes
    )

    schema.setdefault("components", {}).setdefault("securitySchemes", {})
    schema["components"]["securitySchemes"]["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }

    schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi



# ROUTES
from app.routes.auth import ui_router as auth_ui_router, api_router as auth_api_router
from app.routes.home import ui_router as home_ui_router, api_router as home_api_router
from app.routes.profile import ui_router as profile_ui_router, api_router as profile_api_router
from app.routes.shipments import ui_router as shipments_ui_router, api_router as shipments_api_router
from app.routes.tracking import ui_router as tracking_ui_router, api_router as tracking_api_router
from app.routes.streams import ui_router as streams_ui_router, api_router as streams_api_router
from app.routes.admin import ui_router as admin_ui_router, api_router as admin_api_router
from app.routes.users import api_router as users_api_router

# User interface
app.include_router(auth_ui_router)
app.include_router(home_ui_router)
app.include_router(profile_ui_router)
app.include_router(shipments_ui_router)
app.include_router(tracking_ui_router)
app.include_router(streams_ui_router)
app.include_router(admin_ui_router)

# APIs
app.include_router(auth_api_router)
app.include_router(home_api_router)
app.include_router(profile_api_router)
app.include_router(shipments_api_router)
app.include_router(tracking_api_router)
app.include_router(streams_api_router)
app.include_router(admin_api_router)
app.include_router(users_api_router)



# PUBLIC & PROTECTED ROUTE GUARD
PUBLIC_PATHS = {
    "/", "/login", "/signup",
    "/forgot-password", "/reset-password"
}

PUBLIC_PREFIXES = [
    "/static", "/favicon", "/docs", "/openapi.json"
]


@app.middleware("http")
async def authentication_guard(request: Request, call_next):
    path = request.url.path.lower()
    token = request.cookies.get("access_token")
    email = decode_token(token) if token else None
    logged_in = email is not None

    # Allow all APIs – JWT checked 
    if path.startswith("/api"):
        return await call_next(request)

    # Allow all public routes + static files
    if path in PUBLIC_PATHS or any(path.startswith(pref) for pref in PUBLIC_PREFIXES):
        if logged_in and path == "/":
            return RedirectResponse("/dashboard", status_code=303)
        return await call_next(request)

    # If protected & not logged in
    if not logged_in:
        return RedirectResponse("/login", status_code=303)

    # Disable caching for authenticated UI pages
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    return response


#  Admin Exists)
@app.on_event("startup")
def initialize():
    ensure_default_admin()
