import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

from backend.db import Database  # noqa: E402
from backend.report import build_html_report  # noqa: E402
from backend.scoring import marketing_preset_tasks, ScoringEngine  # noqa: E402
from backend.proposal import ProposalGenerator  # noqa: E402


def _db_with_client(tenant="tenant-a", company="ACME"):
    db = Database(":memory:")
    cid = db.add_client(tenant, company)
    return db, cid


# --- DB: 永続化 + テナント分離 ---
def test_task_roundtrip():
    db, cid = _db_with_client()
    tasks = marketing_preset_tasks()
    for t in tasks:
        db.add_task("tenant-a", cid, t)
    loaded = db.list_tasks("tenant-a", cid)
    assert len(loaded) == len(tasks)
    assert loaded[0].name == tasks[0].name


def test_tenant_cannot_read_other_tenants_client():
    db, cid = _db_with_client(tenant="tenant-a")
    # tenant-b から tenant-a のクライアントは見えない(越境不可)
    assert db.get_client("tenant-b", cid) is None
    assert db.get_client("tenant-a", cid) is not None


def test_tenant_cannot_read_other_tenants_diagnosis():
    db, cid = _db_with_client(tenant="tenant-a")
    did = db.save_diagnosis("tenant-a", cid, [{"name": "x"}], [{"task": "x"}], "2026-07-09")
    assert db.get_diagnosis("tenant-b", did) is None    # 越境不可
    assert db.get_diagnosis("tenant-a", did) is not None


def test_list_tasks_isolated_by_tenant():
    db, cid_a = _db_with_client(tenant="tenant-a")
    db.add_task("tenant-a", cid_a, marketing_preset_tasks()[0])
    # 別テナントの同一client_idを問い合わせても取れない
    assert db.list_tasks("tenant-b", cid_a) == []


# --- HTMLレポート ---
def _scored_proposals():
    tasks = marketing_preset_tasks()
    scores = ScoringEngine().score_all(tasks)
    props = ProposalGenerator().generate_top(tasks, scores)
    return [s.as_dict() for s in scores], [p.as_dict() for p in props]


def test_html_report_contains_key_sections_and_disclaimer():
    scores, props = _scored_proposals()
    html = build_html_report("ACME", scores, props)
    assert "<html" in html and "AX診断レポート" in html
    assert "ACME" in html
    assert "優先度ランキング" in html and "改善提案" in html
    assert "想定値" in html            # ROI注記(受け入れ基準)


def test_html_report_escapes_company_name():
    scores, props = _scored_proposals()
    html = build_html_report("<script>x</script>", scores, props)
    assert "<script>x</script>" not in html   # エスケープされる
    assert "&lt;script&gt;" in html


# --- API(FastAPI TestClient) ---
def test_api_end_to_end_and_tenant_isolation():
    pytest.importorskip("fastapi")
    httpx = pytest.importorskip("httpx")  # noqa: F841
    from fastapi.testclient import TestClient
    from backend.api.main import create_app

    client = TestClient(create_app())
    ha = {"X-Tenant-Id": "tenant-a"}
    hb = {"X-Tenant-Id": "tenant-b"}

    cid = client.post("/v1/clients", json={"company": "ACME"}, headers=ha).json()["client_id"]
    survey = {"client_id": cid, "tasks": [
        {"name": "広告運用", "routineness": 3, "data_availability": "digital",
         "decision_type": "semi", "frequency_per_month": 60, "hours_each": 1,
         "num_people": 3, "api_availability": "yes", "data_format": "structured",
         "num_integrations": 3, "error_tolerance": "mid", "compliance_sensitivity": "internal"}]}
    assert client.post("/v1/survey", json=survey, headers=ha).json()["added"] == 1

    diag = client.post(f"/v1/diagnose/{cid}", headers=ha).json()
    assert diag["scores"] and diag["proposals"]
    did = diag["diagnosis_id"]

    # 別テナントは診断レポートを参照できない
    assert client.get(f"/v1/report/{did}", headers=hb).status_code == 404
    r = client.get(f"/v1/report/{did}", headers=ha)
    assert r.status_code == 200 and "AX診断レポート" in r.text
