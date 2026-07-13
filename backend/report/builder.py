"""F4 診断レポート(HTML). 標準ライブラリのみで生成(ロゴ/配色はCSS変数で差し替え可能).

全ROI/削減率数値に「想定値」注記が付く(受け入れ基準)。
"""
from __future__ import annotations

import html
from typing import Dict, List

_CSS = """
:root{ --brand:#1a5fb4; --bg:#f7f8fa; }
body{ font-family:system-ui,sans-serif; background:var(--bg); color:#1a1a2e; margin:0; padding:24px; }
.wrap{ max-width:820px; margin:0 auto; }
h1{ color:var(--brand); font-size:22px; } h2{ font-size:16px; border-left:4px solid var(--brand); padding-left:8px; }
table{ border-collapse:collapse; width:100%; margin:8px 0; } th,td{ border:1px solid #dde; padding:6px 8px; text-align:left; }
th{ background:#eef2fb; } .note{ color:#a15; font-size:12px; }
.quadrant{ display:inline-block; padding:2px 8px; border-radius:8px; background:#eef2fb; }
"""


def build_html_report(company: str, scores: List[Dict], proposals: List[Dict],
                      disclaimer: str = "※削減率・ROIは想定値であり実測ではありません。") -> str:
    def esc(x):
        return html.escape(str(x))

    rows = "".join(
        f"<tr><td>{esc(s['name'])}</td><td>{esc(round(s['priority'],1))}</td>"
        f"<td>{esc(round(s['impact']))}</td><td>{esc(round(s['feasibility']))}</td>"
        f"<td><span class='quadrant'>{esc(s['quadrant'])}</span></td></tr>"
        for s in scores)

    prop_rows = "".join(
        f"<tr><td>{esc(p['task'])}</td><td>{esc(p['solution_type'])}</td>"
        f"<td>{esc(p['poc_weeks'])}週</td><td>{esc(p['effort_days_min'])}〜{esc(p['effort_days_max'])}人日</td>"
        f"<td>{esc(p['expected_reduction_pct'])}%<div class='note'>{esc(p['expected_reduction_note'])}</div></td></tr>"
        for p in proposals)

    return f"""<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<title>AX診断レポート - {esc(company)}</title><style>{_CSS}</style></head>
<body><div class="wrap">
<h1>AX診断レポート — {esc(company)}</h1>
<p>経営層向けサマリ: AI導入余地の高い業務を優先度順に評価し、PoCスコープと概算見積を提示します。</p>
<h2>優先度ランキング(上位)</h2>
<table><tr><th>業務</th><th>優先度</th><th>影響</th><th>容易性</th><th>象限</th></tr>{rows}</table>
<h2>改善提案 / PoCスコープ / 概算工数</h2>
<table><tr><th>業務</th><th>ソリューション</th><th>PoC期間</th><th>概算工数</th><th>期待削減率</th></tr>{prop_rows}</table>
<p class="note">{esc(disclaimer)}</p>
</div></body></html>"""
