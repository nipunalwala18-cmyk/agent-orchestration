"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "../../../store/auth";
import { api } from "../../../services/api";
import {
  Activity,
  Cpu,
  Layers,
  RefreshCw,
  Server,
  UserCheck,
} from "lucide-react";

interface HealthData {
  database: string;
  redis: string;
  api: string;
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [health, setHealth] = useState<HealthData | null>(null);
  const [loadingHealth, setLoadingHealth] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchHealth = async () => {
    setRefreshing(true);
    try {
      const res = await api.get("/api/v1/health");
      setHealth(res.data.data);
    } catch (e) {
      console.error("Health check fetch failed", e);
    } finally {
      setLoadingHealth(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* Welcome Card */}
      <div className="p-6 md:p-8 rounded-3xl bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-xl shadow-violet-500/10">
        <div className="max-w-xl space-y-2">
          <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight">
            Welcome back, {user?.email.split("@")[0]}!
          </h2>
          <p className="text-violet-100 text-sm md:text-base leading-relaxed">
            Welcome to the AI Agent Orchestration Platform control center. All
            core backend engines and security protocols are active and running.
          </p>
        </div>
      </div>

      {/* Stats Cards Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* User Info Card */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 flex items-start gap-4">
          <div className="p-3.5 rounded-2xl bg-violet-50 dark:bg-violet-950/30 text-violet-600 dark:text-violet-400">
            <UserCheck className="h-6 w-6" />
          </div>
          <div className="space-y-1">
            <h4 className="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
              Profile Access
            </h4>
            <p className="text-lg font-bold text-zinc-900 dark:text-white truncate max-w-[180px]">
              {user?.email}
            </p>
            <div className="flex gap-1.5 flex-wrap pt-1">
              {user?.roles.map((role) => (
                <span
                  key={role.name}
                  className="px-2 py-0.5 rounded-full text-xs font-semibold bg-violet-50 dark:bg-violet-950 text-violet-700 dark:text-violet-300 border border-violet-100 dark:border-violet-800"
                >
                  {role.name}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Live Diagnostics Card */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/30 text-emerald-600 dark:text-emerald-400">
                <Activity className="h-6 w-6" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
                  Diagnostics
                </h4>
                <p className="text-lg font-bold text-zinc-900 dark:text-white">
                  System Health
                </p>
              </div>
            </div>
            <button
              onClick={fetchHealth}
              disabled={refreshing}
              className={`text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 ${
                refreshing ? "animate-spin" : ""
              }`}
            >
              <RefreshCw className="h-5 w-5" />
            </button>
          </div>

          <div className="mt-4 grid grid-cols-3 gap-2 text-center">
            <div className="p-2 rounded-xl bg-zinc-50 dark:bg-zinc-800 border border-zinc-100 dark:border-zinc-700">
              <span className="text-[10px] uppercase font-bold text-zinc-400">
                API
              </span>
              <p
                className={`text-xs font-semibold mt-1 ${
                  health?.api === "healthy"
                    ? "text-emerald-500"
                    : "text-red-500"
                }`}
              >
                {loadingHealth ? "..." : health?.api.toUpperCase()}
              </p>
            </div>
            <div className="p-2 rounded-xl bg-zinc-50 dark:bg-zinc-800 border border-zinc-100 dark:border-zinc-700">
              <span className="text-[10px] uppercase font-bold text-zinc-400">
                DB
              </span>
              <p
                className={`text-xs font-semibold mt-1 ${
                  health?.database === "connected"
                    ? "text-emerald-500"
                    : "text-red-500"
                }`}
              >
                {loadingHealth
                  ? "..."
                  : health?.database === "connected"
                    ? "OK"
                    : "ERR"}
              </p>
            </div>
            <div className="p-2 rounded-xl bg-zinc-50 dark:bg-zinc-800 border border-zinc-100 dark:border-zinc-700">
              <span className="text-[10px] uppercase font-bold text-zinc-400">
                Cache
              </span>
              <p
                className={`text-xs font-semibold mt-1 ${
                  health?.redis === "connected"
                    ? "text-emerald-500"
                    : "text-red-500"
                }`}
              >
                {loadingHealth
                  ? "..."
                  : health?.redis === "connected"
                    ? "OK"
                    : "ERR"}
              </p>
            </div>
          </div>
        </div>

        {/* System Core Engine */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 flex items-start gap-4">
          <div className="p-3.5 rounded-2xl bg-indigo-50 dark:bg-indigo-950/30 text-indigo-600 dark:text-indigo-400">
            <Server className="h-6 w-6" />
          </div>
          <div className="space-y-1">
            <h4 className="text-sm font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider">
              Service Stack
            </h4>
            <p className="text-lg font-bold text-zinc-900 dark:text-white">
              FastAPI + Postgres
            </p>
            <span className="inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-400">
              Docker compose local
            </span>
          </div>
        </div>
      </div>

      {/* Placeholders Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Future Agent Registry Placeholder */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-violet-100 dark:bg-zinc-800 text-violet-600 dark:text-violet-400">
              <Cpu className="h-5 w-5" />
            </div>
            <h3 className="font-bold text-zinc-900 dark:text-white text-lg">
              Future Agent Registry (Phase 2)
            </h3>
          </div>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed">
            The Agent Registry will house all AI Agent classes (RAG, SQL,
            Finance, Customer support, etc.). Future orchestrators can load and
            assign tasks to specific workers from this pool.
          </p>
          <div className="p-4 rounded-2xl border border-dashed border-zinc-200 dark:border-zinc-800 flex items-center justify-center text-zinc-400 text-xs font-semibold">
            Registry Schema Prepared
          </div>
        </div>

        {/* Future Orchestration Workflows Placeholder */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-100 dark:bg-zinc-800 text-indigo-600 dark:text-indigo-400">
              <Layers className="h-5 w-5" />
            </div>
            <h3 className="font-bold text-zinc-900 dark:text-white text-lg">
              Recent Chats & Threads (Local)
            </h3>
          </div>
          <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed">
            Conversations will sync here once connected to PostgreSQL. The chat
            architecture handles prompt streaming and chat histories. Currently,
            you can play with a localized sandbox in the Chat Hub.
          </p>
          <div className="p-4 rounded-2xl border border-dashed border-zinc-200 dark:border-zinc-800 flex items-center justify-center text-zinc-400 text-xs font-semibold">
            Local Chat History Ready in Chat Hub
          </div>
        </div>
      </div>
    </div>
  );
}
