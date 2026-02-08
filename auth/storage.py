"""
Capa de abstracción para almacenamiento de sesiones.

Permite usar diferentes backends: JSON, MSSQL, PostgreSQL, Redis, etc.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from datetime import datetime


class SessionStorage(ABC):
    """
    Interfaz abstracta para almacenamiento de sesiones.

    Cualquier backend debe implementar estos métodos.
    """

    @abstractmethod
    def ensure_table(self):
        """Crea la tabla/estructura si no existe."""
        pass

    @abstractmethod
    def create_session(
        self,
        session_id: str,
        username: str,
        created_at: datetime,
        last_activity: datetime,
        scopes: Optional[str] = None
    ) -> bool:
        """
        Crea una nueva sesión.

        Returns:
            True si se creó exitosamente, False en caso contrario
        """
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Obtiene una sesión por ID.

        Returns:
            Dict con datos de la sesión o None si no existe
        """
        pass

    @abstractmethod
    def update_last_activity(self, session_id: str, last_activity: datetime) -> bool:
        """
        Actualiza el LastActivity de una sesión.

        Returns:
            True si se actualizó, False si no existe
        """
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """
        Elimina una sesión.

        Returns:
            True si se eliminó, False si no existía
        """
        pass

    @abstractmethod
    def delete_user_sessions(self, username: str) -> int:
        """
        Elimina todas las sesiones de un usuario.

        Returns:
            Número de sesiones eliminadas
        """
        pass

    @abstractmethod
    def get_user_sessions(
        self,
        username: str,
        expiration_minutes: int
    ) -> List[Dict]:
        """
        Obtiene sesiones activas de un usuario.

        Args:
            username: Usuario a consultar
            expiration_minutes: Minutos para considerar sesión activa

        Returns:
            Lista de sesiones activas
        """
        pass

    @abstractmethod
    def delete_oldest_session(self, username: str) -> bool:
        """
        Elimina la sesión más antigua de un usuario.

        Returns:
            True si se eliminó alguna
        """
        pass

    @abstractmethod
    def get_all_active_sessions(
        self,
        expiration_minutes: int,
        username: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtiene todas las sesiones activas.

        Args:
            expiration_minutes: Minutos para considerar sesión activa
            username: Filtrar por usuario (opcional)

        Returns:
            Lista de sesiones activas
        """
        pass

    @abstractmethod
    def cleanup_expired_sessions(self, expiration_minutes: int) -> int:
        """
        Elimina sesiones expiradas.

        Returns:
            Número de sesiones eliminadas
        """
        pass

    @abstractmethod
    def count_active_sessions(self, username: str, expiration_minutes: int) -> int:
        """
        Cuenta las sesiones activas de un usuario.

        Args:
            username: Usuario a consultar
            expiration_minutes: Minutos para considerar sesión activa

        Returns:
            Número de sesiones activas
        """
        pass

    @abstractmethod
    def get_oldest_session(self, username: str, expiration_minutes: int) -> Optional[Dict]:
        """
        Obtiene la sesión más antigua de un usuario.

        Args:
            username: Usuario a consultar
            expiration_minutes: Minutos para considerar sesión activa

        Returns:
            Dict con datos de la sesión más antigua o None
        """
        pass

    @abstractmethod
    def get_all_sessions(self, username: Optional[str] = None) -> List[Dict]:
        """
        Obtiene todas las sesiones (opcionalmente filtradas por usuario).

        Args:
            username: Filtrar por usuario (opcional)

        Returns:
            Lista de todas las sesiones
        """
        pass

    @abstractmethod
    def get_user_max_sessions(self, username: str) -> int:
        """
        Obtiene el límite de sesiones activas configurado para un usuario.

        Args:
            username: Usuario a consultar

        Returns:
            Número máximo de sesiones permitidas (default: 1 si no se encuentra)
        """
        pass
