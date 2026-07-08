import base64, hashlib, hmac, json, time, secrets
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

bearer = HTTPBearer()

def _sign(payload: bytes) -> str:
    return hmac.new(settings.SECRET_KEY.encode(), payload, hashlib.sha256).hexdigest()

def create_token(username: str) -> str:
    payload = json.dumps({'sub': username, 'iat': int(time.time())}, separators=(',', ':')).encode()
    body = base64.urlsafe_b64encode(payload).decode().rstrip('=')
    sig = _sign(body.encode())
    return f'{body}.{sig}'

def verify_token(token: str) -> str:
    try:
        body, sig = token.split('.', 1)
        expected = _sign(body.encode())
        if not hmac.compare_digest(sig, expected):
            raise ValueError('bad signature')
        payload = json.loads(base64.urlsafe_b64decode(body + '=' * (-len(body) % 4)))
        if payload.get('sub') != settings.QUINT_USER:
            raise ValueError('bad subject')
        return payload['sub']
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')

def authenticate(username: str, password: str) -> bool:
    return secrets.compare_digest(username, settings.QUINT_USER) and secrets.compare_digest(password, settings.QUINT_PASSWORD)

def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    return verify_token(credentials.credentials)
