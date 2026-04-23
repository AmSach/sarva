"use client";
import { useState, useEffect } from "react";
import { getStatus, getNodes, getJobs } from "../lib/api";

export default function Dashboard() {
  const [status, setStatus] = useState<any>(null);
  const [nodes, setNodes] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    async function load() {
      try {
        const [s, n, j] = await Promise.all([getStatus(), getNodes(), getJobs()]);
        setStatus(s);
        setNodes(n.nodes || []);
        setJobs(j.jobs || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
    interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-4xl font-mono font-bold text-cyan-400 animate-pulse">INITIALIZING...</div>
    </div>
  );

  const online = nodes.filter((n: any) => n.online);

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <div className="text-center py-16">
        <h1 className="text-6xl font-mono font-black mb-4">
          <span className="text-cyan-400">Power</span> the <span className="text-white">Grid</span>
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-8">
          Decentralized compute. Share GPU, earn credits, access unlimited power.
        </p>
        <a href="/pool" className="px-8 py-4 bg-cyan-500 hover:bg-cyan-400 text-black font-bold rounded-lg inline-block">
          Join the Pool
        </a>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
        {[
          { label: "Total Nodes", value: status?.nodes ?? 0, color: "text-cyan-400" },
          { label: "Online Now", value: online.length, color: "text-green-400" },
          { label: "Jobs Run", value: status?.jobs ?? 0, color: "text-purple-400" },
          { label: "Network Status", value: "LIVE", color: "text-green-500" },
        ].map((stat) => (
          <div key={stat.label} className="bg-white/5 border border-white/10 rounded-xl p-6 text-center">
            <div className={`text-4xl font-mono font-black ${stat.color}`}>{stat.value}</div>
            <div className="text-gray-500 text-sm mt-1">{stat.label}</div>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />Active Nodes
          </h2>
          {online.length === 0 ? (
            <div className="text-gray-500 text-center py-8">No nodes online yet.</div>
          ) : (
            <div className="space-y-3">
              {online.map((n: any) => (
                <div key={n.id} className="flex justify-between bg-black/30 rounded-lg px-4 py-3">
                  <div>
                    <div className="font-mono text-sm font-bold">{n.name}</div>
                    <div className="text-xs text-gray-500">{n.gpuTier} · {n.cpuCores} cores · {n.ramGb}GB</div>
                  </div>
                  <div className="text-right">
                    <div className="text-cyan-400 font-mono text-sm">{n.qualityScore}x</div>
                    <div className="text-xs text-gray-500">{n.region?.toUpperCase()}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white/5 border border-white/10 rounded-xl p-6">
          <h2 className="text-xl font-bold mb-4">Recent Jobs</h2>
          {jobs.length === 0 ? (
            <div className="text-gray-500 text-center py-8">No jobs yet.</div>
          ) : (
            <div className="space-y-3">
              {jobs.slice(0, 6).map((j: any) => (
                <div key={j.id} className="flex justify-between bg-black/30 rounded-lg px-4 py-3">
                  <div>
                    <div className="font-mono text-sm font-bold">{j.id}</div>
                    <div className="text-xs text-gray-500">{j.type} · {j.status}</div>
                  </div>
                  <div className={`text-sm font-bold ${
                    j.status === "completed" ? "text-green-400" :
                    j.status === "failed" ? "text-red-400" : "text-yellow-400"
                  }`}>{j.status}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}