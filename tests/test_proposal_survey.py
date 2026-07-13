import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scoring import ScoringEngine, marketing_preset_tasks  # noqa: E402
from backend.proposal import ProposalGenerator, SOLUTION_TYPES  # noqa: E402
from backend.survey import from_survey, build_inventory  # noqa: E402


# --- F1 業務棚卸 ---
def test_survey_intake_fills_defaults():
    t = from_survey({"name": "請求書処理", "routineness": 5, "data_format": "structured"})
    assert t.name == "請求書処理"
    assert t.routineness == 5
    assert t.data_format == "structured"
    assert t.error_tolerance == "mid"      # 既定値補完


def test_build_inventory():
    inv = build_inventory([{"name": "A"}, {"name": "B", "num_people": 5}])
    assert len(inv) == 2
    assert inv[1].num_people == 5


# --- F3 提案生成 ---
def _scored():
    tasks = marketing_preset_tasks()
    scores = ScoringEngine().score_all(tasks)
    return tasks, scores


def test_proposal_solution_type_from_enum():
    tasks, scores = _scored()
    props = ProposalGenerator().generate_top(tasks, scores)
    assert props
    for p in props:
        assert p.solution_type in SOLUTION_TYPES   # 創作しない(列挙から選択)


def test_all_roi_numbers_have_disclaimer():
    # 受け入れ基準: すべてのROI/削減率数値に「想定値」注記が付く
    tasks, scores = _scored()
    for p in ProposalGenerator().generate_top(tasks, scores):
        assert p.expected_reduction_note and "想定値" in p.expected_reduction_note
        assert p.roi_note and "想定値" in p.roi_note


def test_poc_weeks_in_range():
    tasks, scores = _scored()
    for p in ProposalGenerator().generate_top(tasks, scores):
        assert 4 <= p.poc_weeks <= 8
        assert p.effort_days_min <= p.effort_days_max


def test_seo_article_maps_to_generation_support():
    tasks, scores = _scored()
    props = {p.task: p for p in ProposalGenerator().generate_top(tasks, scores)}
    assert props["SEO記事制作"].solution_type == "生成支援"
