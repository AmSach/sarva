"use client";
import { useState } from "react";
import { getLeaderboard, registerNode, submitJob } from "../../lib/api";

function JoinNode() {
  const [form, setForm] = useState({ nodeName: "", gpuTier: "rtx-3060", ownerId: "user1" });
  const [result, setResult] = useState<any>(null);

  const join = async () => {
    const r = await registerNode(form.nodeName, form.gpuTier, 4, form.ownerId);
    setResult(r);
  };

  return (
    <div className="bg-gray-800 rounded p-6">
      <h2 className="text-xl font-bold mb-4">Join the Pool</h2>
      <input className="w-full bg-gray-700 rounded px-3 py-2 mb-2" placeholder="Node Name" onChange={e => setForm({ ...form, nodeName: e.target.value })} />
      <select className="w-full bg-gray-700 rounded px-3 py-2 mb-2" onChange={e => setForm({ ...form, gpuTier: e.target.value })}>
        <option value="rtx-4090">RTX 4090</option>
        <option value="rtx-3090">RTX 3090</option>
        <option value="rtx-3060">RTX 3060</option>
        <option value="cpu">CPU</option>
      </select>
      <input className="w-full bg-gray-700 rounded px-3 py-2 mb-4" placeholder="Your User ID" onChange={e => setForm({ ...form, ownerId: e.target.value })} />
      <button onClick={join} className="bg-blue-600 px-6 py-2 rounded font-bold hover:bg-blue-700">Join Pool</button>
      {result && <pre className="mt-4 text-green-400 text-sm">{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}

function SubmitJob() {
  const [form, setForm] = useState({ type: "ml", slices: 4, submitterId: "user1", script: "python train.py" });
  const [result, setResult] = useState<any>(null);

  const submit = async () => {
    const r = await submitJob(form.type, form.script, Number(form.slices), 0, form.submitterId);
    setResult(r);
  };

  return (
    <div className="bg-gray-800 rounded p-6">
      <h2 className="text-xl font-bold mb-4">Submit Compute Job</h2>
      <select className="w-full bg-gray-700 rounded px-3 py-2 mb-2" onChange={e => setForm({ ...form, type: e.target.value })}>
        <option value="ml">ML Training</option>
        <option value="gaming">Gaming Stream</option>
        <option value="render">Rendering</option>
      </select>
      <input type="number" className="w-full bg-gray-700 rounded px-3 py-2 mb-2" placeholder="Slices (parallel parts)" value={form.slices} onChange={e => setForm({ ...form, slices: Number(e.target.value) })} />
      <input className="w-full bg-gray-700 rounded px-3 py-2 mb-4" placeholder="Your User ID" onChange={e => setForm({ ...form, submitterId: e.target.value })} />
      <button onClick={submit} className="bg-green-600 px-6 py-2 rounded font-bold hover:bg-green-700">Submit Job</button>
      {result && <pre className="mt-4 text-green-400 text-sm">{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}

function Leaderboard() {
  const [data, setData] = useState<any>(null);
  const load = async () => { const r = await getLeaderboard(); setData(r); };

  return (
    <div className="bg-gray-800 rounded p-6">
      <h2 className="text-xl font-bold mb-4">Top Contributors</h2>
      <button onClick={load} className="bg-purple-600 px-6 py-2 rounded font-bold hover:bg-purple-700 mb-4">Load Leaderboard</button>
      {data?.leaderboard?.map((u: any, i: number) => (
        <div key={i} className="flex justify-between py-1">
          <span>#{i + 1} {u.userId}</span>
          <span className="text-green-400">{u.earnedTotal.toFixed(2)} credits earned</span>
        </div>
      ))}
    </div>
  );
}

export default function Pool() {
  const [activeTab, setActiveTab] = useState<"join" | "submit" | "leaderboard">("join");
  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">Compute Pool</h1>
        <div className="flex gap-4 mb-6">
          <button onClick={() => setActiveTab("join")} className="bg-blue-600 px-4 py-2 rounded hover:bg-blue-700">Join Pool</button>
          <button onClick={() => setActiveTab("submit")} className="bg-green-600 px-4 py-2 rounded hover:bg-green-700">Submit Job</button>
          <button onClick={() => setActiveTab("leaderboard")} className="bg-purple-600 px-4 py-2 rounded hover:bg-purple-700">Leaderboard</button>
        </div>
        {activeTab === "join" ? <JoinNode /> : activeTab === "submit" ? <SubmitJob /> : <Leaderboard />}
      </div>
    </div>
  );
}