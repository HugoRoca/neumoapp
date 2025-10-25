from datetime import datetime, timedelta
from typing import Optional
import hashlib
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Configuración de bcrypt para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _normalize_password(password: str) -> str:
    """
    Normaliza la contraseña usando SHA256 antes de bcrypt.
    Esto resuelve el límite de 72 bytes de bcrypt y mejora la seguridad.
    """
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que la contraseña coincida con el hash.
    Normaliza la contraseña con SHA256 antes de verificar con bcrypt.
    """
    normalized_password = _normalize_password(plain_password)
    return pwd_context.verify(normalized_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña.
    Primero normaliza con SHA256, luego aplica bcrypt.
    """
    normalized_password = _normalize_password(password)
    return pwd_context.hash(normalized_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decodifica un token JWT"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

