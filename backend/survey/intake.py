"""F1 業務棚卸: アンケート回答 -> BusinessTask への変換(半自動収集の受け口)."""
from __future__ import annotations

from typing import Dict, List

from ..scoring.models import BusinessTask

# アンケート回答(自己評価)-> スコア入力のマッピング既定
_DEFAULTS = dict(routineness=3, data_availability="partial", decision_type="semi",
                 frequency_per_month=20, hours_each=1.0, num_people=2,
                 api_availability="partial", data_format="semi", num_integrations=2,
                 error_tolerance="mid", compliance_sensitivity="internal")


def from_survey(answer: Dict) -> BusinessTask:
    """1業務分のアンケート回答をBusinessTaskに変換(欠損は既定値で補完)."""
    merged = {**_DEFAULTS, **{k: v for k, v in answer.items() if v is not None}}
    return BusinessTask(
        name=answer.get("name", "無名業務"),
        routineness=int(merged["routineness"]),
        data_availability=merged["data_availability"],
        decision_type=merged["decision_type"],
        frequency_per_month=int(merged["frequency_per_month"]),
        hours_each=float(merged["hours_each"]),
        num_people=int(merged["num_people"]),
        api_availability=merged["api_availability"],
        data_format=merged["data_format"],
        num_integrations=int(merged["num_integrations"]),
        error_tolerance=merged["error_tolerance"],
        compliance_sensitivity=merged["compliance_sensitivity"],
    )


def build_inventory(answers: List[Dict]) -> List[BusinessTask]:
    """アンケート回答群 -> 業務棚卸表(BusinessTask のリスト)."""
    return [from_survey(a) for a in answers]
