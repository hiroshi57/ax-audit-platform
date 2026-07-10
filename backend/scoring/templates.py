"""デジタルマーケ5業務プリセット(差別化). ベンチマーク初期値つき."""
from __future__ import annotations

from .models import BusinessTask

# 広告運用/レポート作成/入稿/SEO記事制作/SNS運用 のプリセット(ベンチ値)
DIGITAL_MARKETING_PRESETS = {
    "広告運用": BusinessTask("広告運用", routineness=3, data_availability="digital",
                             decision_type="semi", frequency_per_month=60, hours_each=1.0, num_people=3,
                             api_availability="yes", data_format="structured", num_integrations=3,
                             error_tolerance="mid", compliance_sensitivity="internal"),
    "レポート作成": BusinessTask("レポート作成", routineness=5, data_availability="digital",
                               decision_type="routine", frequency_per_month=20, hours_each=2.0, num_people=4,
                               api_availability="yes", data_format="structured", num_integrations=2,
                               error_tolerance="mid", compliance_sensitivity="internal"),
    "入稿": BusinessTask("入稿", routineness=5, data_availability="digital",
                        decision_type="routine", frequency_per_month=40, hours_each=0.5, num_people=2,
                        api_availability="partial", data_format="semi", num_integrations=2,
                        error_tolerance="low", compliance_sensitivity="internal"),
    "SEO記事制作": BusinessTask("SEO記事制作", routineness=2, data_availability="partial",
                              decision_type="non", frequency_per_month=15, hours_each=4.0, num_people=3,
                              api_availability="partial", data_format="unstructured", num_integrations=1,
                              error_tolerance="mid", compliance_sensitivity="public"),
    "SNS運用": BusinessTask("SNS運用", routineness=3, data_availability="digital",
                           decision_type="semi", frequency_per_month=30, hours_each=1.0, num_people=2,
                           api_availability="partial", data_format="semi", num_integrations=2,
                           error_tolerance="mid", compliance_sensitivity="public"),
}


def marketing_preset_tasks():
    return list(DIGITAL_MARKETING_PRESETS.values())
