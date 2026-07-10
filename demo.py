"""デモ(APIキー不要). デジマ5業務のAI適性スコアリング. `python demo.py`"""
from backend.scoring import ScoringEngine, marketing_preset_tasks, load_weights, top_ranking


def main():
    tasks = marketing_preset_tasks()
    engine = ScoringEngine(weights=load_weights())
    scores = engine.score_all(tasks)

    print("=== AI適性スコアリング(デジタルマーケ5業務) ===")
    print(f"{'業務':<12}{'優先度':>7}{'影響':>6}{'容易':>6}{'適性':>6}{'リスク':>7}  象限")
    for s in top_ranking(scores):
        print(f"{s.name:<12}{s.priority:>7.1f}{s.impact:>6.0f}{s.feasibility:>6.0f}"
              f"{s.automation_fitness:>6.0f}{s.risk:>7.0f}  {s.quadrant}")


if __name__ == "__main__":
    main()
