"use client";

import { AuthGuard } from "../../components/AuthGuard";
import { Sidebar } from "../../components/Sidebar";
import { Navbar } from "../../components/Navbar";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="flex h-screen bg-zinc-50 dark:bg-zinc-950 overflow-hidden transition-colors duration-300">
        {/* Navigation Sidebar */}
        <Sidebar />

        {/* Content Workspace */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {/* Top Navbar */}
          <Navbar />

          {/* Main Panel View */}
          <main className="flex-1 overflow-y-auto p-6 md:p-8 bg-zinc-50/50 dark:bg-zinc-950/40 transition-colors duration-300">
            {children}
          </main>
        </div>
      </div>
    </AuthGuard>
  );
}
