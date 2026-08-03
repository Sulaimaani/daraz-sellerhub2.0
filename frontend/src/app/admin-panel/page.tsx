"use client";

import React, { useState } from 'react';
import { Users, Store, CreditCard, Activity, Ticket, Search, UserCheck, Settings, AlertTriangle } from 'lucide-react';

export default function AdminPanelPage() {
  const [activeTab, setActiveTab] = useState('users');

  return (
    <div className="min-h-screen bg-slate-100 font-sans">
      <div className="bg-slate-900 text-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="font-bold text-xl tracking-tight flex items-center gap-2">
            <span className="text-orange-500">SellerHub</span> <span className="text-slate-400 font-normal">/ Staff Admin</span>
          </div>
          <div className="flex gap-4">
            <div className="text-sm text-slate-400 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span> API Status: Healthy
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 md:grid-cols-12 gap-8">
        <div className="md:col-span-3 space-y-2">
          <button onClick={() => setActiveTab('users')} className={`w-full text-left px-4 py-3 rounded-xl font-bold flex items-center gap-3 transition ${activeTab === 'users' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-600 hover:bg-slate-200'}`}>
            <Users className="w-5 h-5" /> Users & Impersonation
          </button>
          <button onClick={() => setActiveTab('stores')} className={`w-full text-left px-4 py-3 rounded-xl font-bold flex items-center gap-3 transition ${activeTab === 'stores' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-600 hover:bg-slate-200'}`}>
            <Store className="w-5 h-5" /> Store Health
          </button>
          <button onClick={() => setActiveTab('billing')} className={`w-full text-left px-4 py-3 rounded-xl font-bold flex items-center gap-3 transition ${activeTab === 'billing' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-600 hover:bg-slate-200'}`}>
            <CreditCard className="w-5 h-5" /> Subscriptions & Billing
          </button>
          <button onClick={() => setActiveTab('monitoring')} className={`w-full text-left px-4 py-3 rounded-xl font-bold flex items-center gap-3 transition ${activeTab === 'monitoring' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-600 hover:bg-slate-200'}`}>
            <Activity className="w-5 h-5" /> API & Job Monitoring
          </button>
          <button onClick={() => setActiveTab('support')} className={`w-full text-left px-4 py-3 rounded-xl font-bold flex items-center gap-3 transition ${activeTab === 'support' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-600 hover:bg-slate-200'}`}>
            <Ticket className="w-5 h-5" /> Support Tickets
          </button>
        </div>

        <div className="md:col-span-9 space-y-6">
          {activeTab === 'users' && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                <h2 className="text-xl font-bold text-slate-800">User Directory</h2>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input type="text" placeholder="Search email or name..." className="border border-slate-300 rounded-lg pl-10 pr-4 py-2 text-sm outline-none w-64 focus:border-blue-500" />
                </div>
              </div>
              <table className="w-full text-left text-sm">
                <thead className="bg-white border-b border-slate-200 text-slate-500">
                  <tr>
                    <th className="px-6 py-3 font-medium">USER</th>
                    <th className="px-6 py-3 font-medium">STORES</th>
                    <th className="px-6 py-3 font-medium">PLAN</th>
                    <th className="px-6 py-3 font-medium text-right">ACTIONS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  <tr className="hover:bg-slate-50">
                    <td className="px-6 py-4">
                      <div className="font-bold text-slate-800">Sulaimaani Group</div>
                      <div className="text-xs text-slate-500">admin@example.com</div>
                    </td>
                    <td className="px-6 py-4 text-slate-600">2 connected</td>
                    <td className="px-6 py-4"><span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-2 py-1 rounded">Business</span></td>
                    <td className="px-6 py-4 text-right">
                      <button className="flex items-center gap-2 ml-auto text-blue-600 hover:text-blue-800 font-bold bg-blue-50 hover:bg-blue-100 px-3 py-1.5 rounded transition">
                        <UserCheck className="w-4 h-4"/> Impersonate
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'monitoring' && (
            <div className="space-y-6">
              <div className="grid grid-cols-3 gap-6">
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                  <div className="text-slate-500 font-bold text-xs uppercase mb-1">Celery Queue Depth</div>
                  <div className="text-3xl font-bold text-slate-800">42</div>
                  <div className="text-sm text-emerald-600 mt-2">Processing normally</div>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                  <div className="text-slate-500 font-bold text-xs uppercase mb-1">Failed Tasks (24h)</div>
                  <div className="text-3xl font-bold text-rose-600">3</div>
                  <button className="text-sm text-blue-600 hover:underline mt-2">View tracebacks</button>
                </div>
                <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
                  <div className="text-slate-500 font-bold text-xs uppercase mb-1">Daraz API 429 Rate</div>
                  <div className="text-3xl font-bold text-slate-800">0.05%</div>
                  <div className="text-sm text-emerald-600 mt-2">Below threshold</div>
                </div>
              </div>
              
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="p-6 border-b border-slate-100 bg-slate-50">
                  <h2 className="text-xl font-bold text-slate-800">Slowest Endpoints</h2>
                </div>
                <div className="p-6 text-center text-slate-500 text-sm">
                  Metrics gathering initialized. Awaiting traffic.
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
