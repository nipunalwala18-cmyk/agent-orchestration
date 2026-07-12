"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuthStore } from "../store/auth";
import { api } from "../services/api";
import {
  LayoutDashboard,
  MessageSquare,
  User,
  Users,
  LogOut,
  Cpu,
} from "lucide-react";

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, refreshToken, clearAuth, hasPermission } = useAuthStore();

  const handleLogout = async () => {
    try {
      if (refreshToken) {
        await api.post("/api/v1/auth/logout", { refresh_token: refreshToken });
      }
    } catch (e) {
      console.error("Logout failed", e);
    } finally {
      clearAuth();
      router.push("/login");
    }
  };

  const menuItems = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Chat Hub", href: "/chat", icon: MessageSquare },
    { name: "My Profile", href: "/profile", icon: User },
  ];

  const showUsersLink = hasPermission("users:read");

  return (
    <aside className="w-64 bg-white dark:bg-zinc-900 border-r border-zinc-200 dark:border-zinc-800 flex flex-col justify-between h-screen sticky top-0">
      <div className="flex flex-col">
        {/* Header Logo */}
        <div className="h-16 flex items-center gap-3 px-6 border-b border-zinc-200 dark:border-zinc-800">
          <Cpu className="h-6 w-6 text-violet-600 dark:text-violet-400" />
          <span className="font-bold text-lg text-zinc-900 dark:text-white tracking-wide">
            AgentPlatform
          </span>
        </div>

        {/* Menu Items */}
        <nav className="p-4 space-y-1">
          {menuItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200 ${
                  isActive
                    ? "bg-violet-50 dark:bg-violet-950/40 text-violet-600 dark:text-violet-400"
                    : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800/60 hover:text-zinc-900 dark:hover:text-white"
                }`}
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </Link>
            );
          })}

          {showUsersLink && (
            <Link
              href="/users"
              className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200 ${
                pathname === "/users"
                  ? "bg-violet-50 dark:bg-violet-950/40 text-violet-600 dark:text-violet-400"
                  : "text-zinc-600 dark:text-zinc-400 hover:bg-zinc-50 dark:hover:bg-zinc-800/60 hover:text-zinc-900 dark:hover:text-white"
              }`}
            >
              <Users className="h-5 w-5" />
              User Manager
            </Link>
          )}
        </nav>
      </div>

      {/* User Session Footer */}
      <div className="p-4 border-t border-zinc-200 dark:border-zinc-800 space-y-3">
        <div className="flex items-center gap-3 px-3">
          <div className="h-9 w-9 rounded-full bg-violet-600 text-white flex items-center justify-center font-bold text-sm">
            {user?.email[0].toUpperCase()}
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-semibold text-zinc-900 dark:text-white truncate">
              {user?.email}
            </span>
            <span className="text-xs text-zinc-400 truncate">
              {user?.roles.map((r) => r.name).join(", ")}
            </span>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20 font-medium transition-all duration-200"
        >
          <LogOut className="h-5 w-5" />
          Sign Out
        </button>
      </div>
    </aside>
  );
}
