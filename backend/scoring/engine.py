"""F2 AI適性スコアリングエンジン(差別化: 再現性のあるルールベース).

4軸(自動化適性/インパクト/実装容易性/リスク)を0-100で算出し、
重み付き合成で優先度スコアと4象限を出す。LLMはスコアに関与しない。
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Dict, List

from .models import BusinessTask

DEFAULT_WEIGHTS = {
    "axes": {
        "automation_fitness": {"routineness": 0.4, "data_availability": 0.35, "decision_simplicity": 0.25},
        "feasibility": {"api": 0.4, "data_format": 0.35, "integrations": 0.25},
        "risk": {"error_tolerance": 0.5, "compliance": 0.5},
    },
    "priority": {"impact": 0.35, "fitness": 0.25, "feasibility": 0.25, "risk": 0.15},
}

_DATA_AVAIL = {"digital": 100.0, "partial": 50.0, "paper": 0.0}
_DECISION = {"routine": 100.0, "semi": 50.0, "non": 0.0}
_API = {"yes": 100.0, "partial": 50.0, "no": 0.0}
_FORMAT = {"structured": 100.0, "semi": 50.0, "unstructured": 0.0}
_ERR_TOL = {"low": 100.0, "mid": 50.0, "high": 0.0}          # 低許容=危険=高スコア
_COMPLIANCE = {"pii": 100.0, "internal": 50.0, "public": 0.0}


def load_weights(path: str = "") -> Dict:
    path = path or os.path.join(os.path.dirname(__file__), "weights.yaml")
    try:
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return DEFAULT_WEIGHTS


@dataclass
class TaskScore:
    name: str
    automation_fitness: float
    impact: float
    feasibility: float
    risk: float
    priority: float
    quadrant: str

    def as_dict(self):
        return {k: (round(v, 1) if isinstance(v, float) else v)
                for k, v in self.__dict__.items()}


def _wavg(values: Dict[str, float], weights: Dict[str, float]) -> float:
    total = sum(weights.values()) or 1.0
    return sum(values[k] * weights[k] for k in weights) / total


class ScoringEngine:
    def __init__(self, weights: Dict = None) -> None:
        self.w = weights or DEFAULT_WEIGHTS

    def _fitness(self, t: BusinessTask) -> float:
        vals = {
            "routineness": (t.routineness - 1) / 4 * 100,
            "data_availability": _DATA_AVAIL.get(t.data_availability, 0.0),
            "decision_simplicity": _DECISION.get(t.decision_type, 0.0),
        }
        return _wavg(vals, self.w["axes"]["automation_fitness"])

    def _feasibility(self, t: BusinessTask) -> float:
        vals = {
            "api": _API.get(t.api_availability, 0.0),
            "data_format": _FORMAT.get(t.data_format, 0.0),
            "integrations": max(0.0, 100 - 20 * (t.num_integrations - 1)),
        }
        return _wavg(vals, self.w["axes"]["feasibility"])

    def _risk(self, t: BusinessTask) -> float:
        vals = {
            "error_tolerance": _ERR_TOL.get(t.error_tolerance, 50.0),
            "compliance": _COMPLIANCE.get(t.compliance_sensitivity, 50.0),
        }
        return _wavg(vals, self.w["axes"]["risk"])

    def score_all(self, tasks: List[BusinessTask]) -> List[TaskScore]:
        if not tasks:
            return []
        # A2 インパクト: log圧縮 -> min-max 正規化(コーパス依存)
        raws = [math.log1p(t.impact_raw()) for t in tasks]
        lo, hi = min(raws), max(raws)
        span = (hi - lo) or 1.0
        pw = self.w["priority"]

        out: List[TaskScore] = []
        for t, raw in zip(tasks, raws):
            impact = (raw - lo) / span * 100
            fitness = self._fitness(t)
            feasibility = self._feasibility(t)
            risk = self._risk(t)
            priority = (pw["impact"] * impact + pw["fitness"] * fitness
                        + pw["feasibility"] * feasibility - pw["risk"] * risk)
            quadrant = self._quadrant(impact, feasibility)
            out.append(TaskScore(t.name, fitness, impact, feasibility, risk, priority, quadrant))
        out.sort(key=lambda s: s.priority, reverse=True)
        return out

    @staticmethod
    def _quadrant(impact: float, feasibility: float, thr: float = 50.0) -> str:
        hi_i, hi_f = impact >= thr, feasibility >= thr
        if hi_i and hi_f:
            return "今すぐPoC"          # 高影響×高容易
        if hi_i and not hi_f:
            return "重点投資"            # 高影響×低容易
        if not hi_i and hi_f:
            return "クイックウィン"      # 低影響×高容易
        return "見送り候補"              # 低影響×低容易


def top_ranking(scores: List[TaskScore], n: int = 10) -> List[TaskScore]:
    return scores[:n]
