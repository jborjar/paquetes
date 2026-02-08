"""
Autenticación para SAP Business One Service Layer.

Gestiona el login, logout y sesiones con Service Layer.
"""
import os
import requests
from typing import Dict, Optional
from datetime import datetime, timedelta
import urllib3

# Deshabilitar warnings SSL (Service Layer usa certificados auto-firmados)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Caché global de sesión (evita login múltiple en misma ejecución)
_session_cache = {
    'session_id': None,
    'route_id': None,
    'expires_at': None,
    'base_url': None
}


def _get_credentials() -> Dict[str, str]:
    """
    Obtiene las credenciales desde variables de entorno.

    Returns:
        Dict con url, user, password, company_db

    Raises:
        ValueError: Si faltan variables de entorno
    """
    url = os.getenv('SAP_B1_SERVICE_LAYER_URL')
    user = os.getenv('SAP_B1_USER')
    password = os.getenv('SAP_B1_PASSWORD')
    company_db = os.getenv('SAP_B1_COMPANY_DB', '')  # Opcional

    if not url:
        raise ValueError(
            "SAP_B1_SERVICE_LAYER_URL no está configurado en variables de entorno"
        )
    if not user:
        raise ValueError(
            "SAP_B1_USER no está configurado en variables de entorno"
        )
    if not password:
        raise ValueError(
            "SAP_B1_PASSWORD no está configurado en variables de entorno"
        )

    return {
        'url': url.rstrip('/'),  # Remover / final si existe
        'user': user,
        'password': password,
        'company_db': company_db
    }


def login(
    url: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    company_db: Optional[str] = None,
    force_new: bool = False
) -> Dict[str, str]:
    """
    Inicia sesión en SAP Business One Service Layer.

    Args:
        url: URL base del Service Layer (ej: https://server:50000/b1s/v1)
             Si es None, usa SAP_B1_SERVICE_LAYER_URL de .env
        user: Usuario de SAP B1. Si es None, usa SAP_B1_USER de .env
        password: Contraseña. Si es None, usa SAP_B1_PASSWORD de .env
        company_db: Base de datos de la compañía (opcional)
        force_new: Si True, fuerza un nuevo login aunque haya sesión activa

    Returns:
        Dict con 'session_id', 'route_id', 'expires_at'

    Raises:
        requests.exceptions.RequestException: Si falla la conexión
        ValueError: Si las credenciales son inválidas

    Example:
        >>> session = login()
        >>> print(session['session_id'])
        >>>
        >>> # Con parámetros explícitos
        >>> session = login(
        ...     url='https://server:50000/b1s/v1',
        ...     user='manager',
        ...     password='pass123'
        ... )
    """
    global _session_cache

    # Si hay sesión activa y no se fuerza nuevo login, retornar caché
    if not force_new and is_session_active():
        return {
            'session_id': _session_cache['session_id'],
            'route_id': _session_cache['route_id'],
            'expires_at': _session_cache['expires_at']
        }

    # Obtener credenciales (parámetros o env vars)
    if url is None or user is None or password is None:
        creds = _get_credentials()
        url = url or creds['url']
        user = user or creds['user']
        password = password or creds['password']
        company_db = company_db or creds['company_db']

    # Preparar payload de login
    login_url = f"{url}/Login"
    payload = {
        'UserName': user,
        'Password': password
    }

    # Agregar CompanyDB si está especificado
    if company_db:
        payload['CompanyDB'] = company_db

    # Realizar login
    try:
        response = requests.post(
            login_url,
            json=payload,
            verify=False,  # Service Layer usa certificados auto-firmados
            timeout=30
        )
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise ValueError(
                f"Credenciales inválidas para usuario '{user}'"
            )
        raise

    # Extraer cookies de sesión
    session_id = response.cookies.get('B1SESSION')
    route_id = response.cookies.get('ROUTEID')

    if not session_id:
        raise ValueError(
            "Service Layer no retornó B1SESSION. Verifique configuración."
        )

    # Calcular expiración (Service Layer: 30 minutos por defecto)
    expires_at = datetime.now() + timedelta(minutes=25)  # 5 min de margen

    # Guardar en caché
    _session_cache['session_id'] = session_id
    _session_cache['route_id'] = route_id
    _session_cache['expires_at'] = expires_at
    _session_cache['base_url'] = url

    return {
        'session_id': session_id,
        'route_id': route_id,
        'expires_at': expires_at
    }


def logout(
    session_id: Optional[str] = None,
    url: Optional[str] = None
) -> bool:
    """
    Cierra sesión en SAP Business One Service Layer.

    Args:
        session_id: ID de sesión. Si es None, usa la sesión en caché
        url: URL base del Service Layer. Si es None, usa la URL en caché

    Returns:
        True si el logout fue exitoso

    Example:
        >>> logout()
        True
    """
    global _session_cache

    # Usar sesión en caché si no se especifica
    if session_id is None:
        session_id = _session_cache.get('session_id')
    if url is None:
        url = _session_cache.get('base_url')

    if not session_id or not url:
        # No hay sesión activa
        return True

    # Realizar logout
    logout_url = f"{url}/Logout"
    cookies = {
        'B1SESSION': session_id
    }

    if _session_cache.get('route_id'):
        cookies['ROUTEID'] = _session_cache['route_id']

    try:
        response = requests.post(
            logout_url,
            cookies=cookies,
            verify=False,
            timeout=10
        )
        response.raise_for_status()
    except:
        # Ignorar errores de logout (sesión puede estar expirada)
        pass

    # Limpiar caché
    _session_cache['session_id'] = None
    _session_cache['route_id'] = None
    _session_cache['expires_at'] = None
    _session_cache['base_url'] = None

    return True


def get_session(
    url: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    company_db: Optional[str] = None
) -> Dict[str, str]:
    """
    Obtiene una sesión activa (reutiliza caché o crea nueva).

    Esta es la función recomendada para usar en otras funciones del módulo.
    Gestiona automáticamente renovación de sesión expirada.

    Args:
        url: URL base del Service Layer (opcional)
        user: Usuario (opcional)
        password: Contraseña (opcional)
        company_db: Base de datos de la compañía (opcional)

    Returns:
        Dict con session_id, route_id, base_url

    Example:
        >>> session = get_session()
        >>> cookies = {'B1SESSION': session['session_id']}
    """
    # Verificar si hay sesión activa
    if is_session_active():
        return {
            'session_id': _session_cache['session_id'],
            'route_id': _session_cache['route_id'],
            'base_url': _session_cache['base_url']
        }

    # No hay sesión o está expirada, hacer login
    session_info = login(url, user, password, company_db)

    return {
        'session_id': session_info['session_id'],
        'route_id': session_info['route_id'],
        'base_url': _session_cache['base_url']
    }


def is_session_active() -> bool:
    """
    Verifica si hay una sesión activa y no expirada.

    Returns:
        True si hay sesión activa

    Example:
        >>> if is_session_active():
        ...     print("Sesión activa")
    """
    if not _session_cache.get('session_id'):
        return False

    if not _session_cache.get('expires_at'):
        return False

    # Verificar si no ha expirado
    return datetime.now() < _session_cache['expires_at']
