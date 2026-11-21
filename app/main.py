from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import models, schemas, security
from .database import engine, get_db, SessionLocal

models.Base.metadata.create_all(bid=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa los roles base (ADMIN y USER) automáticamente al arrancar la API."""
    db = SessionLocal()
    try:
        roles_base= [
            {"nombre": "ADMIN", "descripcion": "Administrador con acceso total"},
            {"nombre": "USER", "descripcion": "Usuario estandar con acceso limitado"},
        ]
        for r in roles_base:
            existe = db.query(models.Rol).filter(models.Rol.nombre == r["nombre"]).first()
            if not existe:
                db.add(models.Rol(nombre=r["nombre"], descripcion=r["descripcion"]))
                db.commit()
    finally:
        db.close()
    yield

app = FastAPI(
    title= "Sistema de Login y Control de Roles (RBAC)",
    description= "API REST con autenticacion JWT y autorizacion basada en roles.",
    version="1.0.0",
    lifespan=lifespan,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.Usuario:
    """Extrae el token de la petición, lo valida y devuelve el usuario autenticado."""
    credenciales_invalidas= HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalido o expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload =security.decode_access_token(token)
    if payload is None:
        raise credenciales_invalidas

    username: str | None =payload.get("sub")
    if username is None:
        raise credenciales_invalidas

    usuario = db.query(models.Usuario).filter(models.Usuario.username == username).first()
    if usuario is None or not usuario.activo:
        raise credenciales_invalidas

    return usuario

def require_role(rol_requerido: str):
    """Genera un filtro que bloquea el acceso (403 Forbidden) si el usuario no tiene el rol exigido."""
    def role_checker(current_user: models.Usuario = Depends(get_current_user)):
        if current_user.rol.nombre != rol_requerido:
            raise HTTPException(
                status_code= status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: se requiere el rol '{rol_requerido}'",
            )
        return current_user
    return role_checker

@app.post("/register", response_model = schemas.UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(datos: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """Registra un nuevo usuario cifrando su contraseña y asignándole un rol."""
    if db.query(models.Usuario).filter(models.Usuario.username ==datos.username).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
    if db.query(models.Usuario).filter(models.Usuario.email ==datos.email).first():
        raise HTTPException(status_code=400, detail="El correo electronico ya está en uso")

    rol = db.query(models.Rol).filter(models.Rol.nombre ==datos.rol_nombre.upper()).first()
    if not rol:
        raise HTTPException(status_code=404, detail="El rol especificado no existe (usa ADMIN o USER)")
    nuevo_usuario =models.Usuario(
        username=datos.username,
        email=datos.email,
        password_hash=security.hash_password(datos.password),
        rol_id=rol.id,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@app.post("/login", response_model=schemas.Token)
def iniciar_sesion(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Valida credenciales y devuelve un token JWT con el usuario y su rol."""
    usuario = db.query(models.Usuario).filter(models.Usuario.username == form_data.username).first()

    if not usuario or not security.verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = security.create_access_token(
        data={"sub": usuario.username, "rol": usuario.rol.nombre}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.UsuarioResponse)
def leer_perfil_propio(current_user: models.Usuario = Depends(get_current_user)):
    """Ruta accesible para cualquier usuario autenticado (USER o ADMIN)."""
    return current_user


@app.get("/admin/usuarios", response_model=list[schemas.UsuarioResponse])
def listar_todos_los_usuarios(
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(require_role("ADMIN")),
):
    """Ruta exclusiva para administradores: lista todos los usuarios registrados."""
    return db.query(models.Usuario).all()