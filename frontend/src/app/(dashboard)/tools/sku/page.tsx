"use client";

import React, { useState } from 'react';
import { 
  ArrowLeft, HelpCircle, Search, UploadCloud, Download, 
  Settings2, AlertTriangle, Save, Edit3, X, CheckCircle2
} from 'lucide-react';

export default function SkuSettingsPage() {
  const [editingSku, setEditingSku] = useState<string | null>(null);
  const [isBulkOpen, setIsBulkOpen] = useState(false);
  const [previewData, setPreviewData] = useState<{accepted: number, rejected: any[]} | null>(null);

  // Mock data
  const skus = [
    {
      seller_sku: 'WE-PRO-BLK',
      shop_sku: 'S-WE-PRO-BLK',
      name: 'Wireless Earbuds Pro V2',
      variation: 'Color: Black',
      price: 2500,
      cost_price: 1200,
      packaging_cost: 50,
      other_cost: 10,
      margin: 49.6,
      missing_cost: false
    },
    {
      seller_sku: 'WE-PRO-WHT',
      shop_sku: 'S-WE-PRO-WHT',
      name: 'Wireless Earbuds Pro V2',
      variation: 'Color: White',
      price: 2500,
      cost_price: 0,
      packaging_cost: 0,
      other_cost: 0,
      margin: 100,
      missing_cost: true
    }
  ];

  const handleSimulateUpload = () => {
    // Simulate dry run
    setPreviewData({
      accepted: 1,
      rejected: [{ row: 3, reason: 'SKU INVALID-SKU not found' }]
    });
  };

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
        <div className="flex justify-between items-end mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
              <Settings2 className="w-8 h-8 text-blue-500" /> SKU Cost & Settings
            </h1>
            <p className="text-slate-500 mt-2 text-lg">
              Manage your product catalog costs. These values power all profit calculations.
            </p>
          </div>
          <div className="flex gap-3">
            <button onClick={() => setIsBulkOpen(true)} className="flex items-center gap-2 text-sm font-bold text-slate-700 hover:text-slate-900 border border-slate-200 bg-white px-4 py-2.5 rounded-lg shadow-sm">
              <UploadCloud className="w-4 h-4" /> Bulk Import CSV
            </button>
          </div>
        </div>

        {/* Missing Cost Warning */}
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-8 flex justify-between items-center">
          <div className="flex gap-3 items-center">
            <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center text-amber-600">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-amber-900">Missing Cost Report</h3>
              <p className="text-sm text-amber-800">1 SKU is missing cost data, affecting PKR 2,500.00 of provisional revenue.</p>
            </div>
          </div>
          <button className="text-sm font-bold text-amber-700 bg-amber-100 hover:bg-amber-200 px-4 py-2 rounded-lg transition">
            View Missing SKUs
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm mb-6 flex gap-4">
          <div className="flex-1 max-w-md relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input 
              type="text" 
              placeholder="Search SKUs or Product Names..." 
              className="w-full bg-slate-50 border border-slate-200 rounded-lg pl-10 pr-4 py-2 text-sm outline-none focus:border-blue-500"
            />
          </div>
        </div>

        {/* SKU Table */}
        <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200">
              <tr>
                <th className="px-6 py-3">PRODUCT INFO</th>
                <th className="px-6 py-3">PRICE</th>
                <th className="px-6 py-3">COST PRICE</th>
                <th className="px-6 py-3">PACKAGING</th>
                <th className="px-6 py-3">OTHER</th>
                <th className="px-6 py-3">MARGIN</th>
                <th className="px-6 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {skus.map((sku) => (
                <tr key={sku.seller_sku} className="hover:bg-slate-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-slate-100 rounded border border-slate-200"></div>
                      <div>
                        <div className="font-bold text-slate-800">{sku.name}</div>
                        <div className="text-xs text-slate-500">{sku.seller_sku} &middot; {sku.variation}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-medium text-slate-900">PKR {sku.price}</td>
                  
                  {editingSku === sku.seller_sku ? (
                    <>
                      <td className="px-6 py-4"><input type="number" defaultValue={sku.cost_price} className="w-20 border border-slate-300 rounded px-2 py-1 text-sm outline-none" /></td>
                      <td className="px-6 py-4"><input type="number" defaultValue={sku.packaging_cost} className="w-20 border border-slate-300 rounded px-2 py-1 text-sm outline-none" /></td>
                      <td className="px-6 py-4"><input type="number" defaultValue={sku.other_cost} className="w-20 border border-slate-300 rounded px-2 py-1 text-sm outline-none" /></td>
                      <td className="px-6 py-4">
                        <span className="text-slate-400">Auto</span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button onClick={() => setEditingSku(null)} className="text-emerald-600 bg-emerald-50 p-1.5 rounded hover:bg-emerald-100 mr-2"><Save className="w-4 h-4" /></button>
                        <button onClick={() => setEditingSku(null)} className="text-slate-400 bg-slate-100 p-1.5 rounded hover:bg-slate-200"><X className="w-4 h-4" /></button>
                      </td>
                    </>
                  ) : (
                    <>
                      <td className="px-6 py-4">
                        {sku.missing_cost ? (
                          <span className="text-rose-500 font-bold flex items-center gap-1"><AlertTriangle className="w-3 h-3"/> Missing</span>
                        ) : (
                          `PKR ${sku.cost_price}`
                        )}
                      </td>
                      <td className="px-6 py-4">PKR {sku.packaging_cost}</td>
                      <td className="px-6 py-4">PKR {sku.other_cost}</td>
                      <td className="px-6 py-4 font-bold text-slate-700">{sku.margin}%</td>
                      <td className="px-6 py-4 text-right">
                        <button onClick={() => setEditingSku(sku.seller_sku)} className="text-slate-400 hover:text-blue-600"><Edit3 className="w-4 h-4" /></button>
                      </td>
                    </>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bulk Import Overlay */}
      {isBulkOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg overflow-hidden animate-in zoom-in-95 duration-200">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50">
              <h2 className="text-xl font-bold text-slate-800">Bulk Import SKU Costs</h2>
              <button onClick={() => {setIsBulkOpen(false); setPreviewData(null);}} className="text-slate-400 hover:text-slate-600"><X className="w-5 h-5" /></button>
            </div>
            
            <div className="p-6 space-y-6">
              {!previewData ? (
                <>
                  <div className="flex gap-4">
                    <button className="flex-1 flex items-center justify-center gap-2 text-sm font-bold text-slate-700 bg-white border border-slate-200 hover:bg-slate-50 py-3 rounded-lg transition">
                      <Download className="w-4 h-4 text-emerald-600" /> Download Template
                    </button>
                  </div>
                  <div className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center bg-slate-50 hover:bg-slate-100 transition cursor-pointer" onClick={handleSimulateUpload}>
                    <UploadCloud className="w-8 h-8 text-slate-400 mx-auto mb-3" />
                    <div className="text-sm font-bold text-blue-600">Click to upload CSV</div>
                    <div className="text-xs text-slate-500 mt-1">Populate the template and upload it here</div>
                  </div>
                </>
              ) : (
                <div className="space-y-4">
                  <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 flex gap-3 items-center">
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 flex-shrink-0" />
                    <div>
                      <h4 className="font-bold text-emerald-900">Valid Rows: {previewData.accepted}</h4>
                      <p className="text-sm text-emerald-800">These SKUs will be updated.</p>
                    </div>
                  </div>
                  
                  {previewData.rejected.length > 0 && (
                    <div className="bg-rose-50 border border-rose-200 rounded-lg p-4">
                      <h4 className="font-bold text-rose-900 flex items-center gap-2 mb-2">
                        <AlertTriangle className="w-4 h-4" /> Rejected Rows: {previewData.rejected.length}
                      </h4>
                      <p className="text-sm text-rose-800 mb-3">Please fix these errors in your CSV and re-upload.</p>
                      <ul className="text-xs text-rose-700 space-y-1 font-mono bg-white p-2 rounded border border-rose-100">
                        {previewData.rejected.map((r, i) => (
                          <li key={i}>Row {r.row}: {r.reason}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  <div className="pt-4 flex gap-3">
                    <button onClick={() => setPreviewData(null)} className="flex-1 text-slate-600 bg-slate-100 font-bold py-2.5 rounded-lg hover:bg-slate-200">Start Over</button>
                    <button disabled={previewData.rejected.length > 0} className={`flex-1 font-bold py-2.5 rounded-lg text-white transition ${previewData.rejected.length > 0 ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'}`}>
                      Commit Updates
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
