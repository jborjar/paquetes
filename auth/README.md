# Sistema de Autenticación con Session Tokens

> ✨ **MÓDULO PORTABLE**: Sistema de autenticación genérico con soporte multi-backend. Funciona con JSON (por defecto), MSSQL, o cualquier backend personalizado.

Sistema completo de autenticación con session tokens, renovación automática (sliding expiration) y soporte para múltiples backends de almacenamiento.

## 📋 Características

- ✅ **Session Tokens**: Autenticación basada en tokens de sesión (UUID)
- ✅ **Sliding Expiration**: Renovación automática en cada petición
- ✅ **Multi-Backend**: JSON (default), MSSQL, o backends personalizados
- ✅ **Portable**: Funciona sin dependencias externas con JSON storage
- ✅ **Timeout configurable**: 30 minutos por defecto (variable de entorno)
- ✅ **Límite de sesiones**: Máximo de sesiones activas por usuario (configurable por usuario)
- ✅ **Scopes/Permisos**: Soporte para permisos granulares
- ✅ **Decoradores**: Protección de rutas con `@require_auth()`
- ✅ **Multi-framework**: Compatible con Flask y FastAPI
- ✅ **Genérico**: Sin hardcodeo, configurable vía código o `.env`
- ✅ **Limpieza automática**: Función para eliminar sesiones expiradas
- ✅ **Thread-Safe**: Operaciones seguras en entornos concurrentes
- ✅ **Cookie-based Auth**: Soporte para autenticación con cookies HTTP-only
- ✅ **Panel de Admin**: Interfaz web de administración incluida

## 📦 Estructura

```
auth/
├── __init__.py              # Exporta todas las funciones
├── sessions.py              # Gestión de sesiones (usa storage abstraction)
├── storage.py               # Interface abstracta para backends
├── storage_json.py          # Backend JSON (por defecto)
├── storage_mssql.py         # Backend MSSQL (requiere configuración)
├── middleware.py            # Decoradores para proteger rutas
├── endpoints.py             # Helpers para login/logout
└── README.md                # Esta documentación

paquetes/tests/auth/ (ejemplos de uso)
├── example_auth_flask.py    # Ejemplo completo con Flask
└── example_auth_fastapi.py  # Ejemplo completo con FastAPI
```

## 🔧 Instalación

### Dependencias

**Sin dependencias para uso básico con JSON:**

El módulo funciona sin dependencias externas usando almacenamiento JSON por defecto.

**Para usar MSSQL:**

```bash
pip install pyodbc
```

### Configuración de Storage Backend

El sistema soporta múltiples backends de almacenamiento. Por defecto usa JSON (sin base de datos).

#### Opción 1: JSON Storage (Por Defecto)

No requiere configuración. Funciona automáticamente:

```python
from paquetes.auth import create_session, validate_session

# Usa JSON automáticamente (sessions.json)
session = create_session('usuario', 'read:users')
```

Para especificar archivo JSON personalizado:

```python
from paquetes.auth import configure_storage
from paquetes.auth.storage_json import JSONSessionStorage

# Configurar archivo personalizado
configure_storage(JSONSessionStorage('/ruta/a/mis_sesiones.json'))
```

Variable de entorno:

```env
AUTH_SESSIONS_FILE=/ruta/a/sesiones.json  # Default: sessions.json
```

#### Opción 2: MSSQL Storage

Configurar al iniciar la aplicación:

```python
from paquetes.auth import configure_storage
from paquetes.auth.storage_mssql import MSSQLSessionStorage
from paquetes.mssql import get_mssql_connection

# Configurar MSSQL storage
configure_storage(MSSQLSessionStorage(get_mssql_connection))

# Crear tabla si no existe
from paquetes.auth import ensure_sessions_table
ensure_sessions_table()
```

Variables de entorno para MSSQL:

```env
# Conexión MSSQL
MSSQL_HOST=localhost
MSSQL_DATABASE=mi_database
MSSQL_USER=sa
MSSQL_PASSWORD=tu_password
```

### Variables de Entorno Comunes

```env
# Configuración de sesiones (aplica a todos los backends)
SESSION_EXPIRATION_MINUTES=30      # Timeout de sesión (default: 30)
SESIONES_ACTIVAS=2                 # Máximo de sesiones por usuario (default: 2)

# Validador de usuarios (tu implementación)
AUTH_VALIDATOR_MODULE=paquetes.auth.validators
AUTH_VALIDATOR_FUNCTION=validate_user
```

**Nota:** El sistema usa **UUID v4** como session tokens (no JWT). El nombre de la variable `SESSION_EXPIRATION_MINUTES` (o el legacy `JWT_EXPIRATION_MINUTES`) controla el tiempo de expiración.

## 🔑 Validador de Usuarios

El módulo requiere que implementes tu propia función de validación de credenciales. Puedes validar contra:

- Base de datos (MSSQL, HANA, PostgreSQL, etc.)
- LDAP/Active Directory
- API externa
- Cualquier otro sistema

### Crear tu Validador

1. Crea un archivo `validators.py`:

```python
# paquetes/auth/validators.py
def validate_user(username: str, password: str) -> bool:
    """
    Valida credenciales de usuario.

    Args:
        username: Nombre de usuario
        password: Contraseña en texto plano

    Returns:
        True si credenciales son válidas, False en caso contrario
    """
    # Tu lógica aquí
    # Ejemplo: validar contra tabla USERS en MSSQL
    from paquetes.mssql import select_one
    import hashlib

    password_hash = hashlib.sha256(password.encode()).hexdigest()
    user = select_one('USERS', where={
        'Username': username,
        'PasswordHash': password_hash,
        'Active': 1
    })

    return user is not None
```

2. Configura en `.env`:

```env
AUTH_VALIDATOR_MODULE=paquetes.auth.validators
AUTH_VALIDATOR_FUNCTION=validate_user
```

Ver archivos de ejemplo en `paquetes/tests/auth/` para más ejemplos de validadores.

## 🚀 Uso Rápido

### 1. Inicializar Tabla de Sesiones

```python
from paquetes.auth import ensure_sessions_table

# Crear tabla USER_SESSIONS si no existe
ensure_sessions_table()
```

### 2. Login

```python
from paquetes.auth import login_user

# Login de usuario
result = login_user('admin', 'password123', scopes='read:users,write:users')

if result['success']:
    session = result['session']
    print(f"Session ID: {session['session_id']}")
    print(f"Username: {session['username']}")
    print(f"Expires at: {session['expires_at']}")
else:
    print(f"Error: {result['error']}")
```

### 3. Validar y Renovar Sesión

```python
from paquetes.auth import validate_session

# Validar sesión (con renovación automática)
session = validate_session('session-id-aqui', renew=True)

if session:
    print(f"Usuario: {session['username']}")
    print(f"Nueva expiración: {session['expires_at']}")
else:
    print("Sesión inválida o expirada")
```

### 4. Logout

```python
from paquetes.auth import delete_session

# Cerrar sesión
deleted = delete_session('session-id-aqui')
print("Sesión cerrada" if deleted else "Sesión no encontrada")
```

## 🌐 Integración con Frameworks

> 💡 **Ejemplos completos**: Ver [example_auth_flask.py](../tests/auth/example_auth_flask.py) y [example_auth_fastapi.py](../tests/auth/example_auth_fastapi.py) en `paquetes/tests/auth/` para implementaciones completas listas para usar.

### Flask

#### Opción 1: Rutas Automáticas

```python
from flask import Flask
from paquetes.auth import create_flask_auth_routes, ensure_sessions_table

app = Flask(__name__)

# Inicializar tabla
ensure_sessions_table()

# Crear rutas automáticamente
create_flask_auth_routes(app)

# Ahora tienes:
# POST /api/auth/login
# POST /api/auth/logout
# GET /api/auth/session

if __name__ == '__main__':
    app.run()
```

#### Opción 2: Rutas Manuales con Decorador

```python
from flask import Flask, request, jsonify
from paquetes.auth import require_auth, login_user, logout_user

app = Flask(__name__)

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    result = login_user(data['username'], data['password'])

    if result['success']:
        return jsonify(result['session']), 200
    else:
        return jsonify({'error': result['error']}), 401

@app.route('/api/protected')
@require_auth()
def protected_route(session):
    return jsonify({
        'message': 'Acceso permitido',
        'user': session['username']
    })

@app.route('/api/admin')
@require_auth(scopes='admin')
def admin_route(session):
    return jsonify({'message': 'Admin access granted'})

if __name__ == '__main__':
    app.run()
```

**Peticiones con Bearer Token:**

```bash
# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'

# Respuesta:
# {
#   "session_id": "a1b2c3d4-...",
#   "username": "admin",
#   "expires_at": "2026-01-27T09:30:00"
# }

# Acceder a ruta protegida (con Bearer token)
curl http://localhost:5000/api/protected \
  -H "Authorization: Bearer a1b2c3d4-..."

# Logout
curl -X POST http://localhost:5000/api/auth/logout \
  -H "Authorization: Bearer a1b2c3d4-..."
```

**Peticiones con Cookies:**

```bash
# Login (guarda cookie automáticamente)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}' \
  -c cookies.txt

# Acceder a ruta protegida (con cookie)
curl http://localhost:5000/api/protected \
  -b cookies.txt

# Logout (elimina cookie)
curl -X POST http://localhost:5000/api/auth/logout \
  -b cookies.txt -c cookies.txt
```

### FastAPI

#### Opción 1: Rutas Automáticas

```python
from fastapi import FastAPI
from paquetes.auth import create_fastapi_auth_routes, ensure_sessions_table

app = FastAPI()

# Inicializar tabla
ensure_sessions_table()

# Crear rutas automáticamente
create_fastapi_auth_routes(app)

# Ahora tienes:
# POST /api/auth/login
# POST /api/auth/logout
# GET /api/auth/session

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
```

#### Opción 2: Rutas Manuales con Decorador

```python
from fastapi import FastAPI, Request
from paquetes.auth import require_auth, login_user

app = FastAPI()

@app.get('/api/protected')
@require_auth()
async def protected_route(request: Request, session: dict):
    return {
        'message': 'Acceso permitido',
        'user': session['username']
    }

@app.get('/api/admin')
@require_auth(scopes='admin,write:users')
async def admin_route(request: Request, session: dict):
    return {'message': 'Admin access granted'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
```

## 🍪 Autenticación con Cookies

El sistema soporta autenticación mediante cookies HTTP-only, ideal para aplicaciones web SPA (Single Page Applications).

### Configuración en FastAPI

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from paquetes.auth import login_user, logout_user

app = FastAPI()

@app.post('/auth/login')
async def login(username: str, password: str):
    result = login_user(username, password)

    if result['success']:
        # Setear cookie con el session_id
        session_data = result['session']
        json_response = JSONResponse(content=session_data)
        json_response.set_cookie(
            key='Sesion_Auth',
            value=session_data['session_id'],
            path='/',
            httponly=True,        # No accesible desde JavaScript
            samesite='lax',       # Protección CSRF
            secure=False          # Cambiar a True en producción con HTTPS
        )
        return json_response
    else:
        raise HTTPException(status_code=401, detail=result['error'])

@app.post('/auth/logout')
async def logout(request: Request):
    session_id = request.cookies.get('Sesion_Auth')

    if session_id:
        result = logout_user(session_id)
        if result['success']:
            json_response = JSONResponse(content={'message': result['message']})
            json_response.delete_cookie(key='Sesion_Auth', path='/')
            return json_response

    raise HTTPException(status_code=401, detail='No autenticado')
```

### Uso desde el Frontend

```javascript
// Login
const response = await fetch('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',  // ← Importante: enviar/recibir cookies
    body: JSON.stringify({ username: 'admin', password: 'pass123' })
});

// Peticiones protegidas
const data = await fetch('/api/protected', {
    method: 'GET',
    credentials: 'include'  // ← Envía automáticamente la cookie
});

// Logout
await fetch('/auth/logout', {
    method: 'POST',
    credentials: 'include'
});
```

### Ventajas de Cookies HTTP-only

- ✅ **Seguridad XSS**: JavaScript no puede acceder a la cookie
- ✅ **Automático**: El navegador envía la cookie automáticamente
- ✅ **CSRF Protection**: Con `samesite='lax'`
- ✅ **Sin localStorage**: No almacena tokens sensibles en el navegador

### Validación con Cookies

El decorador `@require_auth()` y la función `get_session_from_request()` soportan automáticamente tanto Bearer tokens como cookies:

```python
from paquetes.auth import require_auth

@app.get('/api/protected')
@require_auth()
async def protected_route(request: Request, session: dict):
    # Funciona con:
    # - Header: Authorization: Bearer <token>
    # - Cookie: Sesion_Auth=<token>
    return {'user': session['username']}
```

## 🖥️ Panel de Administración Web

El sistema incluye una interfaz web completa de administración ubicada en `/admin`.

### Características del Panel

- ✅ **Login/Logout**: Interfaz de autenticación con formulario
- ✅ **Dashboard**: Vista de sesiones activas y estadísticas
- ✅ **Gestión de Sesiones**: Lista y administra sesiones activas
- ✅ **Single Page App**: Sin recargas, cambios de estado dinámicos
- ✅ **Responsive**: Funciona en desktop y móvil
- ✅ **Footer Status**: Indicador de estado de conexión en tiempo real

### Estructura del Panel

```
http/admin/
├── index.html           # Página principal (SPA)
├── css/
│   └── styles.css      # Estilos del panel
├── js/
│   └── main.js         # Lógica de la SPA
└── img/                # Recursos (opcional)
```

### Rutas del Panel

- `GET /admin` - Página principal (login si no autenticado, dashboard si autenticado)
- `GET /admin/` - API endpoint (JSON) con estado de autenticación
- `POST /auth/login` - Login del usuario
- `POST /auth/logout` - Logout del usuario
- `GET /auth/session` - Información de sesión actual
- `GET /admin/sessions` - Lista de sesiones (requiere scope: api:admin)

### Configuración del Panel

El panel se configura automáticamente en `main.py`:

```python
from auth_fastapi import create_auth_app
import arch_estaticos

# Crear app con autenticación
app = create_auth_app(
    auth_prefix='/auth',
    admin_prefix='/admin'
)

# Configurar archivos estáticos del panel
arch_estaticos.configure_static_files(app)
```

### Flujo de Autenticación del Panel

1. Usuario accede a `/admin`
2. JavaScript verifica estado con `/auth/session`
3. Si no autenticado: muestra formulario de login
4. Usuario ingresa credenciales
5. POST a `/auth/login` → respuesta incluye cookie `Sesion_Auth`
6. JavaScript detecta login exitoso
7. Elimina formulario del DOM y muestra dashboard
8. Todas las peticiones posteriores incluyen la cookie automáticamente

### Personalización del Panel

Edita los archivos en `http/admin/`:

- **HTML**: `index.html` - Estructura de la página
- **CSS**: `css/styles.css` - Estilos y temas
- **JavaScript**: `js/main.js` - Lógica y funcionalidad

## 📚 API Completa

### Gestión de Sesiones (sessions.py)

| Función | Descripción |
|---------|-------------|
| `ensure_sessions_table()` | Crea tabla USER_SESSIONS si no existe |
| `create_session(username, scopes)` | Crea nueva sesión y retorna session_id |
| `validate_session(session_id, renew)` | Valida sesión y opcionalmente la renueva |
| `delete_session(session_id)` | Elimina una sesión (logout) |
| `delete_user_sessions(username)` | Elimina todas las sesiones de un usuario |
| `cleanup_expired_sessions()` | Elimina sesiones expiradas de la BD |
| `get_active_sessions(username)` | Lista sesiones activas (opcionalmente filtradas por usuario) |

### Middleware (middleware.py)

| Función/Decorador | Descripción |
|-------------------|-------------|
| `@require_auth()` | Decorador para proteger rutas |
| `@require_auth(scopes='admin,write')` | Decorador con validación de permisos |
| `get_session_from_request(request)` | Extrae sesión de request manualmente |

### Endpoints Helpers (endpoints.py)

| Función | Descripción |
|---------|-------------|
| `login_user(username, password, scopes)` | Realiza login y crea sesión |
| `logout_user(session_id)` | Realiza logout |
| `get_session_info(session_id)` | Obtiene info de sesión sin renovarla |
| `create_flask_auth_routes(app)` | Crea rutas automáticas en Flask |
| `create_fastapi_auth_routes(app)` | Crea rutas automáticas en FastAPI |

## 🔄 Sliding Expiration

El sistema renueva automáticamente las sesiones en cada petición:

**Ejemplo:**
- **8:00** → Usuario hace login, sesión expira a las **8:30**
- **8:10** → Usuario hace petición, sesión se renueva, ahora expira a las **8:40**
- **8:35** → Usuario hace petición, sesión se renueva, ahora expira a las **9:05**
- Si no hay actividad por 30 minutos, la sesión expira automáticamente

```python
from paquetes.auth import validate_session

# Validar Y renovar (sliding expiration)
session = validate_session(session_id, renew=True)  # ← Se renueva automáticamente

# Solo validar sin renovar
session = validate_session(session_id, renew=False)
```

## 🔒 Control de Sesiones Activas

El sistema limita automáticamente el número de sesiones activas por usuario. El límite se configura **por usuario** en la tabla `USER` mediante el campo `MaxSessions`.

### Configuración Global (Fallback)

```env
# Máximo de sesiones por defecto (si el usuario no tiene MaxSessions configurado)
SESIONES_ACTIVAS=2
```

### Configuración por Usuario (Recomendado)

El límite se obtiene de la columna `MaxSessions` en la tabla `USER`:

```sql
-- Usuario regular: máximo 2 sesiones
UPDATE [USER] SET MaxSessions = 2 WHERE Username = 'user1';

-- Usuario premium: máximo 5 sesiones
UPDATE [USER] SET MaxSessions = 5 WHERE Username = 'admin';

-- Usuario sin límite (no recomendado)
UPDATE [USER] SET MaxSessions = 999 WHERE Username = 'service_account';
```

**Comportamiento:**
1. Usuario tiene 2 sesiones activas (límite alcanzado según su MaxSessions)
2. Usuario inicia sesión desde un tercer dispositivo
3. El sistema elimina automáticamente **solo** las sesiones más antiguas que exceden el límite
4. Usuario ahora tiene 2 sesiones: la nueva + la más reciente anterior

```python
from paquetes.auth import get_active_sessions

# Ver sesiones activas de un usuario
sessions = get_active_sessions('admin')
for s in sessions:
    print(f"Sesión: {s['session_id']}")
    print(f"Creada: {s['created_at']}")
    print(f"Expira: {s['expires_at']}")
```

## 🎯 Scopes/Permisos

Las sesiones pueden tener permisos granulares:

```python
from paquetes.auth import create_session, require_auth

# Crear sesión con permisos específicos
session = create_session('user', scopes='read:users,read:products')

# Proteger ruta con permisos requeridos
@app.route('/api/admin')
@require_auth(scopes='admin,write:users')
def admin_route(session):
    # Solo usuarios con scopes 'admin' Y 'write:users' pueden acceder
    return {'message': 'Admin access'}
```

**Formato de scopes:**
- Separados por comas: `'read:users,write:users,admin'`
- El decorador valida que la sesión tenga **todos** los scopes requeridos

## 🧹 Limpieza de Sesiones Expiradas

Ejecutar periódicamente (cron job) para limpiar sesiones expiradas:

```python
from paquetes.auth import cleanup_expired_sessions

# Eliminar sesiones expiradas
count = cleanup_expired_sessions()
print(f"Sesiones expiradas eliminadas: {count}")
```

**Cron job (Linux):**

```bash
# Ejecutar cada hora
0 * * * * cd /ruta/proyecto && python3 -c "from paquetes.auth import cleanup_expired_sessions; cleanup_expired_sessions()"
```

## 🔐 Estructura de Tabla USER_SESSIONS

```sql
CREATE TABLE USER_SESSIONS (
    SessionID NVARCHAR(100) PRIMARY KEY,       -- UUID único
    Username NVARCHAR(100) NOT NULL,           -- Usuario propietario
    CreatedAt DATETIME NOT NULL,               -- Fecha de creación
    LastActivity DATETIME NOT NULL,            -- Última actividad (sliding)
    Scopes NVARCHAR(500)                       -- Permisos (opcional)
);

CREATE INDEX idx_username ON USER_SESSIONS(Username);
CREATE INDEX idx_last_activity ON USER_SESSIONS(LastActivity);
```

**Campos:**
- `SessionID`: Identificador único (UUID v4)
- `Username`: Usuario propietario de la sesión
- `CreatedAt`: Fecha de creación de la sesión
- `LastActivity`: Última actividad (se actualiza en cada petición con `renew=True`)
- `Scopes`: Permisos de la sesión (formato: `'scope1,scope2,scope3'`)

## 🔧 Ejemplos Avanzados

### Validar Sesión en Middleware Personalizado

```python
from flask import request, jsonify
from paquetes.auth import validate_session

def custom_auth_middleware():
    """Middleware personalizado para validar sesión."""
    # Obtener header
    auth_header = request.headers.get('Authorization')

    if not auth_header:
        return jsonify({'error': 'No autorizado'}), 401

    # Extraer token
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return jsonify({'error': 'Formato inválido'}), 401

    session_id = parts[1]

    # Validar sesión
    session = validate_session(session_id, renew=True)

    if not session:
        return jsonify({'error': 'Sesión inválida'}), 401

    # Guardar en request para uso posterior
    request.session = session
    return None  # Continuar

@app.before_request
def before_request():
    # Rutas públicas
    if request.path in ['/api/auth/login', '/api/public']:
        return None

    # Validar sesión
    error = custom_auth_middleware()
    if error:
        return error
```

### Cerrar Todas las Sesiones de un Usuario

```python
from paquetes.auth import delete_user_sessions

# Usuario cambia contraseña → cerrar todas sus sesiones
count = delete_user_sessions('admin')
print(f"Cerradas {count} sesiones del usuario 'admin'")
```

### Obtener Info de Sesión Actual

```python
from flask import request
from paquetes.auth import get_session_from_request

@app.route('/api/me')
def current_user():
    # Obtener sesión sin usar decorador
    session = get_session_from_request(request)

    if session:
        return jsonify({
            'username': session['username'],
            'expires_at': session['expires_at'],
            'scopes': session['scopes']
        })
    else:
        return jsonify({'error': 'No autenticado'}), 401
```

## ⚠️ Consideraciones de Seguridad

1. **HTTPS**: Usar HTTPS en producción para proteger tokens en tránsito
2. **Validador seguro**: Usar bcrypt o argon2 para hashes de contraseñas
3. **Timeouts**: Ajustar `JWT_EXPIRATION_MINUTES` según necesidades de seguridad
4. **Limpieza**: Ejecutar `cleanup_expired_sessions()` regularmente
5. **Rate limiting**: Implementar rate limiting en endpoints de login
6. **Logs**: Registrar intentos de login fallidos para detectar ataques

## 📝 Changelog

### v1.1.0 (2026-01-27)
- ✅ Autenticación con cookies HTTP-only
- ✅ Panel de administración web incluido
- ✅ MaxSessions configurable por usuario (campo en BD)
- ✅ Soporte para FastAPI Depends() con get_current_session()
- ✅ Eliminación correcta de sesiones antiguas (solo las que exceden límite)
- ✅ Interfaz SPA con login/logout y gestión de sesiones
- ✅ Footer con indicador de estado de conexión

### v1.0.0 (2026-01-24)
- ✅ Sistema de sesiones con UUID
- ✅ Sliding expiration (renovación automática)
- ✅ Almacenamiento multi-backend (JSON, MSSQL)
- ✅ Límite de sesiones activas por usuario
- ✅ Decoradores para Flask y FastAPI
- ✅ Soporte para scopes/permisos
- ✅ Helpers para login/logout
- ✅ Limpieza de sesiones expiradas
- ✅ Genérico, sin hardcodeo

---

**Versión:** 1.1.0
**Última actualización:** 2026-01-31
