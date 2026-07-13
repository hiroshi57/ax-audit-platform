"""AX診断 API(FastAPI). 永続化(SQLite) + 診断実行 + HTMLレポート.

認証は簡易(X-Tenant-Id ヘッダ)。全操作は tenant_id で分離される。
`uvicorn backend.api.main:app --reload`
"""
# 注: FastAPIがcreate_app内ローカル定義のPydanticモデルを解決できるよう、
# ここでは from __future__ import annotations を使わない(注釈を実オブジェクトのまま扱う)。
from datetime import datetime, timezone

from ..db import Database
from ..proposal import ProposalGenerator
from ..report import build_html_report
from ..scoring import ScoringEngine
from ..scoring.models import BusinessTask
from ..survey import from_survey

DB = Database(":memory:")   # 実運用はファイル/PostgreSQLに差し替え
ENGINE = ScoringEngine()
PROPOSER = ProposalGenerator()


def run_diagnosis(tenant_id: str, client_id: int) -> dict:
    """棚卸済みタスクからスコアリング+提案を生成し、診断として保存."""
    tasks = DB.list_tasks(tenant_id, client_id)
    scores = ENGINE.score_all(tasks)
    proposals = PROPOSER.generate_top(tasks, scores)
    now = datetime.now(timezone.utc).isoformat()
    did = DB.save_diagnosis(tenant_id, client_id,
                            [s.as_dict() for s in scores],
                            [p.as_dict() for p in proposals], now)
    return {"diagnosis_id": did, "scores": [s.as_dict() for s in scores],
            "proposals": [p.as_dict() for p in proposals]}


def create_app():  # pragma: no cover - FastAPI経路(テストはTestClientで別途)
    from fastapi import Depends, FastAPI, Header, HTTPException
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel

    app = FastAPI(title="AX Audit Platform", version="1.0.0")

    def tenant(x_tenant_id: str = Header(...)) -> str:
        if not x_tenant_id:
            raise HTTPException(401, "tenant required")
        return x_tenant_id

    class ClientIn(BaseModel):
        company: str

    class SurveyIn(BaseModel):
        client_id: int
        tasks: list[dict]

    @app.post("/v1/clients")
    def create_client(body: ClientIn, t: str = Depends(tenant)):
        return {"client_id": DB.add_client(t, body.company)}

    @app.post("/v1/survey")
    def submit_survey(body: SurveyIn, t: str = Depends(tenant)):
        if DB.get_client(t, body.client_id) is None:
            raise HTTPException(404, "client not found")
        n = 0
        for raw in body.tasks:
            DB.add_task(t, body.client_id, from_survey(raw)); n += 1
        return {"added": n}

    @app.post("/v1/diagnose/{client_id}")
    def diagnose(client_id: int, t: str = Depends(tenant)):
        if DB.get_client(t, client_id) is None:
            raise HTTPException(404, "client not found")
        return run_diagnosis(t, client_id)

    @app.get("/v1/report/{diagnosis_id}", response_class=HTMLResponse)
    def report(diagnosis_id: int, t: str = Depends(tenant)):
        d = DB.get_diagnosis(t, diagnosis_id)
        if d is None:
            raise HTTPException(404, "diagnosis not found")
        client = DB.get_client(t, d["client_id"])
        company = client["company"] if client else "?"
        return build_html_report(company, d["scores"], d["proposals"])

    @app.get("/healthz")
    def healthz():
        return {"status": "ok"}

    return app


try:  # pragma: no cover
    app = create_app()
except Exception:
    app = None
