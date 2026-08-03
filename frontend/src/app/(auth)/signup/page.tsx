"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [businessName, setBusinessName] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/auth/register/", {
        email,
        password,
        business_name: businessName,
      });
      setSuccess(true);
      setTimeout(() => router.push("/login"), 3000);
    } catch (err) {
      setError((err as { response?: { data?: { error?: string } } }).response?.data?.error || "Failed to create account");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg-app)]">
      <div className="card p-8 w-full max-w-md shadow-lg">
        <h2 className="text-2xl font-bold mb-6 text-center">Sign Up</h2>

        {success ? (
          <div className="bg-green-50 text-green-700 p-4 rounded text-center">
            Registration successful! Redirecting to login...
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 text-red-500 p-3 rounded text-sm">
                {error}
              </div>
            )}
            <div>
              <label className="block text-sm font-medium mb-1">
                Business Name
              </label>
              <input
                type="text"
                value={businessName}
                onChange={(e) => setBusinessName(e.target.value)}
                className="w-full border rounded p-2 focus:outline-none focus:ring-2 focus:ring-[var(--color-brand-primary)]"
              />
            </div>
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
              Create Account
            </button>
          </form>
        )}

        <p className="mt-4 text-sm text-center">
          Already have an account?{" "}
          <Link
            href="/login"
            className="text-[var(--color-brand-primary)] hover:underline"
          >
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
