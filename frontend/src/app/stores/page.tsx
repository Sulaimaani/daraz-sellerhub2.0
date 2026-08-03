"use client";

import { useEffect, useState } from "react";
import api from "../../lib/api";
import { StoreSwitcher } from "../../components/StoreSwitcher";

type Store = {
  id: number;
  name: string;
  short_code: string;
  status: string;
  connected_at: string;
  sync_progress_pct: number;
  sync_status: string;
  sync_counters: Record<string, number>;
};

export default function StoresDashboard() {
  const [stores, setStores] = useState<Store[]>([]);

  useEffect(() => {
    api.get("/stores/").then((res) => {
      setStores(res.data);
    });
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <h1 className="font-bold text-xl text-gray-900">Daraz SaaS</h1>
          <StoreSwitcher />
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8 flex justify-between items-center">
          <h2 className="text-2xl font-bold">Connected Stores</h2>
          <a href="/onboarding?step=2" className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded font-medium text-sm">
            + Connect New Store
          </a>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {stores.map((store) => (
            <div key={store.id} className="bg-white rounded-xl shadow-sm border p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-bold text-lg">{store.name}</h3>
                  <p className="text-sm text-gray-500">Seller ID: {store.short_code}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  store.status === 'connected' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                }`}>
                  {store.status}
                </span>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">History Sync</span>
                    <span className="font-medium">{store.sync_progress_pct}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-orange-500 h-2 rounded-full" 
                      style={{ width: `${store.sync_progress_pct}%` }}
                    ></div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="bg-gray-50 p-2 rounded border">
                    <div className="text-gray-500 text-xs">Orders</div>
                    <div className="font-medium">{store.sync_counters?.orders || 0}</div>
                  </div>
                  <div className="bg-gray-50 p-2 rounded border">
                    <div className="text-gray-500 text-xs">Returns</div>
                    <div className="font-medium">{store.sync_counters?.returns || 0}</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
          {stores.length === 0 && (
            <div className="col-span-full text-center py-12 text-gray-500 bg-white border rounded-xl border-dashed">
              No stores connected yet.
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
