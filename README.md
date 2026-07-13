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

## 本番構成（SQLite + HTMLレポート + Vite 2画面）

- **DB**: `backend/db/`（SQLite・標準ライブラリ）。全クエリ `tenant_id` 強制フィルタで**テナント分離**（越境アクセス不可を自動テスト）
- **API**: `backend/api/main.py`（FastAPI）。clients / survey / diagnose / report(HTML) を提供
- **HTMLレポート**: `backend/report/builder.py`（ロゴ/配色差し替え可、全ROI数値に「想定値」注記、XSSエスケープ）
- **フロント**: `frontend/`（React + Vite）。**クライアント回答**画面＋**コンサル管理**画面の2枚。
  ビルド不要で見たい場合は `frontend/standalone.html` をブラウザで開く
- **CI**: `.github/workflows/ci.yml`（push/PRで pytest 自動実行）

```bash
# バックエンド
uvicorn backend.api.main:app --reload
# フロント(開発)
cd frontend && npm install && npm run dev          # http://localhost:5173
# フロント(ビルド不要デモ)
open frontend/standalone.html
python -m pytest -q                                 # テスト19件(DB/テナント分離/レポート/API E2E含む)
```

## フォルダ構成

```
backend/{scoring✅, survey✅, proposal✅, db✅, report✅, api✅, funnel}
frontend/{index.html, vite.config.js, src/{App,api,screens/*}✅, standalone.html✅}
tests/{test_scoring✅, test_proposal_survey✅, test_db_report_api✅}
.github/workflows/ci.yml✅
docs/{scoring_spec.md✅, operation_playbook.md}
```
