"""デモ(APIキー不要). スコアリング + 提案/PoC見積自動生成. `python demo.py`"""
from backend.scoring import ScoringEngine, marketing_preset_tasks, load_weights, top_ranking
from backend.proposal import ProposalGenerator


def main():
    tasks = marketing_preset_tasks()
    engine = ScoringEngine(weights=load_weights())
    scores = engine.score_all(tasks)

    print("=== AI適性スコアリング(デジタルマーケ5業務) ===")
    print(f"{'業務':<12}{'優先度':>7}{'影響':>6}{'容易':>6}{'適性':>6}{'リスク':>7}  象限")
    for s in top_ranking(scores):
        print(f"{s.name:<12}{s.priority:>7.1f}{s.impact:>6.0f}{s.feasibility:>6.0f}"
              f"{s.automation_fitness:>6.0f}{s.risk:>7.0f}  {s.quadrant}")

    print("\n=== 改善提案 + PoCスコープ + 概算工数 + 期待ROI(想定値) ===")
    for p in ProposalGenerator().generate_top(tasks, scores, n=3):
        print(f"\n■ {p.task} -> {p.solution_type}")
        print(f"    PoC: {p.poc_scope}")
        print(f"    概算工数: {p.effort_days_min}〜{p.effort_days_max}人日 / "
              f"期待削減率: {p.expected_reduction_pct}% {p.expected_reduction_note}")


if __name__ == "__main__":
    main()
