const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export async function analyzeRequirements(payload: {
  goals: string;
  challenges: string;
  raw_preferences: string;
}) {
  const res = await fetch(`${API_BASE}/businesses/analyze-requirements`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return res.json();
}

export async function calculateMatches(businessId: string) {
  const res = await fetch(`${API_BASE}/matches/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ business_id: businessId }),
  });
  return res.json();
}

export async function getCandidateExplanation(businessId: string, managerId: string) {
  const res = await fetch(`${API_BASE}/matches/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ business_id: businessId, manager_id: managerId }),
  });
  return res.json();
}

export async function getManagers() {
  const res = await fetch(`${API_BASE}/managers`, {
    method: "GET",
  });
  return res.json();
}
