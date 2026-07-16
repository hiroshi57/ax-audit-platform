import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.benchmark import deviation_score, roi_sensitivity, INDUSTRY_BENCHMARKS  # noqa: E402


def test_deviation_at_mean_is_50():
    mean = INDUSTRY_BENCHMARKS["広告運用"]["mean"]
    assert round(deviation_score("広告運用", mean).deviation) == 50


def test_deviation_above_mean():
    bench = INDUSTRY_BENCHMARKS["広告運用"]
    r = deviation_score("広告運用", bench["mean"] + bench["std"])
    assert round(r.deviation) == 60
    assert "上位" in r.percentile_hint


def test_deviation_unknown_task_uses_default():
    r = deviation_score("未知業務", 50)
    assert round(r.deviation) == 50


def test_roi_sensitivity_bands_ordered():
    s = roi_sensitivity(base_reduction_pct=60, monthly_hours_now=100, band=0.25)
    assert s.worst_pct < s.base_reduction_pct < s.best_pct
    assert s.worst_saved_hours < s.base_saved_hours < s.best_saved_hours
    assert s.base_saved_hours == 60.0


def test_roi_sensitivity_caps_best_at_95():
    s = roi_sensitivity(base_reduction_pct=90, monthly_hours_now=100, band=0.5)
    assert s.best_pct <= 95.0
