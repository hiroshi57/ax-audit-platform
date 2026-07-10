import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.scoring import (  # noqa: E402
    BusinessTask, ScoringEngine, marketing_preset_tasks, load_weights, DEFAULT_WEIGHTS,
)


def _tasks():
    return marketing_preset_tasks()


def test_scores_within_bounds():
    scores = ScoringEngine().score_all(_tasks())
    for s in scores:
        for axis in (s.automation_fitness, s.impact, s.feasibility, s.risk):
            assert 0.0 <= axis <= 100.0


def test_ranking_sorted_by_priority():
    scores = ScoringEngine().score_all(_tasks())
    ps = [s.priority for s in scores]
    assert ps == sorted(ps, reverse=True)


def test_weight_change_affects_ranking():
    tasks = _tasks()
    base = ScoringEngine(DEFAULT_WEIGHTS).score_all(tasks)
    base_order = [s.name for s in base]

    # リスク重みを極端に上げると、リスクの高い業務が下がり順位が変わる
    w = copy.deepcopy(DEFAULT_WEIGHTS)
    w["priority"] = {"impact": 0.1, "fitness": 0.1, "feasibility": 0.1, "risk": 0.9}
    changed = ScoringEngine(w).score_all(tasks)
    changed_order = [s.name for s in changed]
    assert base_order != changed_order


def test_quadrant_classification():
    hi = BusinessTask("高影響高容易", routineness=5, data_availability="digital",
                      decision_type="routine", frequency_per_month=100, hours_each=3, num_people=5,
                      api_availability="yes", data_format="structured", num_integrations=1,
                      error_tolerance="high", compliance_sensitivity="public")
    lo = BusinessTask("低影響低容易", routineness=1, data_availability="paper",
                      decision_type="non", frequency_per_month=1, hours_each=0.2, num_people=1,
                      api_availability="no", data_format="unstructured", num_integrations=5,
                      error_tolerance="low", compliance_sensitivity="pii")
    scores = {s.name: s for s in ScoringEngine().score_all([hi, lo])}
    assert scores["高影響高容易"].quadrant == "今すぐPoC"
    assert scores["低影響低容易"].quadrant == "見送り候補"


def test_load_weights_returns_structure():
    w = load_weights()
    assert "axes" in w and "priority" in w
    assert abs(sum(w["priority"].values()) - 1.0) < 1e-6


def test_five_presets_present():
    assert len(marketing_preset_tasks()) == 5
