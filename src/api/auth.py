import os
import urllib.request
import json
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, jwk
from jose.utils import base64url_decode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.db.database import get_db
from src.db.models import User
from src.config.settings import settings

security = HTTPBearer()

AUTH0_DOMAIN = settings.auth0_domain
AUTH0_AUDIENCE = settings.auth0_audience
AUTH0_ALGORITHMS = ["RS256"]


def get_auth0_jwks():
    url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    try:
        response = urllib.request.urlopen(url)
        return json.loads(response.read())
    except Exception as e:
        print(f"Error fetching JWKS from Auth0: {e}")
        return {}

def verify_jwt(token: str):
    jwks = get_auth0_jwks()
    unverified_header = jwt.get_unverified_header(token)
    
    rsa_key = {}
    for key in jwks.get("keys", []):
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
            break
            
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=AUTH0_ALGORITHMS,
                audience=AUTH0_AUDIENCE,
                issuer=f"https://{AUTH0_DOMAIN}/"
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token is expired")
        except jwt.JWTClaimsError:
            raise HTTPException(status_code=401, detail="Incorrect claims, check audience and issuer")
        except Exception:
            raise HTTPException(status_code=401, detail="Unable to parse authentication token")
            
    raise HTTPException(status_code=401, detail="Unable to find appropriate key")

def get_user_email_from_userinfo(token: str) -> str | None:
    """Consulta el endpoint de perfil /userinfo de Auth0 para obtener el email."""
    url = f"https://{AUTH0_DOMAIN}/userinfo"
    try:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("email")
    except Exception as e:
        print(f"Error fetching userinfo from Auth0: {e}")
        return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Valida el token de Auth0 y sincroniza al usuario en la BD si no existe.
    Retorna el objeto User de la BD.
    """
    token = credentials.credentials
    payload = verify_jwt(token)
    
    auth0_id = payload.get("sub")
    email = payload.get(f"{AUTH0_AUDIENCE}/email") or payload.get("email")
    
    if not auth0_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Sync User with DB
    result = await db.execute(select(User).where(User.id == auth0_id))
    user = result.scalars().first()
    
    if not user:
        # Si no viene en el token, lo buscamos en el endpoint de userinfo
        if not email:
            email = get_user_email_from_userinfo(token)
            
        # Create user on first login
        user = User(id=auth0_id, email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif not user.email:
        # Autocorrección si el usuario ya existía pero no tenía email
        email = get_user_email_from_userinfo(token)
        if email:
            user.email = email
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
    return user

