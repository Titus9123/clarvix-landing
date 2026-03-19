from pathlib import Path
import sqlite3


DB_PATH = Path(__file__).resolve().parent / "clarvix_ops.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS service_requests (
            id TEXT PRIMARY KEY,
            service_type TEXT NOT NULL,
            status TEXT NOT NULL,
            client_name TEXT NOT NULL,
            website_url TEXT,
            business_description TEXT NOT NULL,
            revenue_model TEXT NOT NULL,
            main_concern TEXT NOT NULL,
            input_payload TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS workflow_runs (
            id TEXT PRIMARY KEY,
            request_id TEXT NOT NULL,
            service_type TEXT NOT NULL,
            run_status TEXT NOT NULL,
            run_input TEXT NOT NULL,
            run_output TEXT NOT NULL,
            error_message TEXT,
            started_at TEXT NOT NULL,
            finished_at TEXT,
            FOREIGN KEY(request_id) REFERENCES service_requests(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reports (
            id TEXT PRIMARY KEY,
            request_id TEXT NOT NULL,
            run_id TEXT NOT NULL,
            service_type TEXT NOT NULL,
            report_json TEXT NOT NULL,
            report_markdown TEXT NOT NULL,
            version INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(request_id) REFERENCES service_requests(id),
            FOREIGN KEY(run_id) REFERENCES workflow_runs(id)
        )
        """
    )
    cur.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_reports_run_id_unique
        ON reports(run_id)
        """
    )

    conn.commit()
    conn.close()
