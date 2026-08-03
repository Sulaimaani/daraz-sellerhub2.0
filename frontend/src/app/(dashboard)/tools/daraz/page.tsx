"use client";

import React, { useState, useEffect, useRef } from 'react';
import { 
  Settings, ChevronRight, RefreshCw, Search, Sparkles, X, Save, Type, Image as ImageIcon, Square, Plus
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

// Dynamically import fabric for client-side only if needed, but we can just use normal imports since "use client"
import * as fabric from 'fabric';

const API_BASE_URL = 'http://localhost:8000/api';

export default function DarazLabelsPage() {
  const [selectedOrders, setSelectedOrders] = useState<string[]>([]);
  const [showEditor, setShowEditor] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Mock data for UI layout
  const orders = [
    { id: '1', order_number: '123456789', status: 'ready_to_ship', items: [{ name: 'Test Product', sku: 'SKU1', awb: 'PK123' }] },
    { id: '2', order_number: '987654321', status: 'ready_to_ship', items: [{ name: 'Another Product', sku: 'SKU2', awb: 'PK456' }] }
  ];

  const toggleOrder = (id: string) => {
    setSelectedOrders(prev => 
      prev.includes(id) ? prev.filter(o => o !== id) : [...prev, id]
    );
  };

  const selectAll = () => setSelectedOrders(orders.map(o => o.id));
  const deselectAll = () => setSelectedOrders([]);

  return (
    <div className="min-h-screen bg-slate-50 pb-24 relative">
      {/* 1. Connected Store Strip */}
      <div className="bg-white border-b border-orange-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center text-orange-600 font-bold">
              D
            </div>
            <div>
              <div className="text-sm font-semibold text-slate-800">store@example.com</div>
              <div className="text-xs text-slate-400">email · PK · Connected 12 Aug 2026</div>
            </div>
          </div>
          <div className="flex gap-2">
            <button className="text-sm text-slate-600 hover:text-slate-800 px-3 py-1 font-medium">Rename</button>
            <button className="text-sm text-red-500 hover:text-red-600 px-3 py-1 font-medium">Disconnect</button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 mt-8 space-y-6">
        {/* 2. Label Settings Card */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 flex justify-between items-center cursor-pointer hover:bg-slate-50 transition">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center">
              <Settings className="text-slate-600 w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-slate-800">Label settings</h3>
              <p className="text-xs text-slate-500">Product name, picking list and packing strip options</p>
            </div>
          </div>
          <ChevronRight className="text-slate-400 w-5 h-5" />
        </div>

        {/* 3. Controls Row */}
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-slate-600">Sort by</span>
            <select className="bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-700 outline-none">
              <option>Latest Order Created</option>
              <option>Oldest</option>
              <option>Order value</option>
              <option>Buyer city</option>
            </select>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-400">Updated just now</span>
            <button className="bg-orange-500 hover:bg-orange-600 text-white font-medium text-sm px-4 py-2 rounded-lg flex items-center gap-2 transition">
              <RefreshCw className="w-4 h-4" /> Refresh synced orders
            </button>
          </div>
        </div>

        {/* 4. Search & Filter */}
        <div className="flex gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
            <input 
              type="text" 
              placeholder="Search order #, SKU, tracking, product..."
              className="w-full pl-10 pr-4 py-2 rounded-lg bg-white border border-slate-200 outline-none text-sm"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <select className="bg-white border border-slate-200 rounded-lg px-4 py-2 text-sm text-slate-700 outline-none w-48">
            <option>All statuses</option>
            <option>ready_to_ship</option>
          </select>
        </div>

        {/* 6. Count Line */}
        <div className="flex justify-between items-center">
          <span className="text-sm text-slate-500 font-medium">
            {orders.length} orders · <span className="text-orange-600">{selectedOrders.length} selected</span>
          </span>
          <div className="flex gap-3 text-sm font-medium">
            <button onClick={deselectAll} className="text-slate-500 hover:text-slate-800">Deselect all</button>
            <button onClick={selectAll} className="text-orange-600 hover:text-orange-700">Select all</button>
          </div>
        </div>

        {/* 7. Orders Table */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          {orders.map(order => (
            <div key={order.id} className={`p-4 border-b border-slate-100 flex items-start gap-4 transition
              ${selectedOrders.includes(order.id) ? 'bg-amber-50/50' : 'hover:bg-slate-50'}`}>
              <div className="pt-1">
                <input 
                  type="checkbox" 
                  checked={selectedOrders.includes(order.id)}
                  onChange={() => toggleOrder(order.id)}
                  className="rounded text-orange-500 focus:ring-orange-500 w-4 h-4" 
                />
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-center mb-3">
                  <span className="font-bold text-slate-800">#{order.order_number}</span>
                  <span className="bg-green-100 text-green-700 text-xs font-bold px-2 py-1 rounded uppercase">
                    {order.status}
                  </span>
                </div>
                {order.items.map((item, idx) => (
                  <div key={idx} className="flex gap-3 mt-2">
                    <div className="w-12 h-12 bg-slate-200 rounded shrink-0"></div>
                    <div>
                      <div className="text-sm font-medium text-blue-600">{item.name}</div>
                      <div className="text-xs text-slate-500 mt-1">Color family: Default SKU: {item.sku}</div>
                      <div className="text-xs text-slate-500 mt-0.5">AWB: <span className="font-medium text-slate-700">{item.awb}</span></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
        
        {/* 10. Label Jobs Panel (Placeholder) */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <h3 className="text-sm font-bold text-slate-800 mb-2">Recent Label Jobs</h3>
          <p className="text-xs text-slate-500">No recent jobs found.</p>
        </div>
      </div>

      {/* 8. Sticky Bottom Bar */}
      {selectedOrders.length > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] p-4 px-8 flex justify-between items-center z-40">
          <div className="text-sm font-bold text-slate-700">
            {selectedOrders.length} orders selected
          </div>
          <button 
            onClick={() => setShowEditor(true)}
            className="bg-orange-500 hover:bg-orange-600 text-white font-bold py-3 px-6 rounded-xl flex items-center gap-2 transition shadow-orange-500/20 shadow-lg">
            <Sparkles className="w-5 h-5" /> Enhance {selectedOrders.length} Labels →
          </button>
        </div>
      )}

      {/* 9. Full Screen Editor Modal */}
      {showEditor && (
        <div className="fixed inset-0 bg-slate-900 z-50 flex flex-col">
          {/* Editor Header */}
          <div className="h-14 bg-slate-800 border-b border-slate-700 flex justify-between items-center px-4 text-white">
            <div className="flex items-center gap-4">
              <button onClick={() => setShowEditor(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
              <div className="font-bold text-sm">Label Editor</div>
            </div>
            <div className="flex items-center gap-4">
              <button className="text-sm font-medium text-slate-300 hover:text-white flex items-center gap-2">
                <Save className="w-4 h-4" /> Save Template
              </button>
              <button className="bg-orange-500 hover:bg-orange-600 px-4 py-1.5 rounded text-sm font-bold flex items-center gap-2">
                Generate PDFs
              </button>
            </div>
          </div>
          
          {/* Editor Body */}
          <div className="flex-1 flex overflow-hidden">
            {/* Left Rail: Order Previews */}
            <div className="w-64 bg-slate-800 border-r border-slate-700 overflow-y-auto p-4 flex flex-col gap-2">
              <div className="text-xs font-bold text-slate-400 uppercase mb-2">Preview Orders</div>
              {selectedOrders.map((id, i) => (
                <div key={id} className={`p-3 rounded cursor-pointer text-sm font-medium
                  ${i === 0 ? 'bg-orange-500 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}>
                  Order #{id}
                </div>
              ))}
            </div>
            
            {/* Main Canvas Area */}
            <div className="flex-1 bg-slate-900 flex justify-center items-center overflow-auto p-8 relative">
              <FabricEditor />
            </div>
            
            {/* Right Rail: Toolbar */}
            <div className="w-72 bg-slate-800 border-l border-slate-700 p-4 overflow-y-auto">
              <div className="text-xs font-bold text-slate-400 uppercase mb-4">Add Elements</div>
              <div className="grid grid-cols-2 gap-2 mb-6">
                <button className="bg-slate-700 hover:bg-slate-600 text-slate-200 p-3 rounded flex flex-col items-center gap-2 text-xs">
                  <Type className="w-5 h-5" /> Text
                </button>
                <button className="bg-slate-700 hover:bg-slate-600 text-slate-200 p-3 rounded flex flex-col items-center gap-2 text-xs">
                  <ImageIcon className="w-5 h-5" /> Image
                </button>
                <button className="bg-slate-700 hover:bg-slate-600 text-slate-200 p-3 rounded flex flex-col items-center gap-2 text-xs">
                  <Square className="w-5 h-5" /> Shape
                </button>
                <button className="bg-slate-700 hover:bg-slate-600 text-slate-200 p-3 rounded flex flex-col items-center gap-2 text-xs">
                  <Plus className="w-5 h-5" /> Barcode
                </button>
              </div>
              
              <div className="text-xs font-bold text-slate-400 uppercase mb-4">Merge Fields</div>
              <div className="flex flex-col gap-2">
                {['{{buyer_name}}', '{{order_number}}', '{{tracking_code}}', '{{sku_list}}'].map(field => (
                  <button key={field} className="bg-slate-900 border border-slate-700 text-slate-300 px-3 py-2 rounded text-xs text-left hover:border-slate-500 font-mono">
                    {field}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Fabric.js Canvas Component isolated in its own effect
function FabricEditor() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    if (!canvasRef.current) return;
    
    // Initialize Fabric
    // We scale mm to px for preview. 101.6mm x 152.4mm (4x6 in)
    // Roughly 400px x 600px preview
    const canvas = new fabric.Canvas(canvasRef.current, {
      width: 400,
      height: 600,
      backgroundColor: '#ffffff'
    });
    
    // Draw Safe Margin (5mm)
    // 5mm / 101.6mm = ~5% of width
    const marginX = 20;
    const marginY = 20;
    
    const safeArea = new fabric.Rect({
      left: marginX,
      top: marginY,
      width: 400 - (marginX*2),
      height: 600 - (marginY*2),
      fill: 'transparent',
      stroke: 'rgba(239, 68, 68, 0.3)', // red dashed
      strokeWidth: 1,
      strokeDashArray: [5, 5],
      selectable: false,
      evented: false
    });
    canvas.add(safeArea);
    
    // Add dummy text
    const text = new fabric.Textbox('{{buyer_name}}', {
      left: 50,
      top: 50,
      width: 150,
      fontSize: 16,
      fontFamily: 'Inter',
      fill: '#333333'
    });
    canvas.add(text);
    
    return () => {
      canvas.dispose();
    };
  }, []);

  return (
    <div className="shadow-2xl">
      <canvas ref={canvasRef} />
    </div>
  );
}
