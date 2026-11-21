from datetime import datetime,timedelta,timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

#La clave secreta para firmar los tokens
SECRET_KEY = "CSSPCEP-JTPLDVM"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#Se configura BCrypt como algoritmo de hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Convierte una contraseña en texto plano en un hash seguro con BCrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """"Compara la contraseña ingresada en el login con el hash guardado en BD."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    """"Genera un token JWT con fecha de expiración"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes= ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict | None:
    """"Verifica la firma del token y extrae los datos del usuario, o None si expiró es invalido."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None