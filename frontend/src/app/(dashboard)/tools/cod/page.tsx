"use client";

import React, { useState } from 'react';
import { 
  ArrowLeft, HelpCircle, Wallet, FileX, AlertTriangle, Search, ChevronDown, 
  Download, FileSpreadsheet, FileText, AlertOctagon, CheckCircle2, ChevronRight
} from 'lucide-react';

export default function FinanceAuditPage() {
  const [hasRun, setHasRun] = useState(false);
  const [isExporting, setIsExporting] = useState(false);

  // Mock data for post-run state
  const mockAudit = {
    gross: 450000,
    deductions: -35000,
    net: 415000,
    expected_profit: 405000,
    actual_profit: 395000,
    difference: -10000,
    issues: [
      { id: 1, type: 'MISSING_PAYMENT', severity: 'critical', title: 'Missing Payout', desc: 'Order 12345 delivered 16 days ago but no settlement.', impact: 5000 },
      { id: 2, type: 'DOUBLE_DEDUCTION', severity: 'critical', title: 'Double Deduction', desc: 'Duplicate Shipping Fee charged on Order 67890.', impact: 150 },
      { id: 3, type: 'SUSPICIOUS_FEE', severity: 'warning', title: 'High Shipping Fee', desc: 'Shipping fee of PKR 800 is 40% above median.', impact: 800 }
    ]
  };

  const handleRunAudit = () => {
    setHasRun(true);
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
        {/* 2. Heading */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 flex items-center gap-3">
            💰 Daraz Finance Audit
          </h1>
          <p className="text-slate-500 mt-2 text-lg">
            Understand your Daraz Seller Center income, deductions, and net payout in one simple dashboard.
          </p>
        </div>

        {/* 3. Amber Panel */}
        <div className="bg-amber-100/50 border border-amber-200 rounded-xl p-6 mb-8">
          <h2 className="text-sm font-bold text-amber-800 uppercase tracking-wider mb-4">What this tool helps you understand</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-white p-5 rounded-xl border border-amber-100 shadow-sm">
              <div className="w-10 h-10 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center mb-3">
                <Wallet className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-800 mb-1">Income Summary</h3>
              <p className="text-sm text-slate-500 leading-snug">See revenue, deductions and net amount, comparable to Seller Center Income Details</p>
            </div>
            <div className="bg-white p-5 rounded-xl border border-amber-100 shadow-sm">
              <div className="w-10 h-10 bg-purple-100 text-purple-600 rounded-lg flex items-center justify-center mb-3">
                <FileX className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-800 mb-1">Deduction Clarity</h3>
              <p className="text-sm text-slate-500 leading-snug">How much Daraz deducted through fees, charges, taxes and adjustments</p>
            </div>
            <div className="bg-white p-5 rounded-xl border border-amber-100 shadow-sm">
              <div className="w-10 h-10 bg-rose-100 text-rose-600 rounded-lg flex items-center justify-center mb-3">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h3 className="font-bold text-slate-800 mb-1">Issue Detection</h3>
              <p className="text-sm text-slate-500 leading-snug">Highlight suspicious finance records or orders needing manual review</p>
            </div>
          </div>
          <div className="bg-white/80 rounded-lg p-3 text-sm text-amber-800 font-medium flex gap-2 items-center">
            <span className="bg-amber-200 text-amber-900 px-2 py-0.5 rounded text-xs font-bold">TIP</span>
            Compare Finance Revenue, Finance Deductions and Finance Net Total with Daraz Seller Center Income Details for the same range.
          </div>
        </div>

        {/* 4. Controls Card */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm mb-8 flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase tracking-wide">Store</label>
            <div className="relative">
              <select className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm font-medium text-slate-800 outline-none appearance-none">
                <option>store@example.com - PK</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            </div>
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase tracking-wide">Period (delivered orders)</label>
            <div className="relative">
              <select className="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2.5 text-sm font-medium text-slate-800 outline-none appearance-none">
                <option>Last 30 days</option>
                <option>Last 7 days</option>
                <option>Last 60 days</option>
                <option>Last 90 days</option>
                <option>Custom</option>
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 pointer-events-none" />
            </div>
          </div>
          <button 
            onClick={handleRunAudit}
            className="bg-orange-500 hover:bg-orange-600 text-white font-bold px-6 py-2.5 rounded-lg flex items-center gap-2 shadow-sm transition h-[42px]">
            <Search className="w-4 h-4" /> Analyze Finance
          </button>
        </div>

        {/* 5. Pre-run State */}
        {!hasRun && (
          <div className="py-24 text-center border-2 border-dashed border-slate-200 rounded-2xl bg-slate-50/50">
            <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-400">
              <Search className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-bold text-slate-700 mb-2">Ready to audit your finances?</h3>
            <p className="text-slate-500">Select a store and period above, then click Analyze Finance.</p>
          </div>
        )}

        {/* 6. Post-run State (The Report) */}
        {hasRun && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Action Bar */}
            <div className="flex justify-end gap-3">
              <button className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 border border-slate-200 bg-white px-4 py-2 rounded-lg shadow-sm">
                <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> Export Excel
              </button>
              <button className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 border border-slate-200 bg-white px-4 py-2 rounded-lg shadow-sm">
                <FileText className="w-4 h-4 text-slate-400" /> Export CSV
              </button>
              <button className="flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 border border-slate-200 bg-white px-4 py-2 rounded-lg shadow-sm">
                <Download className="w-4 h-4 text-rose-500" /> Export PDF
              </button>
            </div>

            {/* Waterfall & Deductions */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <h3 className="text-lg font-bold text-slate-800 mb-6">Income Waterfall</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-4 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="font-bold text-slate-600">Gross Revenue</span>
                    <span className="font-bold text-slate-900">Rs. {mockAudit.gross.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-rose-50 rounded-lg border border-rose-100">
                    <span className="font-bold text-rose-700">Total Deductions</span>
                    <span className="font-bold text-rose-700">Rs. {mockAudit.deductions.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between items-center p-4 bg-emerald-50 rounded-lg border border-emerald-100">
                    <span className="font-bold text-emerald-700 text-lg">Net Payout</span>
                    <span className="font-bold text-emerald-700 text-lg">Rs. {mockAudit.net.toLocaleString()}</span>
                  </div>
                </div>

                <div className="mt-8 pt-6 border-t border-slate-200">
                  <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Profit Reconcilation</h4>
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-slate-500">Expected Profit</div>
                      <div className="font-bold text-slate-800">Rs. {mockAudit.expected_profit.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-sm text-slate-500">Actual Profit</div>
                      <div className="font-bold text-slate-800">Rs. {mockAudit.actual_profit.toLocaleString()}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-slate-500">Difference</div>
                      <div className={`font-bold ${mockAudit.difference < 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                        Rs. {mockAudit.difference.toLocaleString()}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                <h3 className="text-lg font-bold text-slate-800 mb-6">Deduction Breakdown</h3>
                <div className="space-y-0">
                  {[
                    { label: 'Commission', amount: -22000, pct: '4.8%' },
                    { label: 'Payment Fee', amount: -6000, pct: '1.3%' },
                    { label: 'Shipping Fee', amount: -4000, pct: '0.8%' },
                    { label: 'Taxes & VAT', amount: -3000, pct: '0.6%' }
                  ].map((fee, idx) => (
                    <div key={idx} className="flex justify-between items-center py-3 border-b border-slate-100 last:border-0">
                      <span className="text-slate-600 font-medium">{fee.label}</span>
                      <div className="text-right">
                        <div className="font-bold text-rose-600">Rs. {fee.amount.toLocaleString()}</div>
                        <div className="text-xs text-slate-400">{fee.pct} of revenue</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Issues List */}
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
              <div className="p-6 border-b border-slate-200 bg-slate-50 flex justify-between items-center">
                <div>
                  <h3 className="text-lg font-bold text-slate-800">Detected Issues ({mockAudit.issues.length})</h3>
                  <p className="text-sm text-slate-500">These anomalies were found in your payout statements.</p>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium text-slate-500">Total Impact</div>
                  <div className="text-xl font-bold text-rose-600">Rs. {mockAudit.issues.reduce((acc, i) => acc + i.impact, 0).toLocaleString()}</div>
                </div>
              </div>
              <div className="divide-y divide-slate-100">
                {mockAudit.issues.map(issue => (
                  <details key={issue.id} className="group">
                    <summary className="flex items-center gap-4 p-4 cursor-pointer hover:bg-slate-50 list-none">
                      <div className="w-8 flex justify-center">
                        {issue.severity === 'critical' ? (
                          <AlertOctagon className="w-5 h-5 text-rose-500" />
                        ) : (
                          <AlertTriangle className="w-5 h-5 text-amber-500" />
                        )}
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-slate-800">{issue.title}</span>
                          <span className="bg-slate-100 text-slate-600 text-[10px] font-bold px-2 py-0.5 rounded uppercase">{issue.type}</span>
                        </div>
                        <div className="text-sm text-slate-500 mt-0.5">{issue.desc}</div>
                      </div>
                      <div className="text-right pr-4">
                        <div className="font-bold text-rose-600">Rs. {issue.impact.toLocaleString()}</div>
                      </div>
                      <ChevronRight className="w-5 h-5 text-slate-300 group-open:rotate-90 transition-transform" />
                    </summary>
                    <div className="p-4 pl-16 bg-slate-50 border-t border-slate-100 text-sm">
                      <div className="mb-3 font-medium text-slate-700">Evidence for Daraz Claim:</div>
                      <pre className="bg-slate-800 text-slate-300 p-3 rounded-lg text-xs overflow-x-auto">
                        {JSON.stringify({ order_id: 123, transaction_ids: ["TX-999"] }, null, 2)}
                      </pre>
                      <div className="mt-4 flex gap-2">
                        <button className="bg-white border border-slate-200 text-slate-700 px-3 py-1.5 rounded text-xs font-bold hover:bg-slate-100 flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-500" /> Mark as Resolved
                        </button>
                      </div>
                    </div>
                  </details>
                ))}
              </div>
            </div>

            {/* 7. Recent Audits */}
            <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden mt-12">
              <div className="p-5 border-b border-slate-200 flex justify-between items-center">
                <h3 className="font-bold text-slate-800">Recent Audits</h3>
                <button className="text-sm font-medium text-slate-600 hover:text-slate-900 border border-slate-200 px-3 py-1.5 rounded-lg flex items-center gap-2">
                  <RefreshCw className="w-4 h-4" /> Refresh
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-50 text-slate-500 font-medium border-b border-slate-200">
                    <tr>
                      <th className="px-6 py-3">STORE</th>
                      <th className="px-6 py-3">PERIOD</th>
                      <th className="px-6 py-3">DATE</th>
                      <th className="px-6 py-3 text-right">ORDERS</th>
                      <th className="px-6 py-3 text-right">LOSS</th>
                      <th className="px-6 py-3">STATUS</th>
                      <th className="px-6 py-3"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    <tr className="hover:bg-slate-50">
                      <td className="px-6 py-4 font-medium text-slate-800">store@example.com</td>
                      <td className="px-6 py-4 text-slate-600">Last 30 Days</td>
                      <td className="px-6 py-4 text-slate-500">12 Aug 2026</td>
                      <td className="px-6 py-4 text-right text-slate-700 font-medium">1,402</td>
                      <td className="px-6 py-4 text-right font-bold text-rose-600">Rs. 10,000</td>
                      <td className="px-6 py-4">
                        <span className="bg-emerald-100 text-emerald-700 text-xs font-bold px-2 py-1 rounded uppercase">Done</span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button className="text-orange-600 font-medium hover:text-orange-700">View</button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}
