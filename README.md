# ax-audit-platform

AX診断プラットフォーム: 業務棚卸 → AI適性スコアリング → 改善提案・PoCスコープ・概算見積を
1本のフローで自動化する、コンサル営業前段の診断商品。

## 差別化ポイント

1. 診断入力をアンケート＋業務ログで**半自動化**（従来2〜4週間 → 3営業日）
2. 診断結果から**PoCスコープ案と概算見積まで自動生成**
3. **デジタルマーケ5業務（広告運用/レポート作成/入稿/SEO記事/SNS運用）に特化した診断軸を標準搭載**
   — 本業ドメイン知識を診断ロジックに焼き込むことが参入障壁

## ステータス

🟢 **全機能拡張中**（F1業務棚卸 / F2スコアエンジン / F3提案・PoC見積 実装済み）

- [docs/scoring_spec.md](docs/scoring_spec.md) — 4軸スコアの算出式・初期重み・根拠
- `backend/scoring/` — 4軸スコアリング + weights.yaml + デジマ5業務プリセット
- `backend/survey/` — F1 アンケート→業務棚卸(BusinessTask)化
- `backend/proposal/` — F3 提案類型/PoCスコープ/概算工数/期待ROI（**全ROI数値に「想定値」注記**）

```bash
python demo.py          # スコアリング + 提案/PoC見積自動生成
python -m pytest -q     # テスト12件
```

## フォルダ構成

```
backend/{scoring✅, survey✅, proposal✅, api, report, funnel, db}
frontend/{client-app, console-app}          # 未(承認後)
tests/{test_scoring✅, test_proposal_survey✅, test_tenancy, test_disclaimer}
docs/{scoring_spec.md✅, operation_playbook.md}
```
