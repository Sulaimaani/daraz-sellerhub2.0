"use client";
import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import api from "@/lib/api";
import { useAuthStore } from "@/store/authStore";
import {
  LayoutDashboard,
  Store,
  Tag,
  DollarSign,
  RotateCcw,
  Calculator,
  Settings,
  HelpCircle,
  LogOut,
} from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const setAccessToken = useAuthStore((state) => state.setAccessToken);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Attempt to verify auth (refresh token will be used if access token is missing/expired)
    api
      .get("/auth/me/")
      .then(() => setLoading(false))
      .catch(() => {
        router.push("/login");
      });
  }, [router]);

  const handleLogout = async () => {
    try {
      await api.post("/auth/logout/");
      setAccessToken(null);
      router.push("/login");
    } catch {
      console.error("Logout failed");
    }
  };

  if (loading)
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    );

  const navItems = [
    { name: "Orders & Profit", href: "/dashboard", icon: LayoutDashboard },
    { name: "Stores", href: "/stores", icon: Store },
    { name: "Label Enhancement", href: "/tools/daraz", icon: Tag },
    { name: "COD Reconciliation", href: "/tools/cod", icon: DollarSign },
    { name: "Returns & Claims", href: "/tools/returns", icon: RotateCcw },
    { name: "Profit Calculator", href: "/tools/calculator", icon: Calculator },
    { name: "SKU Settings", href: "/tools/sku", icon: Settings },
    { name: "How-to Guides", href: "/docs", icon: HelpCircle },
  ];

  return (
    <div className="flex h-screen bg-[var(--color-bg-app)] overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-[var(--color-border-card)] flex flex-col">
        <div className="p-6">
          <h1 className="text-xl font-bold text-[var(--color-brand-primary)]">
            Daraz Seller SaaS
          </h1>
        </div>

        <nav className="flex-1 overflow-y-auto py-4">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className={`sidebar-item ${isActive ? "active" : ""}`}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    {item.name}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="p-4 border-t border-[var(--color-border-card)]">
          <Link href="/settings" className="sidebar-item mb-2">
            <Settings className="w-5 h-5 mr-3" />
            Account Settings
          </Link>
          <button
            onClick={handleLogout}
            className="sidebar-item w-full text-left text-red-600 hover:bg-red-50 hover:text-red-700"
          >
            <LogOut className="w-5 h-5 mr-3" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <header className="header-gradient p-6">
          <h2 className="text-2xl font-bold">Dashboard</h2>
        </header>
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}
