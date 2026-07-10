"use client";

import { useEffect, useState, useCallback } from "react";
import {
  Activity,
  Database,
  Server,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Cpu,
  Layers,
  Terminal,
  ExternalLink,
  GitBranch,
} from "lucide-react";

interface HealthStatus {
  database: string;
  redis: string;
  api: string;
}

export default function Home() {
  const [status, setStatus] = useState<HealthStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>("");
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [historyLogs, setHistoryLogs] = useState<Array<{ time: string; msg: string; type: "info" | "success" | "error" }>>([]);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const addLog = (msg: string, type: "info" | "success" | "error" = "info") => {
    const time = new Date().toLocaleTimeString();
    setHistoryLogs((prev) => [{ time, msg, type }, ...prev.slice(0, 14)]);
  };

  const fetchHealth = useCallback(async () => {
    setIsRefreshing(true);
    addLog(`Initiating connection check to health endpoint: ${API_URL}/health`, "info");
    
    try {
      const startTime = Date.now();
      const res = await fetch(`${API_URL}/health`, { cache: "no-store" });
      const duration = Date.now() - startTime;

      if (!res.ok && res.status !== 503) {
        throw new Error(`HTTP network error: status code ${res.status}`);
      }

      const wrapper = await res.json();
      const data = wrapper.data;
      if (!data) {
        throw new Error("Invalid API response payload structure");
      }
      setStatus(data);
      setError(null);
      setLastUpdated(new Date().toLocaleTimeString());

      const apiState = data.api === "healthy" ? "HEALTHY" : "UNHEALTHY";
      addLog(`Backend responded in ${duration}ms. System state: ${apiState} (DB: ${data.database}, Redis: ${data.redis})`, data.api === "healthy" ? "success" : "error");
    } catch (err: unknown) {
      const errMsg = err instanceof Error ? err.message : "Failed to reach FastAPI Gateway";
      setError(errMsg);
      setStatus(null);
      addLog(`Connectivity check failed: ${errMsg}`, "error");
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, [API_URL]);

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 8000);
    return () => clearInterval(interval);
  }, [fetchHealth]);

  const getStatusColor = (state: string | undefined) => {
    if (state === "connected" || state === "healthy") {
      return "text-emerald-400 border-emerald-500/30 bg-emerald-500/10 shadow-[0_0_15px_rgba(16,185,129,0.15)]";
    }
    if (state === "disconnected" || state === "unhealthy" || !state) {
      return "text-rose-400 border-rose-500/30 bg-rose-500/10 shadow-[0_0_15px_rgba(244,63,94,0.15)]";
    }
    return "text-amber-400 border-amber-500/30 bg-amber-500/10 shadow-[0_0_15px_rgba(245,158,11,0.15)]";
  };

  const getStatusBadge = (state: string | undefined) => {
    if (state === "connected" || state === "healthy") {
      return (
        <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 border border-emerald-500/25 text-emerald-400">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Connected
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/15 border border-rose-500/25 text-rose-400">
        <span className="h-1.5 w-1.5 rounded-full bg-rose-400" />
        Disconnected
      </span>
    );
  };

  return (
    <main className="min-h-screen bg-[#070709] text-zinc-100 flex flex-col items-center justify-start p-4 sm:p-8 font-sans selection:bg-indigo-500/30">
      {/* Decorative Gradients */}
      <div className="absolute top-0 left-1/4 w-[400px] h-[400px] rounded-full bg-indigo-600/10 blur-[100px] pointer-events-none" />
      <div className="absolute bottom-10 right-1/4 w-[500px] h-[500px] rounded-full bg-purple-600/10 blur-[120px] pointer-events-none" />

      {/* Outer Dashboard Shell */}
      <div className="w-full max-w-5xl z-10 space-y-8 mt-4 sm:mt-8">
        
        {/* Top Header Card */}
        <div className="relative overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-900/30 backdrop-blur-md p-6 sm:p-8 shadow-xl">
          <div className="absolute right-0 top-0 h-full w-1/3 bg-gradient-to-l from-indigo-500/5 to-transparent pointer-events-none" />
          
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
                  <Layers className="h-6 w-6" />
                </div>
                <span className="text-xs font-bold uppercase tracking-widest text-indigo-400">Orchestration Control Plane</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-zinc-50 to-zinc-400">
                AI Multi-Agent Orchestration Platform
              </h1>
              <p className="text-sm text-zinc-400 max-w-xl">
                Phase 1 Core Infrastructure Control Panel. Monitoring vital connection gates, caching fabrics, and messaging backbones.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={fetchHealth}
                disabled={isRefreshing}
                className="flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg bg-zinc-800 hover:bg-zinc-700 active:bg-zinc-800 text-zinc-200 border border-zinc-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed group cursor-pointer"
              >
                <RefreshCw className={`h-4 w-4 text-indigo-400 transition-transform duration-700 ${isRefreshing ? "animate-spin" : "group-hover:rotate-180"}`} />
                {isRefreshing ? "Validating..." : "Recheck Status"}
              </button>
            </div>
          </div>

          {/* Quick Details Bar */}
          <div className="mt-8 pt-6 border-t border-zinc-800/80 flex flex-wrap items-center gap-x-6 gap-y-3 text-xs text-zinc-500">
            <div className="flex items-center gap-1.5">
              <Cpu className="h-3.5 w-3.5 text-zinc-400" />
              <span>Gateway URL: <span className="font-mono text-zinc-300">{API_URL}</span></span>
            </div>
            <div className="flex items-center gap-1.5">
              <GitBranch className="h-3.5 w-3.5 text-zinc-400" />
              <span>Phase: <span className="text-indigo-400 font-semibold">01 Foundation</span></span>
            </div>
            <div className="sm:ml-auto text-zinc-500">
              Last Check: <span className="font-mono text-zinc-300">{lastUpdated || "Never"}</span>
            </div>
          </div>
        </div>

        {/* 3-Column Status Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Card 1: API Status */}
          <div className={`rounded-xl border p-6 transition duration-300 hover:scale-[1.01] flex flex-col justify-between h-48 backdrop-blur-md ${getStatusColor(status?.api)}`}>
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <span className="text-xs uppercase font-semibold tracking-wider opacity-60">API Gateway</span>
                <h3 className="text-lg font-bold text-zinc-100">Backend Status</h3>
              </div>
              <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                <Server className="h-5 w-5" />
              </div>
            </div>
            <div className="flex items-center justify-between mt-4">
              <span className="text-2xl font-black uppercase tracking-tight">
                {loading ? "Checking" : (status ? "Healthy" : "Offline")}
              </span>
              {loading ? (
                <div className="h-2 w-2 rounded-full bg-amber-400 animate-ping" />
              ) : (
                status?.api === "healthy" ? (
                  <CheckCircle className="h-6 w-6 text-emerald-400" />
                ) : (
                  <XCircle className="h-6 w-6 text-rose-400 animate-pulse" />
                )
              )}
            </div>
          </div>

          {/* Card 2: Database Status */}
          <div className={`rounded-xl border p-6 transition duration-300 hover:scale-[1.01] flex flex-col justify-between h-48 backdrop-blur-md ${getStatusColor(status?.database)}`}>
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <span className="text-xs uppercase font-semibold tracking-wider opacity-60">Storage Core</span>
                <h3 className="text-lg font-bold text-zinc-100">Database Status</h3>
              </div>
              <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                <Database className="h-5 w-5" />
              </div>
            </div>
            <div className="flex items-center justify-between mt-4">
              <span className="text-2xl font-black uppercase tracking-tight">
                {loading ? "Loading" : (status?.database === "connected" ? "Online" : "Offline")}
              </span>
              {loading ? (
                <div className="h-2 w-2 rounded-full bg-amber-400 animate-ping" />
              ) : (
                getStatusBadge(status?.database)
              )}
            </div>
          </div>

          {/* Card 3: Redis Status */}
          <div className={`rounded-xl border p-6 transition duration-300 hover:scale-[1.01] flex flex-col justify-between h-48 backdrop-blur-md ${getStatusColor(status?.redis)}`}>
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <span className="text-xs uppercase font-semibold tracking-wider opacity-60">Memory Cache</span>
                <h3 className="text-lg font-bold text-zinc-100">Redis Status</h3>
              </div>
              <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                <Activity className="h-5 w-5" />
              </div>
            </div>
            <div className="flex items-center justify-between mt-4">
              <span className="text-2xl font-black uppercase tracking-tight">
                {loading ? "Loading" : (status?.redis === "connected" ? "Active" : "Offline")}
              </span>
              {loading ? (
                <div className="h-2 w-2 rounded-full bg-amber-400 animate-ping" />
              ) : (
                getStatusBadge(status?.redis)
              )}
            </div>
          </div>

        </div>

        {/* Global Error Banner */}
        {error && (
          <div className="flex items-center gap-3 p-4 rounded-xl border border-rose-500/25 bg-rose-500/5 text-rose-400 animate-fade-in shadow-[0_0_20px_rgba(244,63,94,0.05)]">
            <AlertTriangle className="h-5 w-5 shrink-0" />
            <div className="text-sm font-medium">
              <span className="font-bold">Gateway Connection Failure:</span> {error}. Ensure your FastAPI server is running locally on port 8000 or through Docker Compose.
            </div>
          </div>
        )}

        {/* Diagnostic Terminal Card */}
        <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-6 shadow-2xl relative">
          <div className="absolute top-3 right-4 flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-zinc-800" />
            <span className="w-2.5 h-2.5 rounded-full bg-zinc-800" />
            <span className="w-2.5 h-2.5 rounded-full bg-zinc-800" />
          </div>

          <div className="flex items-center gap-2 mb-4 border-b border-zinc-900 pb-3">
            <Terminal className="h-4.5 w-4.5 text-indigo-400" />
            <span className="text-xs font-bold uppercase tracking-wider text-zinc-400 font-mono">Gateway Console Log</span>
          </div>

          <div className="font-mono text-xs space-y-2.5 h-44 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-zinc-800 scrollbar-track-transparent">
            {loading && historyLogs.length === 0 ? (
              <div className="text-zinc-500 italic animate-pulse">Establishing handshake connections...</div>
            ) : (
              historyLogs.map((log, index) => (
                <div key={index} className="flex gap-4 items-start leading-relaxed hover:bg-zinc-900/20 p-1 rounded transition">
                  <span className="text-zinc-600 select-none shrink-0">[{log.time}]</span>
                  <span className={
                    log.type === "success" ? "text-emerald-400" :
                    log.type === "error" ? "text-rose-400 font-semibold" : "text-indigo-300"
                  }>
                    {log.type === "success" && "✔ "}
                    {log.type === "error" && "✖ "}
                    {log.msg}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Footer info */}
        <div className="flex flex-col sm:flex-row items-center justify-between text-xs text-zinc-500 pt-6 border-t border-zinc-900 gap-4">
          <p>© 2026 AI Orchestration Platform. All rights reserved.</p>
          <div className="flex items-center gap-4">
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 hover:text-indigo-400 transition">
              <span>Swagger API Docs</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          </div>
        </div>

      </div>
    </main>
  );
}
