"use client";

import React, { useState } from 'react';
import { 
  ArrowLeft, HelpCircle, Search, Camera, Wallet, RefreshCw, 
  AlertCircle, Clock, CheckCircle2, AlertTriangle, FileText,
  UploadCloud, X
} from 'lucide-react';

export default function ReturnsManagerPage() {
  const [activeQueue, setActiveQueue] = useState('Late Claim');
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 pb-24">
      {/* 1. Top navigation */}
      <div className="max-w-7xl mx-auto px-4 pt-6 flex justify-between items-center">
        <a href="#" className="flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-slate-800">
          <ArrowLeft className="w-4 h-4" /> Back to tools
        </a>
        <button className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 border border-slate-200 bg-white px-3 py-1.5 rounded-lg shadow-sm">
          <HelpCircle className="w-4 h-4" /> Guide me
        </button>
      </div>

      <div className="max-w-7xl mx-auto px-4 mt-6">
        {/* 1. Header (Amber Panel) */}
        <div className="bg-amber-100/50 border border-amber-200 rounded-xl p-6 mb-8">
          <h2 className="text-sm font-bold text-amber-800 uppercase tracking-wider mb-2">RETURN OPERATIONS</h2>
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3 mb-2">
            📦 Return & Claim Manager
          </h1>
          <p className="text-slate-600 font-medium">
            ONE PHYSICAL PACKAGE APPEARS IN EXACTLY ONE OPERATIONAL QUEUE.
          </p>
          <p className="text-sm text-slate-500 mt-1">
            Lifecycle, claim, finance and evidence quality are shown as supporting badges, never as competing queues.
          </p>
        </div>

        {/* 2. Toolbar */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm mb-8 flex flex-wrap gap-4 items-center justify-between">
          <div className="flex items-center gap-4 flex-1">
            <select className="bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm font-medium text-slate-800 outline-none w-48">
              <option>All Stores</option>
            </select>
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input 
                type="text" 
                placeholder="Search all queues: order, return ID, tracking, SKU..." 
                className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-10 pr-4 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button className="flex items-center gap-2 text-sm font-bold text-slate-700 hover:text-slate-900 border border-slate-200 bg-white px-4 py-2.5 rounded-lg shadow-sm">
              <Camera className="w-4 h-4 text-blue-500" /> Scan Returns
            </button>
            <button className="flex items-center gap-2 text-sm font-bold text-slate-700 hover:text-slate-900 border border-slate-200 bg-white px-4 py-2.5 rounded-lg shadow-sm">
              <Wallet className="w-4 h-4 text-emerald-500" /> Check Finance
            </button>
            <button className="flex items-center gap-2 text-sm font-bold text-white bg-orange-500 hover:bg-orange-600 px-4 py-2.5 rounded-lg shadow-sm transition">
              <RefreshCw className="w-4 h-4" /> Sync All Stores
            </button>
          </div>
        </div>

        {/* 3. Queue Groups */}
        <div className="space-y-6 mb-12">
          {/* Action Required */}
          <div className="border border-slate-200 rounded-xl bg-white overflow-hidden shadow-sm relative">
            <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-rose-500"></div>
            <div className="p-4 border-b border-slate-100 flex justify-between items-center pl-6">
              <div>
                <h3 className="font-bold text-slate-800 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-rose-500" /> ACTION REQUIRED
                </h3>
              </div>
              <span className="bg-rose-100 text-rose-700 text-xs font-bold px-2 py-0.5 rounded-full">12</span>
            </div>
            <div className="p-4 pl-6 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-3 border border-slate-200 rounded-lg hover:border-blue-500 cursor-pointer transition">
                <div className="font-bold text-slate-800 mb-1">Need Checking</div>
                <div className="text-2xl font-bold text-rose-600 mb-1">4</div>
                <div className="text-xs text-slate-500 leading-tight">Inspect the returned parcel and record condition</div>
              </div>
              <div className="p-3 border border-slate-200 rounded-lg hover:border-blue-500 cursor-pointer transition">
                <div className="font-bold text-slate-800 mb-1">Claim Required</div>
                <div className="text-2xl font-bold text-rose-600 mb-1">2</div>
                <div className="text-xs text-slate-500 leading-tight">Claim action required inside valid window</div>
              </div>
              <div className="p-3 border-2 border-blue-500 bg-blue-50/50 rounded-lg cursor-pointer relative">
                <div className="absolute -top-2.5 -right-2.5 bg-blue-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">Active</div>
                <div className="font-bold text-blue-900 mb-1">Late Claim</div>
                <div className="text-2xl font-bold text-rose-600 mb-1">1</div>
                <div className="text-xs text-blue-700/70 leading-tight">Official window passed; record late filing</div>
              </div>
              <div className="p-3 border border-slate-200 rounded-lg hover:border-blue-500 cursor-pointer transition">
                <div className="font-bold text-slate-800 mb-1">Payout Follow-up</div>
                <div className="text-2xl font-bold text-rose-600 mb-1">5</div>
                <div className="text-xs text-slate-500 leading-tight">Approved/partial payout missing follow-up</div>
              </div>
            </div>
          </div>

          {/* Review Group */}
          <div className="border border-slate-200 rounded-xl bg-white overflow-hidden shadow-sm relative">
            <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-amber-400"></div>
            <div className="p-4 border-b border-slate-100 flex justify-between items-center pl-6">
              <div>
                <h3 className="font-bold text-slate-800 flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-amber-500" /> REVIEW
                </h3>
              </div>
              <span className="bg-amber-100 text-amber-700 text-xs font-bold px-2 py-0.5 rounded-full">3</span>
            </div>
            <div className="p-4 pl-6 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-3 border border-slate-200 rounded-lg hover:border-blue-500 cursor-pointer transition">
                <div className="font-bold text-slate-800 mb-1">Review Rejected Claim</div>
                <div className="text-2xl font-bold text-amber-600 mb-1">3</div>
                <div className="text-xs text-slate-500 leading-tight">Review Daraz rejection and decide next step</div>
              </div>
              <div className="p-3 border border-slate-200 rounded-lg hover:border-blue-500 cursor-pointer transition">
                <div className="font-bold text-slate-800 mb-1">Needs Data Review</div>
                <div className="text-2xl font-bold text-amber-600 mb-1">0</div>
                <div className="text-xs text-slate-500 leading-tight">Evidence incomplete or ambiguous for deadline</div>
              </div>
            </div>
          </div>

        </div>

        {/* 4. Active Queue Bar */}
        <div className="flex justify-between items-center bg-slate-800 text-white p-3 rounded-t-xl px-6">
          <div className="text-sm font-medium">
            Active queue: <span className="font-bold text-blue-300">{activeQueue}</span> &middot; Showing 1 of 1 &middot; Classified: 1/1 packages &middot; Item records: 1
          </div>
          <div>
            <button className="text-xs font-bold bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded transition">Export Excel</button>
          </div>
        </div>

        {/* 5. Package Card */}
        <div className="border-x border-b border-slate-200 bg-white rounded-b-xl shadow-sm overflow-hidden relative">
          <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-rose-500"></div>
          
          <div className="p-6 pl-8">
            {/* Top Pill Row */}
            <div className="flex gap-2 mb-6">
              <span className="bg-rose-100 text-rose-700 text-xs font-bold px-2.5 py-1 rounded-full flex items-center gap-1">
                <Clock className="w-3 h-3" /> ⌛ Late Claim / Missed Window
              </span>
              <span className="bg-slate-100 text-slate-600 text-xs font-bold px-2.5 py-1 rounded-full">Lifecycle: Returned to Seller</span>
              <span className="bg-slate-100 text-slate-600 text-xs font-bold px-2.5 py-1 rounded-full">Full package return</span>
              <span className="bg-slate-100 text-slate-600 text-xs font-bold px-2.5 py-1 rounded-full">Store: seller@example.com</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-6">
              {/* Left Column */}
              <div>
                <div className="text-sm text-slate-500 mb-1">TRACKING NO.</div>
                <div className="text-xl font-bold text-slate-900 mb-4">PK-DX-999888777</div>
                
                <div className="text-sm text-slate-600 mb-1">Order: <span className="font-medium text-slate-900">1234567890</span></div>
                <div className="text-sm text-slate-600 mb-4">Daraz last update: <span className="font-medium text-slate-900">29-Jun-2026, 09:41 am</span></div>
                
                <div className="font-bold text-slate-800">Full package return &middot; 1 product line &middot; qty 1</div>
              </div>

              {/* Right Column */}
              <div>
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <div className="text-sm text-slate-500 mb-1">ITEM VALUE</div>
                    <div className="text-3xl font-bold text-slate-900">PKR 469.00</div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-slate-500 mb-1">OPERATIONAL STATUS</div>
                    <span className="bg-rose-50 text-rose-700 border border-rose-200 text-sm font-bold px-3 py-1 rounded-lg inline-block">Late Claim</span>
                  </div>
                </div>

                <div className="bg-slate-50 p-3 rounded-lg text-sm text-slate-600 mb-4 leading-relaxed">
                  Parcel returned on <span className="font-bold">2026-06-29T09:41:34</span> (source: <code className="bg-slate-200 px-1 rounded">daraz_status_updated_at</code>); 
                  the 5-business-day inspection window closed on <span className="font-bold text-rose-600">2026-07-06T09:41:34</span> with no inspection recorded.
                </div>

                <div className="flex flex-wrap gap-2 mb-4">
                  <span className="bg-slate-100 text-slate-600 text-xs font-bold px-2 py-1 rounded border border-slate-200">Claim: Not filed</span>
                  <span className="bg-slate-100 text-slate-600 text-xs font-bold px-2 py-1 rounded border border-slate-200">Finance: Not checked</span>
                  <span className="bg-emerald-50 text-emerald-700 text-xs font-bold px-2 py-1 rounded border border-emerald-200">Data: Evidence OK</span>
                </div>

                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 text-sm text-amber-800 font-medium mb-3">
                  Next: File late claim manually and accept penalty risk.
                </div>

                <div className="text-xs text-slate-400 font-medium">
                  Deadline: 2026-07-06 09:41 &middot; source: daraz_status_updated_at
                </div>
              </div>
            </div>

            {/* 5. Item Rows */}
            <div className="border border-slate-200 rounded-xl overflow-hidden mt-6">
              <div className="p-4 flex gap-6 items-start bg-white">
                <div className="text-center w-20 flex-shrink-0">
                  <div className="font-bold text-slate-800">Qty &times;1</div>
                  <div className="text-xs text-slate-500 mb-2">of 1 ordered</div>
                  <div className="w-16 h-16 bg-slate-100 rounded-lg mx-auto border border-slate-200"></div>
                </div>
                
                <div className="flex-1">
                  <div className="font-bold text-slate-800 mb-1 text-lg">Wireless Earbuds Pro V2</div>
                  <div className="text-sm text-slate-500 mb-3">SKU: WE-PRO-BLK &middot; Item ID: 9988776655</div>
                  
                  <div className="flex gap-2 mb-4">
                    <span className="bg-slate-100 text-slate-600 text-[10px] font-bold px-2 py-0.5 rounded uppercase">Daraz: Package Returned</span>
                    <span className="bg-amber-100 text-amber-700 text-[10px] font-bold px-2 py-0.5 rounded uppercase">Check: Needs Checking</span>
                    <span className="bg-slate-100 text-slate-600 text-[10px] font-bold px-2 py-0.5 rounded uppercase">Claim: Not Filed</span>
                  </div>

                  <div className="bg-slate-100 px-3 py-1.5 text-xs text-slate-600 font-medium rounded mb-4 inline-block">
                    Claim deadline: 2026-07-06 09:41
                  </div>

                  {/* Condition Buttons */}
                  <div className="flex flex-wrap gap-2">
                    <button className="bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 text-xs font-bold px-4 py-2 rounded-lg transition">Received OK</button>
                    <button onClick={() => setIsDrawerOpen(true)} className="bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-200 text-xs font-bold px-4 py-2 rounded-lg transition">Damaged</button>
                    <button onClick={() => setIsDrawerOpen(true)} className="bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-bold px-4 py-2 rounded-lg transition">Wrong Item</button>
                    <button onClick={() => setIsDrawerOpen(true)} className="bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-bold px-4 py-2 rounded-lg transition">Missing</button>
                    <button onClick={() => setIsDrawerOpen(true)} className="bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-bold px-4 py-2 rounded-lg transition">Accessories Missing</button>
                    <button onClick={() => setIsDrawerOpen(true)} className="bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 text-xs font-bold px-4 py-2 rounded-lg transition">Package Not Received</button>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>

      {/* 6. Claim Drawer (Overlay) */}
      {isDrawerOpen && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm" onClick={() => setIsDrawerOpen(false)}></div>
          <div className="relative w-full max-w-xl bg-white h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-slate-800">File Claim</h2>
                <p className="text-sm text-slate-500">Tracking: PK-DX-999888777</p>
              </div>
              <button onClick={() => setIsDrawerOpen(false)} className="p-2 hover:bg-slate-100 rounded-full text-slate-500">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              <div className="bg-amber-50 border border-amber-200 p-4 rounded-lg">
                <h3 className="font-bold text-amber-800 flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-4 h-4" /> Late Filing Warning
                </h3>
                <p className="text-sm text-amber-900/80 mb-3">
                  The inspection window for this package closed on 2026-07-06. Daraz may reject this claim automatically.
                </p>
                <label className="flex items-start gap-3">
                  <input type="checkbox" className="mt-1 w-4 h-4 rounded border-amber-300 text-amber-600 focus:ring-amber-500" />
                  <span className="text-sm font-medium text-amber-900">I acknowledge this is a late filing and assume the risk of rejection.</span>
                </label>
              </div>

              <div>
                <label className="block text-sm font-bold text-slate-700 mb-2">Condition Recorded</label>
                <div className="bg-slate-50 border border-slate-200 px-4 py-2 rounded-lg text-slate-800 font-medium inline-block">
                  Damaged
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-slate-700 mb-2">Evidence Upload (Images & Video)</label>
                <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center bg-slate-50 hover:bg-slate-100 transition cursor-pointer">
                  <UploadCloud className="w-8 h-8 text-slate-400 mx-auto mb-3" />
                  <div className="text-sm font-bold text-blue-600">Click to upload or drag and drop</div>
                  <div className="text-xs text-slate-500 mt-1">SVG, PNG, JPG or MP4 (max. 10MB)</div>
                  <div className="text-xs text-emerald-600 font-medium mt-2">✓ EXIF metadata will be stripped automatically</div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-bold text-slate-700 mb-2">Claim Notes</label>
                <textarea className="w-full border border-slate-200 rounded-lg p-3 text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none h-24" placeholder="Describe the damage or issue..."></textarea>
              </div>

              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="block text-sm font-bold text-slate-700 mb-2">Expected Refund</label>
                  <div className="bg-slate-100 border border-slate-200 px-4 py-2.5 rounded-lg text-slate-500 font-medium">
                    PKR 469.00
                  </div>
                </div>
                <div className="flex-1">
                  <label className="block text-sm font-bold text-slate-700 mb-2">Claim Amount</label>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 font-medium text-sm">PKR</span>
                    <input type="number" defaultValue="469.00" className="w-full border border-slate-200 rounded-lg pl-12 pr-4 py-2.5 text-sm font-bold text-slate-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none" />
                  </div>
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-slate-100 bg-slate-50 flex gap-3">
              <button onClick={() => setIsDrawerOpen(false)} className="flex-1 bg-white border border-slate-200 text-slate-700 font-bold px-4 py-2.5 rounded-lg hover:bg-slate-50 transition">Cancel</button>
              <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold px-4 py-2.5 rounded-lg transition">Submit Claim</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
