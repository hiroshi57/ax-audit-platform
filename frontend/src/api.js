// バックエンドAPIクライアント. X-Tenant-Id でテナント分離。
const BASE = import.meta.env?.VITE_API || "http://localhost:8000";

function headers(tenant) {
  return { "Content-Type": "application/json", "X-Tenant-Id": tenant };
}

export async function createClient(tenant, company) {
  const r = await fetch(`${BASE}/v1/clients`, {
    method: "POST", headers: headers(tenant), body: JSON.stringify({ company }),
  });
  return r.json();
}

export async function submitSurvey(tenant, clientId, tasks) {
  const r = await fetch(`${BASE}/v1/survey`, {
    method: "POST", headers: headers(tenant),
    body: JSON.stringify({ client_id: clientId, tasks }),
  });
  return r.json();
}

export async function diagnose(tenant, clientId) {
  const r = await fetch(`${BASE}/v1/diagnose/${clientId}`, {
    method: "POST", headers: headers(tenant),
  });
  return r.json();
}

export function reportUrl(diagnosisId) {
  return `${BASE}/v1/report/${diagnosisId}`;
}
