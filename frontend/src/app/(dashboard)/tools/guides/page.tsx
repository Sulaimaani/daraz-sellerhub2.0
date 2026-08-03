"use client";

import React, { useState } from 'react';
import { BookOpen, Search, ArrowRight, Book, HelpCircle } from 'lucide-react';

export default function GuidesPage() {
  const [search, setSearch] = useState('');
  
  const guides = [
    { id: 'connect-store', category: 'Getting Started', title: 'Connecting a Daraz Store', summary: 'Learn how to securely authenticate and link your Seller Center account.' },
    { id: 'understanding-120-sync', category: 'Sync Engine', title: 'Understanding the 120-day Import', summary: 'How the sync engine safely pulls 120 days of historical orders and finance records.' },
    { id: 'profit-confidence', category: 'Finance', title: 'Reading Profit Numbers & Confidence Levels', summary: 'What FINAL vs PROVISIONAL means and why SKU costs matter.' },
    { id: 'label-templates', category: 'Fulfillment', title: 'Designing a Label Template', summary: 'How to overlay custom barcodes and fragile warnings on Daraz shipping labels.' },
    { id: 'finance-audit', category: 'Finance', title: 'Running a Finance Audit', summary: 'Identify missing payouts and suspicious fees with automated daily audits.' },
    { id: 'returns-queues', category: 'Returns', title: 'Working the Returns Queues', summary: 'The 11-step precedence order for return packages and when to take action.' },
    { id: 'filing-claim', category: 'Returns', title: 'Filing a Claim', summary: 'Upload EXIF-stripped evidence and manage the 5-business-day window.' },
    { id: 'sku-costs', category: 'Inventory', title: 'Setting SKU Costs via CSV', summary: 'Import your COGS using the CSV bulk uploader for accurate profit calculation.' },
  ];

  const filtered = guides.filter(g => g.title.toLowerCase().includes(search.toLowerCase()) || g.summary.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="min-h-screen bg-slate-50 pb-24">
      <div className="max-w-7xl mx-auto px-4 pt-12">
        <div className="text-center mb-12">
          <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <BookOpen className="w-8 h-8" />
          </div>
          <h1 className="text-4xl font-bold text-slate-900 mb-4">SellerHub Knowledge Base</h1>
          <p className="text-lg text-slate-600 max-w-2xl mx-auto">
            Everything you need to know to automate your Daraz store operations, understand your true profit, and win claims.
          </p>
          
          <div className="max-w-xl mx-auto mt-8 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input 
              type="text" 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search for guides, features, or troubleshooting..." 
              className="w-full bg-white border border-slate-200 rounded-xl pl-12 pr-4 py-4 text-slate-800 shadow-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 transition text-lg"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map(guide => (
            <a key={guide.id} href={`#${guide.id}`} className="group bg-white border border-slate-200 rounded-xl p-6 shadow-sm hover:shadow-md hover:border-blue-300 transition block">
              <div className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-2">{guide.category}</div>
              <h3 className="font-bold text-slate-900 text-lg mb-2 group-hover:text-blue-600 transition flex items-center gap-2">
                <Book className="w-5 h-5 text-slate-400 group-hover:text-blue-500" /> {guide.title}
              </h3>
              <p className="text-slate-600 text-sm leading-relaxed mb-4">
                {guide.summary}
              </p>
              <div className="text-sm font-bold text-blue-600 flex items-center gap-1">
                Read guide <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
