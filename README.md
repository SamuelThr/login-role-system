# Sistema de Autenticación y Control de Acceso Basado en Roles (RBAC)

API RESTful desarrollada con **FastAPI** y **SQLAlchemy** que implementa registro de usuarios, autenticación mediante tokens **JWT (JSON Web Tokens)**, cifrado de contraseñas con **BCrypt** y autorización basada en roles (`ADMIN` y `USER`).

## Tecnologías utilizadas

* **Lenguaje:** Python 3.13
* **Framework Web:** FastAPI + Uvicorn
* **Base de datos y ORM:** SQLite + SQLAlchemy
* **Validación de datos:** Pydantic
* **Seguridad:** Passlib (`bcrypt`) y Python-JOSE (JWT HS256)

## Estructura del proyecto

* `app/database.py`: Conexión a SQLite y gestión de sesiones.
* `app/models.py`: Tablas relacionales (`Rol` y `Usuario`).
* `app/schemas.py`: Validación de datos de entrada y salida.
* `app/security.py`: Cifrado de contraseñas y generación/validación de tokens JWT.
* `app/main.py`: Rutas de la API (`/register`, `/login`, `/me`, `/admin/usuarios`).

## Endpoints disponibles

| Método | Ruta | Acceso | Descripción |
| :--- | :--- | :--- | :--- |
| `POST` | `/register` | Público | Registra un usuario nuevo (`USER` o `ADMIN`). |
| `POST` | `/login` | Público | Valida credenciales y entrega un token JWT. |
| `GET` | `/me` | Autenticado | Muestra el perfil del usuario actual. |
| `GET` | `/admin/usuarios` | Solo `ADMIN` | Lista todos los usuarios registrados. |

## Cómo ejecutarlo localmente

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/SamuelThr/login-role-system.git](https://github.com/SamuelThr/login-role-system.git)
   cd login-role-system
   ```

2. Crear y activar el entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Encender el servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Abrir `http://127.0.0.1:8000/docs` en el navegador para probar los endpoints.
