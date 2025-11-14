from fastapi import Header, HTTPException, status
from typing import Optional


async def get_request_user(x_user_id: Optional[int] = Header(default=None), x_role: Optional[str] = Header(default="User")):
    if x_role not in ("User", "Admin"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
    return {"user_id": x_user_id, "role": x_role}