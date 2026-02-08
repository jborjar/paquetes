"""
Implementación de SessionStorage usando JSON.

Almacena sesiones en un archivo JSON. Completamente portable,
no requiere base de datos.
"""
import os
import json
import threading
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path
from .storage import SessionStorage


class JSONSessionStorage(SessionStorage):
    """
    Almacena sesiones en un archivo JSON.

    Portable y simple. Ideal para desarrollo o aplicaciones pequeñas.
    """

    def __init__(self, file_path: str = 'sessions.json'):
        """
        Inicializa el storage JSON.

        Args:
            file_path: Ruta al archivo JSON (default: sessions.json)
        """
        self.file_path = file_path
        self.lock = threading.Lock()  # Para operaciones thread-safe
        self.ensure_table()

    def _read_sessions(self) -> Dict:
        """Lee el archivo de sesiones."""
        if not os.path.exists(self.file_path):
            return {}

        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _write_sessions(self, sessions: Dict):
        """Escribe las sesiones al archivo."""
        # Crear directorio si no existe
        Path(self.file_path).parent.mkdir(parents=True, exist_ok=True)

        with open(self.file_path, 'w') as f:
            json.dump(sessions, f, indent=2, default=str)

    def ensure_table(self):
        """Crea el archivo JSON si no existe."""
        with self.lock:
            if not os.path.exists(self.file_path):
                self._write_sessions({})

    def create_session(
        self,
        session_id: str,
        username: str,
        created_at: datetime,
        last_activity: datetime,
        scopes: Optional[str] = None
    ) -> bool:
        """Crea una nueva sesión."""
        with self.lock:
            sessions = self._read_sessions()
            sessions[session_id] = {
                'session_id': session_id,
                'username': username,
                'created_at': created_at.isoformat(),
                'last_activity': last_activity.isoformat(),
                'scopes': scopes
            }
            self._write_sessions(sessions)
            return True

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Obtiene una sesión por ID."""
        sessions = self._read_sessions()
        session = sessions.get(session_id)

        if session:
            # Convertir strings a datetime
            return {
                **session,
                'created_at': datetime.fromisoformat(session['created_at']),
                'last_activity': datetime.fromisoformat(session['last_activity'])
            }
        return None

    def update_last_activity(self, session_id: str, last_activity: datetime) -> bool:
        """Actualiza el LastActivity de una sesión."""
        with self.lock:
            sessions = self._read_sessions()
            if session_id in sessions:
                sessions[session_id]['last_activity'] = last_activity.isoformat()
                self._write_sessions(sessions)
                return True
            return False

    def delete_session(self, session_id: str) -> bool:
        """Elimina una sesión."""
        with self.lock:
            sessions = self._read_sessions()
            if session_id in sessions:
                del sessions[session_id]
                self._write_sessions(sessions)
                return True
            return False

    def delete_user_sessions(self, username: str) -> int:
        """Elimina todas las sesiones de un usuario."""
        with self.lock:
            sessions = self._read_sessions()
            to_delete = [sid for sid, s in sessions.items() if s['username'] == username]

            for sid in to_delete:
                del sessions[sid]

            if to_delete:
                self._write_sessions(sessions)

            return len(to_delete)

    def get_user_sessions(
        self,
        username: str,
        expiration_minutes: int
    ) -> List[Dict]:
        """Obtiene sesiones activas de un usuario."""
        sessions = self._read_sessions()
        now = datetime.now()
        active_sessions = []

        for session in sessions.values():
            if session['username'] != username:
                continue

            last_activity = datetime.fromisoformat(session['last_activity'])
            age_minutes = (now - last_activity).total_seconds() / 60

            if age_minutes <= expiration_minutes:
                active_sessions.append({
                    **session,
                    'created_at': datetime.fromisoformat(session['created_at']),
                    'last_activity': last_activity
                })

        return active_sessions

    def delete_oldest_session(self, username: str) -> bool:
        """Elimina la sesión más antigua de un usuario."""
        with self.lock:
            sessions = self._read_sessions()
            user_sessions = [
                (sid, s) for sid, s in sessions.items()
                if s['username'] == username
            ]

            if not user_sessions:
                return False

            # Encontrar la más antigua
            oldest = min(user_sessions, key=lambda x: x[1]['last_activity'])
            del sessions[oldest[0]]
            self._write_sessions(sessions)
            return True

    def get_all_active_sessions(
        self,
        expiration_minutes: int,
        username: Optional[str] = None
    ) -> List[Dict]:
        """Obtiene todas las sesiones activas."""
        sessions = self._read_sessions()
        now = datetime.now()
        active_sessions = []

        for session in sessions.values():
            # Filtrar por usuario si se especificó
            if username and session['username'] != username:
                continue

            last_activity = datetime.fromisoformat(session['last_activity'])
            age_minutes = (now - last_activity).total_seconds() / 60

            if age_minutes <= expiration_minutes:
                active_sessions.append({
                    **session,
                    'created_at': datetime.fromisoformat(session['created_at']),
                    'last_activity': last_activity
                })

        return active_sessions

    def cleanup_expired_sessions(self, expiration_minutes: int) -> int:
        """Elimina sesiones expiradas."""
        with self.lock:
            sessions = self._read_sessions()
            now = datetime.now()
            to_delete = []

            for sid, session in sessions.items():
                last_activity = datetime.fromisoformat(session['last_activity'])
                age_minutes = (now - last_activity).total_seconds() / 60

                if age_minutes > expiration_minutes:
                    to_delete.append(sid)

            for sid in to_delete:
                del sessions[sid]

            if to_delete:
                self._write_sessions(sessions)

            return len(to_delete)

    def count_active_sessions(self, username: str, expiration_minutes: int) -> int:
        """Cuenta las sesiones activas de un usuario."""
        sessions = self._read_sessions()
        now = datetime.now()
        count = 0

        for session in sessions.values():
            if session['username'] != username:
                continue

            last_activity = datetime.fromisoformat(session['last_activity'])
            age_minutes = (now - last_activity).total_seconds() / 60

            if age_minutes <= expiration_minutes:
                count += 1

        return count

    def get_oldest_session(self, username: str, expiration_minutes: int) -> Optional[Dict]:
        """Obtiene la sesión más antigua de un usuario."""
        sessions = self._read_sessions()
        now = datetime.now()
        oldest = None

        for session in sessions.values():
            if session['username'] != username:
                continue

            last_activity = datetime.fromisoformat(session['last_activity'])
            age_minutes = (now - last_activity).total_seconds() / 60

            if age_minutes <= expiration_minutes:
                if oldest is None or last_activity < datetime.fromisoformat(oldest['last_activity']):
                    oldest = {
                        **session,
                        'created_at': datetime.fromisoformat(session['created_at']),
                        'last_activity': last_activity
                    }

        return oldest

    def get_all_sessions(self, username: Optional[str] = None) -> List[Dict]:
        """Obtiene todas las sesiones (opcionalmente filtradas por usuario)."""
        sessions = self._read_sessions()
        result = []

        for session in sessions.values():
            # Filtrar por usuario si se especificó
            if username and session['username'] != username:
                continue

            result.append({
                **session,
                'created_at': session['created_at'],
                'last_activity': session['last_activity']
            })

        return result

    def get_user_max_sessions(self, username: str) -> int:
        """
        Obtiene el límite de sesiones activas configurado para un usuario.

        Como JSON no tiene tabla de usuarios, retorna el valor por defecto.

        Args:
            username: Usuario a consultar (no usado en JSON)

        Returns:
            Número máximo de sesiones permitidas (default: 1)
        """
        return 1
