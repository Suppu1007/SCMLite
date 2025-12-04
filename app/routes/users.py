# app/routes/users.py

from fastapi import APIRouter, Depends, HTTPException, Form
from app.core.config import users_collection
from app.core.dependencies import admin_required

api_router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
    dependencies=[Depends(admin_required)],
)


@api_router.get("/")
async def list_users():
    users = list(users_collection.find({}, {"password": 0}))
    return {"users": users}


@api_router.get("/{email}")
async def get_user(email: str):
    user = users_collection.find_one({"email": email}, {"password": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@api_router.post("/status")
async def update_status(email: str = Form(...), status: str = Form(...)):
    result = users_collection.update_one({"email": email}, {"$set": {"status": status}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Status updated"}
