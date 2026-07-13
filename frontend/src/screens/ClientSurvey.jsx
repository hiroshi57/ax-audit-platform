import React, { useState } from "react";

// クライアント回答画面: 業務のアンケート入力(部署別・15分想定の簡易版)。
const EMPTY = {
  name: "", routineness: 3, data_availability: "digital", decision_type: "semi",
  frequency_per_month: 20, hours_each: 1, num_people: 2,
  api_availability: "partial", data_format: "semi", num_integrations: 2,
  error_tolerance: "mid", compliance_sensitivity: "internal",
};

export default function ClientSurvey({ onSubmit }) {
  const [rows, setRows] = useState([{ ...EMPTY, name: "広告レポート作成" }]);

  const update = (i, key, val) =>
    setRows(rows.map((r, j) => (j === i ? { ...r, [key]: val } : r)));
  const addRow = () => setRows([...rows, { ...EMPTY }]);

  return (
    <div className="card">
      <h2>業務棚卸アンケート</h2>
      {rows.map((r, i) => (
        <div key={i} className="row">
          <input placeholder="業務名" value={r.name}
            onChange={(e) => update(i, "name", e.target.value)} />
          <label>定型度
            <input type="range" min="1" max="5" value={r.routineness}
              onChange={(e) => update(i, "routineness", Number(e.target.value))} />
          </label>
          <label>頻度/月
            <input type="number" value={r.frequency_per_month}
              onChange={(e) => update(i, "frequency_per_month", Number(e.target.value))} />
          </label>
        </div>
      ))}
      <button onClick={addRow}>＋業務を追加</button>
      <button className="primary" onClick={() => onSubmit(rows)}>診断を実行</button>
    </div>
  );
}
