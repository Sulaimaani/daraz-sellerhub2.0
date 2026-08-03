"use client";

import { useEffect, useState } from "react";
import api from "../lib/api";

type Store = {
  id: number;
  name: string;
  short_code: string;
};

export function StoreSwitcher() {
  const [stores, setStores] = useState<Store[]>([]);
  const [activeStoreId, setActiveStoreId] = useState<number | null>(null);

  useEffect(() => {
    api.get("/stores/").then((res) => {
      setStores(res.data);
    }).catch(() => {});
  }, []);

  return (
    <div className="flex items-center space-x-2 border px-3 py-1 rounded-md">
      <select 
        className="bg-transparent text-sm font-medium focus:outline-none"
        value={activeStoreId || ""}
        onChange={(e) => setActiveStoreId(e.target.value ? parseInt(e.target.value) : null)}
      >
        <option value="">All Stores</option>
        {stores.map(store => (
          <option key={store.id} value={store.id}>
            {store.name} {store.short_code ? `(${store.short_code})` : ""}
          </option>
        ))}
      </select>
    </div>
  );
}
