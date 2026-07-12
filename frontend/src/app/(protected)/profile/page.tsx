"use client";

import { useAuthStore } from "../../../store/auth";
import { Shield, Key } from "lucide-react";

export default function ProfilePage() {
  const { user } = useAuthStore();

  const getPermissions = () => {
    if (!user) return [];
    const perms = new Set<string>();
    user.roles.forEach((role) => {
      role.permissions.forEach((perm) => perms.add(perm.name));
    });
    return Array.from(perms);
  };

  const userPermissions = getPermissions();

  return (
    <div className="max-w-3xl space-y-6">
      {/* Profile Header */}
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 flex flex-col md:flex-row items-center gap-6">
        <div className="h-20 w-20 rounded-full bg-violet-100 dark:bg-violet-950/40 text-violet-600 dark:text-violet-400 flex items-center justify-center font-bold text-2xl border border-violet-200 dark:border-violet-800">
          {user?.email[0].toUpperCase()}
        </div>
        <div className="space-y-1.5 text-center md:text-left flex-1 min-w-0">
          <h2 className="text-xl font-bold text-zinc-900 dark:text-white truncate">
            {user?.email}
          </h2>
          <p className="text-zinc-400 text-sm">
            UUID: <span className="font-mono text-xs">{user?.id}</span>
          </p>
          <div className="flex gap-2 justify-center md:justify-start">
            {user?.roles.map((role) => (
              <span
                key={role.name}
                className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-violet-50 dark:bg-violet-950 text-violet-700 dark:text-violet-400"
              >
                {role.name}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Details Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Roles Details */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-indigo-50 dark:bg-zinc-800 text-indigo-600 dark:text-indigo-400 rounded-xl">
              <Shield className="h-5 w-5" />
            </div>
            <h3 className="font-bold text-zinc-900 dark:text-white text-lg">
              Assigned Security Roles
            </h3>
          </div>
          <div className="space-y-3">
            {user?.roles.map((role) => (
              <div
                key={role.name}
                className="p-4 rounded-2xl bg-zinc-50 dark:bg-zinc-800 border border-zinc-100 dark:border-zinc-700"
              >
                <span className="font-bold text-sm text-zinc-800 dark:text-zinc-200">
                  {role.name}
                </span>
                <p className="text-xs text-zinc-400 mt-1">
                  {role.description || "No description provided."}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Permissions Details */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-6 space-y-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-violet-50 dark:bg-zinc-800 text-violet-600 dark:text-violet-400 rounded-xl">
              <Key className="h-5 w-5" />
            </div>
            <h3 className="font-bold text-zinc-900 dark:text-white text-lg">
              Active Security Permissions
            </h3>
          </div>
          <div className="grid grid-cols-1 gap-2">
            {userPermissions.map((perm) => (
              <div
                key={perm}
                className="flex items-center gap-3 px-4 py-3 rounded-2xl bg-zinc-50 dark:bg-zinc-800 border border-zinc-100 dark:border-zinc-700"
              >
                <div className="h-2.5 w-2.5 rounded-full bg-emerald-500"></div>
                <span className="font-mono text-sm text-zinc-700 dark:text-zinc-300">
                  {perm}
                </span>
              </div>
            ))}
            {userPermissions.length === 0 && (
              <p className="text-sm text-zinc-400 text-center py-4">
                No active permissions mapping found.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
