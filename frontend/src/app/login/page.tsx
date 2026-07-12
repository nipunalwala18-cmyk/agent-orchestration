"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Script from "next/script";
import { api } from "../../services/api";
import { useAuthStore } from "../../store/auth";
import { Cpu, Eye, EyeOff, Lock, Mail } from "lucide-react";

export default function LoginPage() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const [isRegister, setIsRegister] = useState(false);

  // Form Fields
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  // UI State
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [googleInitialized, setGoogleInitialized] = useState(false);

  const handleGoogleCallback = async (response: any) => {
    setLoading(true);
    setError(null);
    try {
      const idToken = response.credential;
      const res = await api.post("/api/v1/auth/google", { id_token: idToken });
      const { access_token, refresh_token } = res.data.data;

      // Fetch current user details
      const meRes = await api.get("/api/v1/auth/me", {
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      });
      const user = meRes.data.data;

      setAuth(user, access_token, refresh_token);
      router.push("/dashboard");
    } catch (err) {
      const responseError = err as any;
      setError(
        responseError.response?.data?.message ||
          "Google Authentication failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const initGoogle = () => {
    const google = (window as any).google;
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;

    if (google && clientId) {
      try {
        google.accounts.id.initialize({
          client_id: clientId,
          callback: handleGoogleCallback,
        });
        const container = document.getElementById("google-signin-button");
        if (container) {
          google.accounts.id.renderButton(container, {
            theme: "outline",
            size: "large",
            width: "382",
            shape: "pill",
          });
          setGoogleInitialized(true);
        }
      } catch (err) {
        console.error("Error rendering Google Sign-In button:", err);
      }
    }
  };

  useEffect(() => {
    if (typeof window !== "undefined" && (window as any).google && !googleInitialized) {
      initGoogle();
    }
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setLoading(true);

    if (isRegister) {
      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        setLoading(false);
        return;
      }
      if (password.length < 8) {
        setError("Password must be at least 8 characters long.");
        setLoading(false);
        return;
      }
    }

    try {
      if (isRegister) {
        await api.post("/api/v1/auth/register", { email, password });
        setSuccess("Account created successfully! You can now log in.");
        setIsRegister(false);
        setPassword("");
        setConfirmPassword("");
      } else {
        const res = await api.post("/api/v1/auth/login", { email, password });
        const { access_token, refresh_token } = res.data.data;

        // Fetch current user details
        const meRes = await api.get("/api/v1/auth/me", {
          headers: {
            Authorization: `Bearer ${access_token}`,
          },
        });
        const user = meRes.data.data;

        setAuth(user, access_token, refresh_token);
        router.push("/dashboard");
      }
    } catch (err) {
      const responseError = err as any;
      setError(
        responseError.response?.data?.message ||
          "An error occurred. Please verify your credentials."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-zinc-50 dark:bg-zinc-950 p-6 relative overflow-hidden transition-colors duration-300">
      {/* Dynamic Gradients */}
      <div className="absolute top-0 -left-4 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl dark:bg-violet-500/5"></div>
      <div className="absolute bottom-0 -right-4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl dark:bg-indigo-500/5"></div>

      <div className="w-full max-w-md relative z-10">
        {/* Brand Banner */}
        <div className="flex flex-col items-center mb-8 gap-2">
          <div className="h-12 w-12 rounded-2xl bg-violet-600 flex items-center justify-center shadow-lg shadow-violet-500/30">
            <Cpu className="h-6 w-6 text-white" />
          </div>
          <h2 className="text-2xl font-extrabold text-zinc-900 dark:text-white tracking-tight">
            AI Agent Platform
          </h2>
          <p className="text-zinc-500 dark:text-zinc-400 text-sm">
            Phase 1 Foundation Control Center
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-3xl p-8 shadow-xl shadow-zinc-200/50 dark:shadow-none">
          <h3 className="text-xl font-bold text-zinc-900 dark:text-white mb-6">
            {isRegister ? "Create Account" : "Welcome Back"}
          </h3>

          {error && (
            <div className="mb-4 p-4 rounded-xl bg-red-50 dark:bg-red-950/25 border border-red-200 dark:border-red-800/40 text-red-600 dark:text-red-400 text-sm font-medium">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-4 p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/25 border border-emerald-200 dark:border-emerald-800/40 text-emerald-600 dark:text-emerald-400 text-sm font-medium">
              {success}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-2">
                Email Address
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-400">
                  <Mail className="h-5 w-5" />
                </span>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@domain.com"
                  className="block w-full pl-10 pr-4 py-3 bg-zinc-50 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-xl text-zinc-900 dark:text-white placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500 dark:focus:ring-violet-400 transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-2">
                Password
              </label>
              <div className="relative">
                <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-400">
                  <Lock className="h-5 w-5" />
                </span>
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="block w-full pl-10 pr-10 py-3 bg-zinc-50 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-xl text-zinc-900 dark:text-white placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500 dark:focus:ring-violet-400 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            {isRegister && (
              <div>
                <label className="block text-xs font-semibold text-zinc-500 dark:text-zinc-400 uppercase tracking-wider mb-2">
                  Confirm Password
                </label>
                <div className="relative">
                  <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-400">
                    <Lock className="h-5 w-5" />
                  </span>
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="block w-full pl-10 pr-4 py-3 bg-zinc-50 dark:bg-zinc-800 border border-zinc-200 dark:border-zinc-700 rounded-xl text-zinc-900 dark:text-white placeholder-zinc-400 dark:placeholder-zinc-500 focus:outline-none focus:ring-2 focus:ring-violet-500 dark:focus:ring-violet-400 transition-colors"
                  />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 bg-violet-600 hover:bg-violet-700 text-white rounded-xl font-bold shadow-md shadow-violet-500/20 transition flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="h-5 w-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : isRegister ? (
                "Create Account"
              ) : (
                "Sign In"
              )}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-6 flex items-center justify-center">
            <div className="absolute inset-x-0 border-t border-zinc-200 dark:border-zinc-800"></div>
            <span className="relative z-10 px-3 bg-white dark:bg-zinc-900 text-xs font-semibold text-zinc-400 dark:text-zinc-500 uppercase tracking-wider">
              Or continue with
            </span>
          </div>

          {/* Google Sign-In Button */}
          <div className="w-full flex justify-center mb-4">
            <div id="google-signin-button"></div>
          </div>

          {/* Toggle Button */}
          <div className="mt-6 text-center">
            <button
              onClick={() => {
                setIsRegister(!isRegister);
                setError(null);
                setSuccess(null);
              }}
              className="text-sm font-semibold text-violet-600 dark:text-violet-400 hover:underline"
            >
              {isRegister
                ? "Already have an account? Sign In"
                : "New here? Create an Account"}
            </button>
          </div>
        </div>
      </div>
      <Script
        src="https://accounts.google.com/gsi/client"
        strategy="lazyOnload"
        onLoad={initGoogle}
      />
    </main>
  );
}
