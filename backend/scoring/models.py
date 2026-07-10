"""業務(評価単位)の入力モデル. アンケート＋文書解析＋LLM分類の結果を保持."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BusinessTask:
    name: str
    # A1 自動化適性
    routineness: int             # 定型度 自己評価 1-5
    data_availability: str       # digital / partial / paper
    decision_type: str           # routine / semi / non
    # A2 インパクト
    frequency_per_month: int
    hours_each: float
    num_people: int
    # A3 実装容易性
    api_availability: str        # yes / partial / no
    data_format: str             # structured / semi / unstructured
    num_integrations: int
    # A4 リスク
    error_tolerance: str         # low(=危険) / mid / high
    compliance_sensitivity: str  # pii / internal / public

    def impact_raw(self) -> float:
        return self.frequency_per_month * self.hours_each * self.num_people
