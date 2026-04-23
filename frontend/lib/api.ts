const API = "https://e65440d9-cfb0-47fa-b11a-d2070bf13013.up.railway.app";

async function apiGet(path: string): Promise<any> {
  const r = await fetch(`${API}${path}`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

async function apiPost(path: string, body: Record<string, any>): Promise<any> {
  const r = await fetch(`${API}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export const getStatus = () => apiGet("/status");
export const getNodes = () => apiGet("/nodes");
export const getJobs = () => apiGet("/jobs");
export const getLeaderboard = () => apiGet("/credits/leaderboard");

export const registerNode = (nodeName: string, gpuTier: string, cpuCores: number, ownerId: string) =>
  apiPost("/nodes/register", { nodeName, gpuTier, cpuCores, ramGb: 8, ownerId, region: "in" });

export const submitJob = (type: string, script: string, slices: number, priority: number, submitterId: string) =>
  apiPost("/jobs/submit", { type, script, slices: Number(slices), priority: Number(priority), submitterId });