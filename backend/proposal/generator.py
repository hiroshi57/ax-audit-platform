"""F3 改善提案 + PoCスコープ + 概算工数 + 期待ROI(想定値) 自動生成.

差別化: PoCスコープと概算見積まで自動生成。全ROI数値に「想定値」注記を必ず付与する。
LLMは提案文の整形にのみ使う想定で、類型・数値はテーブル駆動(再現性)。
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List

from ..scoring.engine import TaskScore
from ..scoring.models import BusinessTask

# ソリューション類型(enum相当。創作しない)
SOLUTION_TYPES = ["業務自動化", "RAG検索", "エージェント", "生成支援"]


def _load_yaml(name: str, default: Dict) -> Dict:
    path = os.path.join(os.path.dirname(__file__), name)
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return default


EFFORT = _load_yaml("effort_table.yaml", {"solution_effort_days": {
    "業務自動化": {"min": 10, "max": 25}, "RAG検索": {"min": 15, "max": 35},
    "エージェント": {"min": 25, "max": 60}, "生成支援": {"min": 8, "max": 20}}})
REDUCTION = _load_yaml("reduction_table.yaml", {"solution_reduction_pct": {
    "業務自動化": 60, "RAG検索": 40, "エージェント": 50, "生成支援": 45},
    "disclaimer": "※削減率は想定値であり実測ではありません。"})


@dataclass
class Proposal:
    task: str
    solution_type: str
    poc_scope: str
    poc_weeks: int
    effort_days_min: int
    effort_days_max: int
    expected_reduction_pct: int
    expected_reduction_note: str      # ★「想定値」注記(必須・非空)
    roi_note: str                     # ★ROI数値への注記(必須・非空)

    def as_dict(self):
        return self.__dict__


def _choose_solution(task: BusinessTask) -> str:
    # 属性から類型を決定(テーブル駆動の分類, 創作しない)
    if task.data_format == "unstructured" or task.decision_type == "non":
        # 非構造・非定型の知識作業 -> 生成支援 or RAG
        return "生成支援" if "記事" in task.name or "レポート" in task.name else "RAG検索"
    if task.routineness >= 4 and task.data_format == "structured":
        return "業務自動化"
    return "エージェント"


class ProposalGenerator:
    def generate(self, task: BusinessTask, score: TaskScore) -> Proposal:
        sol = _choose_solution(task)
        eff = EFFORT["solution_effort_days"][sol]
        reduction = REDUCTION["solution_reduction_pct"][sol]
        disclaimer = REDUCTION.get("disclaimer", "※想定値")
        # PoC 期間: 工数から概算(5人日=1週目安, 4-8週にクランプ)
        weeks = max(4, min(8, round((eff["min"] + eff["max"]) / 2 / 5)))
        return Proposal(
            task=task.name, solution_type=sol,
            poc_scope=f"{task.name}を対象に{sol}を{weeks}週間で試行し、成功指標(処理時間・誤り率)を計測",
            poc_weeks=weeks,
            effort_days_min=eff["min"], effort_days_max=eff["max"],
            expected_reduction_pct=reduction,
            expected_reduction_note=disclaimer,
            roi_note=disclaimer,
        )

    def generate_top(self, tasks: List[BusinessTask], scores: List[TaskScore],
                     n: int = 10) -> List[Proposal]:
        by_name = {t.name: t for t in tasks}
        out = []
        for s in scores[:n]:
            t = by_name.get(s.name)
            if t:
                out.append(self.generate(t, s))
        return out
