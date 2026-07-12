"use client";

import { useEffect, useState } from "react";
import { useAuthStore } from "../../../store/auth";
import { api } from "../../../services/api";
import { Users, ShieldAlert } from "lucide-react";

interface UserRecord {
  id: string;
  email: string;
  is_active: boolean;
  roles: {
    name: string;
    description?: string;
  }[];
}

export default function UsersPage() {
  const { hasPermission } = useAuthStore();
  const [usersList, setUsersList] = useState<UserRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = async () => {
    try {
      const res = await api.get("/api/v1/users");
      setUsersList(res.data.data);
    } catch (err: any) {
      setError(
        err.response?.data?.message || "Failed to retrieve user listing."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (hasPermission("users:read")) {
      fetchUsers();
    } else {
      setLoading(false);
    }
  }, []);

  if (!hasPermission("users:read")) {
    return (
      <div className="max-w-md mx-auto mt-12 text-center space-y-4">
        <div className="p-4 bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 rounded-3xl inline-block border border-red-200 dark:border-red-800/40">
          <ShieldAlert className="h-10 w-10" />
        </div>
        <h3 className="text-xl font-bold text-zinc-900 dark:text-white">
          Permission Denied
        </h3>
        <p className="text-sm text-zinc-500 dark:text-zinc-400 leading-relaxed">
          Your active account role does not possess the{" "}
          <code className="font-mono text-xs text-red-600 bg-red-50 dark:bg-red-950/30 px-1.5 py-0.5 rounded">
            users:read
          </code>{" "}
          permission required to view user details.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="p-2.5 bg-violet-50 dark:bg-zinc-800 text-violet-600 dark:text-violet-400 rounded-2xl">
          <Users className="h-6 w-6" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-zinc-900 dark:text-white">
            User Security Control
          </h2>
          <p className="text-xs text-zinc-400">
            List and monitor user system roles and authorizations.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-violet-500"></div>
        </div>
      ) : error ? (
        <div className="p-4 rounded-2xl bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800/40 text-red-600 dark:text-red-400 text-sm font-medium">
          {error}
        </div>
      ) : (
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-zinc-200 dark:border-zinc-800 bg-zinc-50/50 dark:bg-zinc-800/20 text-zinc-500 dark:text-zinc-400 text-xs uppercase font-bold tracking-wider">
                  <th className="px-6 py-4">User</th>
                  <th className="px-6 py-4">User ID (UUID)</th>
                  <th className="px-6 py-4">Assigned Roles</th>
                  <th className="px-6 py-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800 text-sm">
                {usersList.map((user) => (
                  <tr
                    key={user.id}
                    className="hover:bg-zinc-50/50 dark:hover:bg-zinc-800/20 transition-colors duration-150"
                  >
                    <td className="px-6 py-4 font-semibold text-zinc-900 dark:text-white">
                      <div className="flex items-center gap-2.5">
                        <div className="h-8 w-8 rounded-full bg-violet-100 dark:bg-violet-950 text-violet-700 dark:text-violet-400 flex items-center justify-center font-bold text-xs">
                          {user.email[0].toUpperCase()}
                        </div>
                        <span className="truncate max-w-[150px]">
                          {user.email}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-zinc-500 dark:text-zinc-400">
                      {user.id}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex gap-1.5 flex-wrap">
                        {user.roles.map((role) => (
                          <span
                            key={role.name}
                            className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-violet-50 dark:bg-violet-950 text-violet-700 dark:text-violet-400 border border-violet-100 dark:border-violet-800"
                          >
                            {role.name}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                          user.is_active
                            ? "bg-emerald-50 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-400"
                            : "bg-red-50 dark:bg-red-950 text-red-700 dark:text-red-400"
                        }`}
                      >
                        <span
                          className={`h-1.5 w-1.5 rounded-full ${
                            user.is_active ? "bg-emerald-500" : "bg-red-500"
                          }`}
                        ></span>
                        {user.is_active ? "Active" : "Disabled"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
