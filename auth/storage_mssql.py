"""
Implementación de SessionStorage usando MSSQL.

Requiere el paquete paquetes.mssql instalado y configurado.
"""
from typing import Dict, Optional, List, Callable
from datetime import datetime, timedelta
from .storage import SessionStorage


class MSSQLSessionStorage(SessionStorage):
    """
    Almacena sesiones en MSSQL.

    Requiere inyección de la función de conexión.
    """

    def __init__(
        self,
        get_connection: Callable,
        user_table: Optional[str] = None,
        max_sessions_column: Optional[str] = None,
        username_column: Optional[str] = None
    ):
        """
        Inicializa el storage MSSQL.

        Args:
            get_connection: Función que retorna una conexión MSSQL
                           Ejemplo: from paquetes.mssql import get_mssql_connection
            user_table: Nombre de la tabla de usuarios (opcional, para consultar MaxSessions)
            max_sessions_column: Nombre de la columna MaxSessions (opcional)
            username_column: Nombre de la columna de username (opcional)
        """
        self.get_connection = get_connection
        self.user_table = user_table
        self.max_sessions_column = max_sessions_column
        self.username_column = username_column

    def ensure_table(self):
        """Crea la tabla USER_SESSIONS si no existe."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'USER_SESSIONS')
                BEGIN
                    CREATE TABLE USER_SESSIONS (
                        SessionID NVARCHAR(100) PRIMARY KEY,
                        Username NVARCHAR(100) NOT NULL,
                        CreatedAt DATETIME NOT NULL,
                        LastActivity DATETIME NOT NULL,
                        Scopes NVARCHAR(500)
                    );

                    CREATE INDEX idx_username ON USER_SESSIONS(Username);
                    CREATE INDEX idx_last_activity ON USER_SESSIONS(LastActivity);
                END
            """)
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def create_session(
        self,
        session_id: str,
        username: str,
        created_at: datetime,
        last_activity: datetime,
        scopes: Optional[str] = None
    ) -> bool:
        """Crea una nueva sesión."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO USER_SESSIONS (SessionID, Username, CreatedAt, LastActivity, Scopes)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, username, created_at, last_activity, scopes))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            cursor.close()
            conn.close()

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Obtiene una sesión por ID."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT SessionID, Username, CreatedAt, LastActivity, Scopes
                FROM USER_SESSIONS
                WHERE SessionID = ?
            """, (session_id,))

            row = cursor.fetchone()
            if row:
                return {
                    'session_id': row[0],
                    'username': row[1],
                    'created_at': row[2],
                    'last_activity': row[3],
                    'scopes': row[4]
                }
            return None
        finally:
            cursor.close()
            conn.close()

    def update_last_activity(self, session_id: str, last_activity: datetime) -> bool:
        """Actualiza el LastActivity de una sesión."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE USER_SESSIONS
                SET LastActivity = ?
                WHERE SessionID = ?
            """, (last_activity, session_id))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def delete_session(self, session_id: str) -> bool:
        """Elimina una sesión."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM USER_SESSIONS WHERE SessionID = ?", (session_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def delete_user_sessions(self, username: str) -> int:
        """Elimina todas las sesiones de un usuario."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM USER_SESSIONS WHERE Username = ?", (username,))
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()

    def get_user_sessions(
        self,
        username: str,
        expiration_minutes: int
    ) -> List[Dict]:
        """Obtiene sesiones activas de un usuario."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT SessionID, Username, CreatedAt, LastActivity, Scopes
                FROM USER_SESSIONS
                WHERE Username = ?
                    AND DATEADD(MINUTE, ?, LastActivity) > GETDATE()
            """, (username, expiration_minutes))

            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'username': row[1],
                    'created_at': row[2],
                    'last_activity': row[3],
                    'scopes': row[4]
                })
            return sessions
        finally:
            cursor.close()
            conn.close()

    def delete_oldest_session(self, username: str) -> bool:
        """Elimina la sesión más antigua de un usuario."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM USER_SESSIONS
                WHERE SessionID = (
                    SELECT TOP 1 SessionID
                    FROM USER_SESSIONS
                    WHERE Username = ?
                    ORDER BY LastActivity ASC
                )
            """, (username,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            cursor.close()
            conn.close()

    def get_all_active_sessions(
        self,
        expiration_minutes: int,
        username: Optional[str] = None
    ) -> List[Dict]:
        """Obtiene todas las sesiones activas."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if username:
                cursor.execute("""
                    SELECT SessionID, Username, CreatedAt, LastActivity, Scopes
                    FROM USER_SESSIONS
                    WHERE Username = ?
                        AND DATEADD(MINUTE, ?, LastActivity) > GETDATE()
                    ORDER BY LastActivity DESC
                """, (username, expiration_minutes))
            else:
                cursor.execute("""
                    SELECT SessionID, Username, CreatedAt, LastActivity, Scopes
                    FROM USER_SESSIONS
                    WHERE DATEADD(MINUTE, ?, LastActivity) > GETDATE()
                    ORDER BY LastActivity DESC
                """, (expiration_minutes,))

            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'username': row[1],
                    'created_at': row[2],
                    'last_activity': row[3],
                    'scopes': row[4]
                })
            return sessions
        finally:
            cursor.close()
            conn.close()

    def cleanup_expired_sessions(self, expiration_minutes: int) -> int:
        """Elimina sesiones expiradas."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM USER_SESSIONS
                WHERE DATEADD(MINUTE, ?, LastActivity) < GETDATE()
            """, (expiration_minutes,))
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()

    def count_active_sessions(self, username: str, expiration_minutes: int) -> int:
        """Cuenta las sesiones activas de un usuario."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT COUNT(*)
                FROM USER_SESSIONS
                WHERE Username = ?
                    AND DATEADD(MINUTE, ?, LastActivity) > GETDATE()
            """, (username, expiration_minutes))
            row = cursor.fetchone()
            return row[0] if row else 0
        finally:
            cursor.close()
            conn.close()

    def get_oldest_session(self, username: str, expiration_minutes: int) -> Optional[Dict]:
        """Obtiene la sesión más antigua de un usuario."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT TOP 1 SessionID, Username, CreatedAt, LastActivity, Scopes
                FROM USER_SESSIONS
                WHERE Username = ?
                    AND DATEADD(MINUTE, ?, LastActivity) > GETDATE()
                ORDER BY LastActivity ASC
            """, (username, expiration_minutes))

            row = cursor.fetchone()
            if row:
                return {
                    'session_id': row[0],
                    'username': row[1],
                    'created_at': row[2],
                    'last_activity': row[3],
                    'scopes': row[4]
                }
            return None
        finally:
            cursor.close()
            conn.close()

    def get_all_sessions(self, username: Optional[str] = None) -> List[Dict]:
        """Obtiene todas las sesiones (opcionalmente filtradas por usuario)."""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            if username:
                cursor.execute("""
                    SELECT SessionID, Username, CreatedAt, LastActivity, Scopes
                    FROM USER_SESSIONS
                    WHERE Username = ?
                    ORDER BY LastActivity DESC
                """, (username,))
            else:
                cursor.execute("""
                    SELECT SessionID, Username, CreatedAt, LastActivity, Scopes
                    FROM USER_SESSIONS
                    ORDER BY LastActivity DESC
                """)

            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    'session_id': row[0],
                    'username': row[1],
                    'created_at': row[2].isoformat() if hasattr(row[2], 'isoformat') else str(row[2]),
                    'last_activity': row[3].isoformat() if hasattr(row[3], 'isoformat') else str(row[3]),
                    'scopes': row[4]
                })
            return sessions
        finally:
            cursor.close()
            conn.close()

    def get_user_max_sessions(self, username: str) -> int:
        """
        Obtiene el límite de sesiones activas configurado para un usuario.

        Si se configuró user_table, consulta la base de datos.
        Si no, usa la variable de entorno DEFAULT_MAX_SESSIONS (default: 1).

        Args:
            username: Usuario a consultar

        Returns:
            Número máximo de sesiones permitidas
        """
        import os

        # Si no se configuró tabla de usuarios, usar valor por defecto
        if not self.user_table or not self.max_sessions_column or not self.username_column:
            return int(os.getenv('DEFAULT_MAX_SESSIONS', '1'))

        # Consultar la base de datos
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            query = f"""
                SELECT {self.max_sessions_column}
                FROM {self.user_table}
                WHERE {self.username_column} = ?
            """
            cursor.execute(query, (username,))

            row = cursor.fetchone()
            if row and row[0] is not None:
                return row[0]
            return int(os.getenv('DEFAULT_MAX_SESSIONS', '1'))
        finally:
            cursor.close()
            conn.close()
