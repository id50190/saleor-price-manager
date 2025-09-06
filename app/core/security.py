from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
import jwt
from app.core.config import settings

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Проверяет JWT-токен от Saleor"""
    try:
        token = credentials.credentials
        # Проверяем токен (предполагаем, что Saleor использует стандартный JWT)
        decoded = jwt.decode(token, settings.SALEOR_APP_TOKEN, algorithms=["HS256"])
        return token
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
