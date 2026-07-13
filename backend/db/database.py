"""永続化層(SQLite, 標準ライブラリ). テナント分離を強制する.

全クエリは tenant_id で必ずフィルタする。越境アクセス(他テナントのデータ参照)は
返さない(受け入れ基準: tenant_id 強制フィルタ + 越境アクセスの自動テスト)。
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from typing import Dict, List, Optional

from ..scoring.models import BusinessTask

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    company TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS business_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    client_id INTEGER NOT NULL,
    payload TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS diagnoses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id TEXT NOT NULL,
    client_id INTEGER NOT NULL,
    scores TEXT NOT NULL,
    proposals TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


class Database:
    def __init__(self, path: str = ":memory:") -> None:
        # Web(スレッドプール)から使うため check_same_thread=False。
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # --- clients ---
    def add_client(self, tenant_id: str, company: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO clients(tenant_id, company) VALUES (?, ?)", (tenant_id, company))
        self.conn.commit()
        return cur.lastrowid

    def get_client(self, tenant_id: str, client_id: int) -> Optional[Dict]:
        row = self.conn.execute(
            "SELECT id, company FROM clients WHERE id=? AND tenant_id=?",
            (client_id, tenant_id)).fetchone()
        return dict(row) if row else None   # 他テナントなら None(越境不可)

    # --- business tasks ---
    def add_task(self, tenant_id: str, client_id: int, task: BusinessTask) -> int:
        cur = self.conn.execute(
            "INSERT INTO business_tasks(tenant_id, client_id, payload) VALUES (?, ?, ?)",
            (tenant_id, client_id, json.dumps(asdict(task), ensure_ascii=False)))
        self.conn.commit()
        return cur.lastrowid

    def list_tasks(self, tenant_id: str, client_id: int) -> List[BusinessTask]:
        rows = self.conn.execute(
            "SELECT payload FROM business_tasks WHERE tenant_id=? AND client_id=?",
            (tenant_id, client_id)).fetchall()
        return [BusinessTask(**json.loads(r["payload"])) for r in rows]

    # --- diagnoses ---
    def save_diagnosis(self, tenant_id: str, client_id: int,
                       scores: List[Dict], proposals: List[Dict], created_at: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO diagnoses(tenant_id, client_id, scores, proposals, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (tenant_id, client_id, json.dumps(scores, ensure_ascii=False),
             json.dumps(proposals, ensure_ascii=False), created_at))
        self.conn.commit()
        return cur.lastrowid

    def get_diagnosis(self, tenant_id: str, diagnosis_id: int) -> Optional[Dict]:
        row = self.conn.execute(
            "SELECT id, client_id, scores, proposals, created_at FROM diagnoses "
            "WHERE id=? AND tenant_id=?", (diagnosis_id, tenant_id)).fetchone()
        if not row:
            return None    # 他テナントの診断は参照不可
        return {"id": row["id"], "client_id": row["client_id"],
                "scores": json.loads(row["scores"]), "proposals": json.loads(row["proposals"]),
                "created_at": row["created_at"]}

    def close(self) -> None:
        self.conn.close()
