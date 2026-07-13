import React from "react";

// コンサル管理画面: 優先度ランキング + 提案 + レポートリンク。
export default function ConsultantConsole({ result, onOpenReport }) {
  if (!result) return <div className="card">診断結果はまだありません。</div>;
  const { scores, proposals } = result;
  return (
    <div className="card">
      <h2>優先度ランキング</h2>
      <table>
        <thead><tr><th>業務</th><th>優先度</th><th>影響</th><th>容易性</th><th>象限</th></tr></thead>
        <tbody>
          {scores.map((s) => (
            <tr key={s.name}>
              <td>{s.name}</td><td>{s.priority.toFixed(1)}</td>
              <td>{Math.round(s.impact)}</td><td>{Math.round(s.feasibility)}</td>
              <td><span className="quadrant">{s.quadrant}</span></td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>改善提案 / PoC見積</h2>
      <table>
        <thead><tr><th>業務</th><th>ソリューション</th><th>PoC</th><th>工数</th><th>期待削減率</th></tr></thead>
        <tbody>
          {proposals.map((p) => (
            <tr key={p.task}>
              <td>{p.task}</td><td>{p.solution_type}</td><td>{p.poc_weeks}週</td>
              <td>{p.effort_days_min}〜{p.effort_days_max}人日</td>
              <td>{p.expected_reduction_pct}%<div className="note">{p.expected_reduction_note}</div></td>
            </tr>
          ))}
        </tbody>
      </table>

      {result.diagnosis_id && (
        <button className="primary" onClick={() => onOpenReport(result.diagnosis_id)}>
          HTMLレポートを開く
        </button>
      )}
    </div>
  );
}
