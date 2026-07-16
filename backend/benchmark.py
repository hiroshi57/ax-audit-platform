"""業界ベンチマーク偏差値 + ROI感度分析(尖った武器).

診断を「絶対スコア」でなく「業界内での相対位置(偏差値)」で語り、
ROIは単一値でなく worst/base/best の幅で提示する(過大主張の回避 + 説得力)。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

# デジマ5業務の業界ベンチ(優先度スコアの平均・標準偏差。社内実績想定値)
INDUSTRY_BENCHMARKS: Dict[str, Dict[str, float]] = {
    "広告運用": {"mean": 62.0, "std": 12.0},
    "レポート作成": {"mean": 70.0, "std": 10.0},
    "入稿": {"mean": 40.0, "std": 15.0},
    "SEO記事制作": {"mean": 48.0, "std": 14.0},
    "SNS運用": {"mean": 45.0, "std": 13.0},
}


@dataclass
class DeviationResult:
    task: str
    priority: float
    industry_mean: float
    deviation: float          # 偏差値(50=平均, 60=上位約16%)
    percentile_hint: str

    def as_dict(self):
        return {"task": self.task, "priority": round(self.priority, 1),
                "industry_mean": self.industry_mean, "deviation": round(self.deviation, 1),
                "percentile_hint": self.percentile_hint}


def _pct_hint(dev: float) -> str:
    if dev >= 70:
        return "上位約2%"
    if dev >= 60:
        return "上位約16%"
    if dev >= 50:
        return "平均以上"
    if dev >= 40:
        return "平均以下"
    return "下位約16%"


def deviation_score(task: str, priority: float) -> DeviationResult:
    bench = INDUSTRY_BENCHMARKS.get(task, {"mean": 50.0, "std": 15.0})
    std = bench["std"] or 1.0
    dev = 50 + 10 * (priority - bench["mean"]) / std
    return DeviationResult(task=task, priority=priority, industry_mean=bench["mean"],
                           deviation=dev, percentile_hint=_pct_hint(dev))


@dataclass
class RoiSensitivity:
    base_reduction_pct: float
    worst_pct: float
    best_pct: float
    monthly_hours_now: float
    worst_saved_hours: float
    base_saved_hours: float
    best_saved_hours: float

    def as_dict(self):
        return {k: round(v, 1) for k, v in self.__dict__.items()}


def roi_sensitivity(base_reduction_pct: float, monthly_hours_now: float,
                    band: float = 0.25) -> RoiSensitivity:
    """削減率に±band(既定25%)の不確実性を見込み、削減時間の幅を出す."""
    worst = base_reduction_pct * (1 - band)
    best = min(95.0, base_reduction_pct * (1 + band))
    return RoiSensitivity(
        base_reduction_pct=base_reduction_pct, worst_pct=worst, best_pct=best,
        monthly_hours_now=monthly_hours_now,
        worst_saved_hours=monthly_hours_now * worst / 100,
        base_saved_hours=monthly_hours_now * base_reduction_pct / 100,
        best_saved_hours=monthly_hours_now * best / 100)
