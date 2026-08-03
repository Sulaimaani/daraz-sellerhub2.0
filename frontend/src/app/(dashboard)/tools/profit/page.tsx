"use client";

import React, { useState, useEffect } from 'react';
import { Calculator, ArrowLeft, HelpCircle, Save, Download, AlertTriangle } from 'lucide-react';

export default function ProfitCalculatorPage() {
  const [inputs, setInputs] = useState({
    price: 2500,
    cost: 1200,
    packaging: 50,
    other: 10,
    commissionPct: 4.5,
    paymentFeePct: 1.75,
    shippingCost: 100,
    sellerVoucher: 0,
    returnRate: 5,
    failedDeliveryRate: 2
  });

  const [outputs, setOutputs] = useState({
    gross: 0,
    darazFees: 0,
    cogs: 0,
    netProfit: 0,
    marginPct: 0,
    breakEven: 0,
    riskAdjustedProfit: 0
  });

  useEffect(() => {
    // Math mirroring the Phase 4 profit.py exactly
    const gross = inputs.price;
    const commission = (inputs.price * (inputs.commissionPct / 100));
    const paymentFee = (inputs.price * (inputs.paymentFeePct / 100));
    const darazFees = commission + paymentFee + inputs.shippingCost;
    const cogs = inputs.cost + inputs.packaging + inputs.other;
    
    const netProfit = gross - darazFees - cogs - inputs.sellerVoucher;
    const marginPct = (netProfit / gross) * 100;
    
    // Break-even price
    // netProfit = 0 -> price = darazFees + cogs + voucher -> but fees depend on price.
    // P - (P * comm) - (P * pay) - flat = 0 -> P(1 - comm - pay) = flat
    const flatCosts = inputs.shippingCost + cogs + inputs.sellerVoucher;
    const breakEven = flatCosts / (1 - (inputs.commissionPct/100) - (inputs.paymentFeePct/100));

    // Risk adjusted
    const failCost = flatCosts * (inputs.failedDeliveryRate / 100);
    const returnCost = (flatCosts + (inputs.price * 0.05)) * (inputs.returnRate / 100); // Daraz charges 5% processing on returns usually
    const riskAdjusted = netProfit - failCost - returnCost;

    setOutputs({
      gross,
      darazFees,
      cogs,
      netProfit,
      marginPct,
      breakEven,
      riskAdjustedProfit: riskAdjusted
    });
  }, [inputs]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputs({
      ...inputs,
      [e.target.name]: parseFloat(e.target.value) || 0
    });
  };

  return (
    <div className="min-h-screen bg-slate-50 pb-24">
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
              <Calculator className="w-8 h-8 text-emerald-500" /> Profit Calculator
            </h1>
            <p className="text-slate-500 mt-2 text-lg">
              Simulate scenarios and calculate exact margins based on Daraz fees.
            </p>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 text-sm font-bold text-slate-700 hover:text-slate-900 border border-slate-200 bg-white px-4 py-2.5 rounded-lg shadow-sm">
              <Download className="w-4 h-4 text-blue-500" /> Load from SKU
            </button>
            <button className="flex items-center gap-2 text-sm font-bold text-white bg-emerald-600 hover:bg-emerald-700 px-4 py-2.5 rounded-lg shadow-sm transition">
              <Save className="w-4 h-4" /> Save Scenario
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Inputs Column */}
          <div className="lg:col-span-4 space-y-6">
            <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
              <h3 className="font-bold text-slate-800 mb-4 border-b border-slate-100 pb-2">Revenue</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Selling Price (PKR)</label>
                  <input name="price" type="number" value={inputs.price} onChange={handleInputChange} className="w-full border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-emerald-500" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Seller Voucher (PKR)</label>
                  <input name="sellerVoucher" type="number" value={inputs.sellerVoucher} onChange={handleInputChange} className="w-full border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-emerald-500" />
                </div>
              </div>

              <h3 className="font-bold text-slate-800 mb-4 border-b border-slate-100 pb-2 mt-8">Costs of Goods</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Cost Price (PKR)</label>
                  <input name="cost" type="number" value={inputs.cost} onChange={handleInputChange} className="w-full border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-emerald-500" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Packaging</label>
                    <input name="packaging" type="number" value={inputs.packaging} onChange={handleInputChange} className="w-full border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-emerald-500" />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Other flat</label>
                    <input name="other" type="number" value={inputs.other} onChange={handleInputChange} className="w-full border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-emerald-500" />
                  </div>
                </div>
              </div>

              <h3 className="font-bold text-slate-800 mb-4 border-b border-slate-100 pb-2 mt-8">Daraz Fees</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Commission %</label>
                    <input name="commissionPct" type="number" step="0.1" value={inputs.commissionPct} onChange={handleInputChange} className="w-full border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-emerald-500" />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Payment Fee %</label>
                    <input name="paymentFeePct" type="number" step="0.1" value={inputs.paymentFeePct} onChange={handleInputChange} className="w-full border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-emerald-500" />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Seller Shipping (PKR)</label>
                  <input name="shippingCost" type="number" value={inputs.shippingCost} onChange={handleInputChange} className="w-full border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-emerald-500" />
                </div>
              </div>

              <h3 className="font-bold text-slate-800 mb-4 border-b border-slate-100 pb-2 mt-8">Risk Factors</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Return Rate %</label>
                    <input name="returnRate" type="number" step="0.1" value={inputs.returnRate} onChange={handleInputChange} className="w-full border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-emerald-500" />
                  </div>
                  <div>
                    <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase">Fail Rate %</label>
                    <input name="failedDeliveryRate" type="number" step="0.1" value={inputs.failedDeliveryRate} onChange={handleInputChange} className="w-full border border-slate-200 rounded-lg px-3 py-2 outline-none focus:border-emerald-500" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Outputs Column */}
          <div className="lg:col-span-8 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-emerald-600 text-white p-6 rounded-xl shadow-sm">
                <div className="text-emerald-100 font-medium mb-1 uppercase text-sm tracking-wide">Net Profit per Unit</div>
                <div className="text-5xl font-bold mb-4">PKR {outputs.netProfit.toFixed(0)}</div>
                <div className="flex gap-4 border-t border-emerald-500 pt-4">
                  <div>
                    <div className="text-emerald-200 text-xs uppercase mb-1">Margin</div>
                    <div className="text-xl font-bold">{outputs.marginPct.toFixed(1)}%</div>
                  </div>
                  <div className="pl-4 border-l border-emerald-500">
                    <div className="text-emerald-200 text-xs uppercase mb-1">Risk Adjusted</div>
                    <div className="text-xl font-bold">PKR {outputs.riskAdjustedProfit.toFixed(0)}</div>
                  </div>
                </div>
              </div>

              <div className="bg-white border border-slate-200 p-6 rounded-xl shadow-sm">
                <h3 className="font-bold text-slate-800 mb-4 text-sm uppercase tracking-wider">Unit Economics Breakdown</h3>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between items-center py-2 border-b border-slate-100">
                    <span className="text-slate-500">Gross Revenue</span>
                    <span className="font-bold text-slate-900">PKR {outputs.gross.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-slate-100">
                    <span className="text-rose-500">Cost of Goods (COGS)</span>
                    <span className="font-bold text-rose-600">- PKR {outputs.cogs.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-slate-100">
                    <span className="text-rose-500">Daraz Fees (Comm+Pay+Ship)</span>
                    <span className="font-bold text-rose-600">- PKR {outputs.darazFees.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-slate-100">
                    <span className="text-rose-500">Vouchers</span>
                    <span className="font-bold text-rose-600">- PKR {inputs.sellerVoucher.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between items-center pt-2">
                    <span className="text-emerald-600 font-bold">Net Profit</span>
                    <span className="font-bold text-emerald-600">PKR {outputs.netProfit.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-blue-50 border border-blue-200 p-6 rounded-xl">
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600 flex-shrink-0">
                    <AlertTriangle className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="font-bold text-blue-900 mb-1">Break-even Point</h3>
                    <div className="text-sm text-blue-800 leading-relaxed mb-3">
                      To cover all costs and fees without making a loss, you must sell this item for at least:
                    </div>
                    <div className="text-2xl font-bold text-blue-700">PKR {outputs.breakEven.toFixed(0)}</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
              <div className="p-5 border-b border-slate-100 bg-slate-50">
                <h3 className="font-bold text-slate-800">Price Sensitivity Table</h3>
                <p className="text-sm text-slate-500">How margin scales as you adjust the selling price.</p>
              </div>
              <table className="w-full text-left text-sm">
                <thead className="bg-white text-slate-500 font-medium border-b border-slate-200">
                  <tr>
                    <th className="px-6 py-3">SELLING PRICE</th>
                    <th className="px-6 py-3">DARAZ FEES</th>
                    <th className="px-6 py-3">NET PROFIT</th>
                    <th className="px-6 py-3">MARGIN %</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {[-20, -10, 0, 10, 20].map((step) => {
                    const simPrice = inputs.price * (1 + step/100);
                    const simComm = simPrice * (inputs.commissionPct/100);
                    const simPay = simPrice * (inputs.paymentFeePct/100);
                    const simDaraz = simComm + simPay + inputs.shippingCost;
                    const simNet = simPrice - simDaraz - outputs.cogs - inputs.sellerVoucher;
                    const simMargin = (simNet / simPrice) * 100;
                    
                    return (
                      <tr key={step} className={step === 0 ? "bg-emerald-50/50" : ""}>
                        <td className="px-6 py-3 font-medium text-slate-900">PKR {simPrice.toFixed(0)} {step === 0 && <span className="ml-2 text-[10px] bg-emerald-100 text-emerald-700 px-1.5 py-0.5 rounded font-bold">CURRENT</span>}</td>
                        <td className="px-6 py-3 text-slate-600">PKR {simDaraz.toFixed(0)}</td>
                        <td className={`px-6 py-3 font-bold ${simNet < 0 ? 'text-rose-600' : 'text-emerald-600'}`}>PKR {simNet.toFixed(0)}</td>
                        <td className={`px-6 py-3 font-bold ${simMargin < 0 ? 'text-rose-600' : 'text-slate-700'}`}>{simMargin.toFixed(1)}%</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

          </div>
        </div>
      </div>
    </div>
  );
}
