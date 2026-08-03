"use client";

import React, { useState } from 'react';
import { User, Bell, Shield, Key, Smartphone, Trash2, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile');

  return (
    <div className="min-h-screen bg-slate-50 pb-24">
      <div className="max-w-7xl mx-auto px-4 pt-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-8">Account Settings</h1>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
          {/* Sidebar */}
          <div className="md:col-span-3 space-y-1">
            <button 
              onClick={() => setActiveTab('profile')}
              className={`w-full text-left px-4 py-3 rounded-lg font-medium flex items-center gap-3 transition ${activeTab === 'profile' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-100'}`}
            >
              <User className="w-5 h-5" /> Profile & Business
            </button>
            <button 
              onClick={() => setActiveTab('notifications')}
              className={`w-full text-left px-4 py-3 rounded-lg font-medium flex items-center gap-3 transition ${activeTab === 'notifications' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-100'}`}
            >
              <Bell className="w-5 h-5" /> Notifications
            </button>
            <button 
              onClick={() => setActiveTab('security')}
              className={`w-full text-left px-4 py-3 rounded-lg font-medium flex items-center gap-3 transition ${activeTab === 'security' ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:bg-slate-100'}`}
            >
              <Shield className="w-5 h-5" /> Security & Sessions
            </button>
            <button 
              onClick={() => setActiveTab('danger')}
              className={`w-full text-left px-4 py-3 rounded-lg font-medium flex items-center gap-3 transition ${activeTab === 'danger' ? 'bg-rose-50 text-rose-700' : 'text-slate-600 hover:bg-slate-100'}`}
            >
              <Trash2 className="w-5 h-5" /> Danger Zone
            </button>
          </div>

          {/* Main Content */}
          <div className="md:col-span-9 space-y-6">
            
            {activeTab === 'profile' && (
              <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
                <div className="p-6 border-b border-slate-100">
                  <h2 className="text-xl font-bold text-slate-800">Business Profile</h2>
                  <p className="text-sm text-slate-500 mt-1">Manage your company details and timezone preferences.</p>
                </div>
                <div className="p-6 space-y-6">
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-bold text-slate-700 mb-2">Business Name</label>
                      <input type="text" defaultValue="Tech Accessories PK" className="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-slate-700 mb-2">Support Phone</label>
                      <input type="text" defaultValue="+92 300 1234567" className="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-slate-700 mb-2">Timezone</label>
                      <select className="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm outline-none focus:border-blue-500">
                        <option>Asia/Karachi (PKT)</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div className="p-6 border-t border-slate-100 bg-slate-50 flex justify-end">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-6 py-2.5 rounded-lg transition">Save Changes</button>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
                <div className="p-6 border-b border-slate-100">
                  <h2 className="text-xl font-bold text-slate-800">Notification Preferences</h2>
                  <p className="text-sm text-slate-500 mt-1">Choose how and when you want to be alerted by the beat scanner.</p>
                </div>
                <div className="p-0">
                  <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 border-b border-slate-100">
                      <tr>
                        <th className="px-6 py-3 font-medium text-slate-500">TRIGGER EVENT</th>
                        <th className="px-6 py-3 font-medium text-slate-500 text-center">IN-APP</th>
                        <th className="px-6 py-3 font-medium text-slate-500 text-center">EMAIL</th>
                        <th className="px-6 py-3 font-medium text-slate-500 text-center">SMS (Pro)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {[
                        { name: 'Claim deadline in 24h', inapp: true, email: true, sms: true },
                        { name: 'Finance missing payout', inapp: true, email: true, sms: false },
                        { name: 'Daraz token expiry warning', inapp: true, email: true, sms: true },
                        { name: 'Store sync completed', inapp: true, email: false, sms: false },
                      ].map((pref, i) => (
                        <tr key={i}>
                          <td className="px-6 py-4 font-medium text-slate-800">{pref.name}</td>
                          <td className="px-6 py-4 text-center"><input type="checkbox" defaultChecked={pref.inapp} className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500" /></td>
                          <td className="px-6 py-4 text-center"><input type="checkbox" defaultChecked={pref.email} className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500" /></td>
                          <td className="px-6 py-4 text-center"><input type="checkbox" defaultChecked={pref.sms} disabled={!pref.sms} className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 disabled:opacity-50" /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="p-6 border-t border-slate-100 bg-slate-50 flex justify-end">
                  <button className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-6 py-2.5 rounded-lg transition">Update Matrix</button>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <>
                <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden mb-6">
                  <div className="p-6 border-b border-slate-100">
                    <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2"><Key className="w-5 h-5"/> Change Password</h2>
                  </div>
                  <div className="p-6 space-y-4 max-w-md">
                    <div>
                      <label className="block text-sm font-bold text-slate-700 mb-2">Current Password</label>
                      <input type="password" placeholder="••••••••" className="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-slate-700 mb-2">New Password</label>
                      <input type="password" placeholder="••••••••" className="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
                    </div>
                    <button className="bg-slate-800 hover:bg-slate-900 text-white font-bold px-6 py-2.5 rounded-lg transition mt-2">Update Password</button>
                  </div>
                </div>

                <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
                  <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                    <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2"><Smartphone className="w-5 h-5"/> Active Sessions</h2>
                    <button className="text-sm font-bold text-rose-600 hover:text-rose-700">Revoke All Others</button>
                  </div>
                  <div className="p-0">
                    <div className="flex items-center justify-between p-6 border-b border-slate-100">
                      <div>
                        <div className="font-bold text-slate-800 flex items-center gap-2">Windows &middot; Chrome <span className="bg-emerald-100 text-emerald-700 text-[10px] uppercase px-2 py-0.5 rounded font-bold">Current</span></div>
                        <div className="text-sm text-slate-500 mt-1">Karachi, PK &middot; IP 103.24.12.1</div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between p-6">
                      <div>
                        <div className="font-bold text-slate-800">iOS &middot; Safari</div>
                        <div className="text-sm text-slate-500 mt-1">Lahore, PK &middot; Last active 2h ago</div>
                      </div>
                      <button className="text-sm font-bold text-slate-500 border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50">Revoke</button>
                    </div>
                  </div>
                </div>
              </>
            )}

            {activeTab === 'danger' && (
              <div className="bg-white border border-rose-200 rounded-xl shadow-sm overflow-hidden">
                <div className="p-6 border-b border-rose-100 bg-rose-50/50">
                  <h2 className="text-xl font-bold text-rose-800 flex items-center gap-2"><AlertTriangle className="w-5 h-5"/> Delete Account (GDPR)</h2>
                  <p className="text-sm text-rose-700 mt-1 max-w-2xl">
                    Once you delete your account, there is no going back. A 30-day grace period applies during which your data is soft-deleted, after which all PII is permanently scrubbed.
                  </p>
                </div>
                <div className="p-6 space-y-4 max-w-md">
                  <div>
                    <label className="block text-sm font-bold text-slate-700 mb-2">To verify, type <span className="font-mono text-rose-600 bg-rose-50 px-1 rounded">delete my account</span> below:</label>
                    <input type="text" className="w-full border border-slate-200 rounded-lg px-4 py-2.5 text-sm outline-none focus:border-rose-500" />
                  </div>
                  <button className="bg-rose-600 hover:bg-rose-700 text-white font-bold px-6 py-2.5 rounded-lg transition mt-2 flex items-center gap-2">
                    <Trash2 className="w-4 h-4"/> Delete Account
                  </button>
                </div>
              </div>
            )}
            
          </div>
        </div>
      </div>
    </div>
  );
}
