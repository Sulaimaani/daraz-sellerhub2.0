"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api";
import { useAuthStore } from "@/store/authStore";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();
  const setAccessToken = useAuthStore((state) => state.setAccessToken);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await api.post("/auth/login/", { email, password });
      setAccessToken(response.data.access);
      router.push("/dashboard");
    } catch (err) {
      setError((err as { response?: { data?: { error?: string } } }).response?.data?.error || "Failed to login");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg-app)]">
      <div className="card p-8 w-full max-w-md shadow-lg">
        <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>
        {error && (
          <div className="bg-red-50 text-red-500 p-3 rounded mb-4 text-sm">
            {error}
          </div>
        )}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border rounded p-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-brand-primary)]"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border rounded p-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-brand-primary)]"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-[var(--color-brand-primary)] text-white p-2 rounded hover:bg-[var(--color-brand-primary-dark)] font-bold"
          >
            Sign In
          </button>
        </form>
        <p className="mt-4 text-sm text-center">
          Don&apos;t have an account?{" "}
          <Link
            href="/signup"
            className="text-[var(--color-brand-primary)] hover:underline"
          >
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
