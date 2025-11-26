from .auth import router as auth_router
from .admin import router as admin_router
from .shipments import router as shipments_router
from .streams import router as streams_router
from .tracking import router as tracking_router   # <-- ADD THIS

__all__ = [
    "auth_router",
    "admin_router",
    "shipments_router",
    "streams_router",
    "tracking_router"
]
