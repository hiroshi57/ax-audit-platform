# ax-audit-platform

AX診断プラットフォーム: 業務棚卸 → AI適性スコアリング → 改善提案・PoCスコープ・概算見積を
1本のフローで自動化する、コンサル営業前段の診断商品。

## 差別化ポイント

1. 診断入力をアンケート＋業務ログで**半自動化**（従来2〜4週間 → 3営業日）
2. 診断結果から**PoCスコープ案と概算見積まで自動生成**
3. **デジタルマーケ5業務（広告運用/レポート作成/入稿/SEO記事/SNS運用）に特化した診断軸を標準搭載**
   — 本業ドメイン知識を診断ロジックに焼き込むことが参入障壁

## ステータス

🟡 **仕様書ドラフト作成済み・承認待ち**（実装は未着手）

- [docs/scoring_spec.md](docs/scoring_spec.md) — 4軸スコアの算出式・初期重み・根拠

進め方（プロンプト指定）: スコアリング仕様書 → **承認** → 実装（F2スコアエンジン→F1→F3→F4→F5）。
承認後に着手する実装順・成果物は仕様書末尾の未確定事項を確定してから確定する。

## 予定フォルダ構成（実装時）

```
backend/{api,survey,scoring,proposal,report,funnel,db}
frontend/{client-app,console-app}
seed/demo_client/
tests/{test_scoring,test_tenancy,test_disclaimer}
docs/{scoring_spec.md, operation_playbook.md}
```
