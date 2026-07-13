import React, { useState } from "react";
import ClientSurvey from "./screens/ClientSurvey.jsx";
import ConsultantConsole from "./screens/ConsultantConsole.jsx";
import { createClient, submitSurvey, diagnose, reportUrl } from "./api.js";

const TENANT = "demo-tenant";

export default function App() {
  const [tab, setTab] = useState("survey");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  const runDiagnosis = async (rows) => {
    setBusy(true);
    try {
      const { client_id } = await createClient(TENANT, "デモ株式会社");
      await submitSurvey(TENANT, client_id, rows);
      const diag = await diagnose(TENANT, client_id);
      setResult(diag);
      setTab("console");
    } catch (e) {
      alert("バックエンド未起動の可能性があります: " + e.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="wrap">
      <h1>AX診断プラットフォーム</h1>
      <nav>
        <button onClick={() => setTab("survey")} disabled={tab === "survey"}>クライアント回答</button>
        <button onClick={() => setTab("console")} disabled={tab === "console"}>コンサル管理</button>
        {busy && <span> 診断中...</span>}
      </nav>
      {tab === "survey"
        ? <ClientSurvey onSubmit={runDiagnosis} />
        : <ConsultantConsole result={result} onOpenReport={(id) => window.open(reportUrl(id), "_blank")} />}
    </div>
  );
}
