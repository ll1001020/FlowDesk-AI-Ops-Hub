import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Iterator, List, Optional

from app.schemas import Ticket


def _db_path(database_url: str) -> str:
    if database_url.startswith("sqlite:///"):
        return database_url.replace("sqlite:///", "", 1)
    return database_url


class TicketStore:
    def __init__(self, database_url: str):
        self.path = _db_path(database_url)
        db_file = Path(self.path)
        if db_file.parent and str(db_file.parent) != ".":
            db_file.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init_db(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    scenario TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    status TEXT NOT NULL,
                    owner_team TEXT NOT NULL,
                    ai_summary TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def create_ticket(self, *, title: str, description: str, scenario: str, severity: str, owner_team: str, ai_summary: str) -> Ticket:
        created_at = datetime.utcnow().isoformat()
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO tickets (title, description, scenario, severity, status, owner_team, ai_summary, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (title, description, scenario, severity, "open", owner_team, ai_summary, created_at),
            )
            ticket_id = int(cur.lastrowid)
        return self.get_ticket(ticket_id)  # type: ignore[return-value]

    def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return self._row_to_ticket(row) if row else None

    def list_tickets(self, limit: int = 50) -> List[Ticket]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM tickets ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [self._row_to_ticket(row) for row in rows]

    def update_status(self, ticket_id: int, status: str) -> Optional[Ticket]:
        with self.connect() as conn:
            conn.execute("UPDATE tickets SET status = ? WHERE id = ?", (status, ticket_id))
        return self.get_ticket(ticket_id)

    @staticmethod
    def _row_to_ticket(row: sqlite3.Row) -> Ticket:
        return Ticket(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            scenario=row["scenario"],
            severity=row["severity"],
            status=row["status"],
            owner_team=row["owner_team"],
            ai_summary=row["ai_summary"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
