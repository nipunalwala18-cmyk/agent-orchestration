"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "../store/auth";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, accessToken } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && (!isAuthenticated || !accessToken)) {
      router.push("/login");
    }
  }, [mounted, isAuthenticated, accessToken, router]);

  // Show a premium loading spinner while resolving authentication state
  if (!mounted || !isAuthenticated || !accessToken) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-zinc-50 dark:bg-zinc-950">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-violet-500 border-t-transparent"></div>
          <p className="text-zinc-500 dark:text-zinc-400 font-medium animate-pulse">
            Authenticating Session...
          </p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
