"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import api from "../../lib/api";
import { useSyncStatus } from "../../hooks/useSyncStatus";
import { CheckCircle, Loader2, Store, PackageSearch, Undo2, Rocket } from "lucide-react";

function OnboardingContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [step, setStep] = useState(1);
  const [storeId, setStoreId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(searchParams.get("error"));
  
  const { syncJob, isPolling } = useSyncStatus(storeId);

  useEffect(() => {
    // Check state from backend
    api.get("/onboarding/").then((res) => {
      const serverStep = res.data.current_step;
      const queryStep = searchParams.get("step");
      if (queryStep) {
        api.post("/onboarding/step/", { step: parseInt(queryStep) }).then(() => {
          setStep(parseInt(queryStep));
          setError(null);
        }).catch((err) => {
          setError((err as { response?: { data?: { error?: string } } }).response?.data?.error || "An error occurred");
        });
      } else {
        setStep(serverStep);
      }
    });

    api.get("/stores/").then((res) => {
      if (res.data.length > 0) {
        setStoreId(res.data[0].id);
      }
    });
  }, [searchParams]);

  const advanceStep = async (newStep: number) => {
    try {
      await api.post("/onboarding/step/", { step: newStep });
      setStep(newStep);
      setError(null);
    } catch (err) {
      setError((err as { response?: { data?: { error?: string } } }).response?.data?.error || "An error occurred");
    }
  };

  const handleConnectStore = async () => {
    try {
      const res = await api.post("/stores/connect/");
      window.location.href = res.data.authorize_url;
    } catch {
      setError("Failed to generate connect URL");
    }
  };

  const steps = [
    { id: 1, title: "Welcome", desc: "Understand what SellerHub needs to prepare your account." },
    { id: 2, title: "Connect Daraz Store", desc: "Required for API tools." },
    { id: 3, title: "Import SKU Catalog / Add Cost", desc: "Needed for clean labels and accurate profit." },
    { id: 4, title: "Start Returns First Sync", desc: "Prepare Return & Claim Manager." },
    { id: 5, title: "Finish", desc: "Start using your tools." },
  ];

  const pctComplete = ((step - 1) / (steps.length - 1)) * 100;

  return (
    <div className="min-h-screen flex bg-gray-50">
      
      {/* Sidebar */}
      <div className="w-80 bg-white border-r p-6 hidden md:block">
        <h2 className="text-xl font-bold mb-6">Setup Guide</h2>
        <div className="mb-8">
          <div className="text-sm font-medium text-gray-500 mb-2">
            Step {step} of 5 · {Math.round(pctComplete)}% complete
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-orange-500 h-2 rounded-full transition-all duration-300" 
              style={{ width: `${pctComplete}%` }}
            ></div>
          </div>
        </div>

        <div className="space-y-6">
          {steps.map((s) => {
            const isCompleted = step > s.id;
            const isCurrent = step === s.id;
            return (
              <div key={s.id} className="flex gap-3">
                <div className="mt-1">
                  {isCompleted ? (
                    <CheckCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center text-[10px] font-bold ${isCurrent ? 'border-orange-500 text-orange-500' : 'border-gray-300 text-gray-400'}`}>
                      {s.id}
                    </div>
                  )}
                </div>
                <div>
                  <h4 className={`font-semibold ${isCurrent ? 'text-gray-900' : (isCompleted ? 'text-gray-700' : 'text-gray-400')}`}>{s.title}</h4>
                  <p className={`text-sm ${isCurrent ? 'text-gray-600' : 'text-gray-400'}`}>{s.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col p-8 md:p-12">
        <div className="max-w-2xl w-full mx-auto bg-white rounded-xl shadow-sm border p-8">
          {error && (
            <div className="bg-red-50 text-red-600 p-4 rounded-md mb-6 border border-red-200">
              {error}
            </div>
          )}

          {step === 1 && (
            <div className="space-y-6">
              <h2 className="text-3xl font-bold text-gray-900">Welcome to SellerHub</h2>
              <p className="text-lg text-gray-600">
                To give you accurate profit numbers, claim management, and order tracking, we need to connect to your Daraz account and import your catalog. 
                <br/><br/>
                We&apos;ll walk you through the process step-by-step.
              </p>
              <div className="pt-4">
                <button 
                  onClick={() => advanceStep(2)}
                  className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-3 rounded-lg font-medium transition-colors"
                >
                  Continue to Connect
                </button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 text-orange-500 mb-2">
                <Store className="w-10 h-10" />
                <h2 className="text-3xl font-bold text-gray-900">Connect Daraz Store</h2>
              </div>
              
              {!storeId ? (
                <>
                  <p className="text-gray-600 text-lg">
                    You will be redirected to Daraz to authorize access. We only ask for the permissions needed to sync your data.
                  </p>
                  <button 
                    onClick={handleConnectStore}
                    className="bg-[#FF6A00] hover:bg-[#e65c00] text-white px-8 py-3 rounded-lg font-medium transition-colors inline-block mt-4"
                  >
                    Connect with Daraz
                  </button>
                </>
              ) : (
                <div className="bg-gray-50 border rounded-xl p-6">
                  {(isPolling || (syncJob && syncJob.status === 'running') || syncJob?.status === 'queued') ? (
                    <div className="text-center py-6">
                      <Loader2 className="w-12 h-12 text-orange-500 animate-spin mx-auto mb-4" />
                      <h3 className="text-xl font-bold mb-2">Syncing 120-Day History...</h3>
                      <p className="text-gray-500 mb-6">Importing orders and finance records.</p>
                      
                      <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                        <div 
                          className="bg-orange-500 h-2 rounded-full transition-all duration-500" 
                          style={{ width: `${syncJob?.progress_pct || 0}%` }}
                        ></div>
                      </div>
                      <div className="flex justify-between text-sm text-gray-500 mb-6">
                        <span>Progress</span>
                        <span>{syncJob?.progress_pct || 0}%</span>
                      </div>
                      
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 text-left">
                        <div className="bg-white p-3 rounded border shadow-sm">
                          <div className="text-xs text-gray-400">Orders</div>
                          <div className="font-bold text-lg">{syncJob?.counters?.orders || 0}</div>
                        </div>
                        <div className="bg-white p-3 rounded border shadow-sm">
                          <div className="text-xs text-gray-400">Finance</div>
                          <div className="font-bold text-lg">{syncJob?.counters?.finance || 0}</div>
                        </div>
                        <div className="bg-white p-3 rounded border shadow-sm">
                          <div className="text-xs text-gray-400">Returns</div>
                          <div className="font-bold text-lg">{syncJob?.counters?.returns || 0}</div>
                        </div>
                        <div className="bg-white p-3 rounded border shadow-sm">
                          <div className="text-xs text-gray-400">Profit</div>
                          <div className="font-bold text-lg">{syncJob?.counters?.profit || 0}</div>
                        </div>
                      </div>
                    </div>
                  ) : syncJob?.status === "failed" ? (
                    <div className="text-center py-6 text-red-600">
                      <p className="font-bold mb-2">Sync Failed</p>
                      <p className="text-sm mb-4">{syncJob.error}</p>
                      <button onClick={handleConnectStore} className="text-orange-500 underline font-medium">Reconnect & Try Again</button>
                    </div>
                  ) : (
                    <div className="text-center py-6">
                      <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                      <h3 className="text-xl font-bold mb-2">Store Connected & Synced!</h3>
                      <p className="text-gray-500 mb-6">We have successfully imported your store history.</p>
                      <button 
                        onClick={() => advanceStep(3)}
                        className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-3 rounded-lg font-medium transition-colors"
                      >
                        Continue to SKU Catalog
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 text-orange-500 mb-2">
                <PackageSearch className="w-10 h-10" />
                <h2 className="text-3xl font-bold text-gray-900">Import SKU Catalog</h2>
              </div>
              <p className="text-lg text-gray-600">
                To calculate accurate profit margins, we need the Cost of Goods (COGS) for each SKU.
                You can import this now via CSV, or skip and add it later in SKU Settings.
              </p>
              
              <div className="bg-gray-50 border border-dashed border-gray-300 rounded-xl p-8 text-center">
                <p className="text-gray-500 mb-4">SKU Import functionality will be available in Phase 3.</p>
                <button 
                  disabled
                  className="bg-gray-200 text-gray-500 px-6 py-2 rounded-lg font-medium cursor-not-allowed"
                >
                  Upload CSV
                </button>
              </div>

              <div className="pt-4 flex gap-4">
                <button 
                  onClick={() => advanceStep(4)}
                  className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-3 rounded-lg font-medium transition-colors"
                >
                  Skip for now
                </button>
              </div>
            </div>
          )}

          {step === 4 && (
            <div className="space-y-6">
              <div className="flex items-center gap-4 text-orange-500 mb-2">
                <Undo2 className="w-10 h-10" />
                <h2 className="text-3xl font-bold text-gray-900">Returns First Sync</h2>
              </div>
              <p className="text-lg text-gray-600">
                We need to do an initial pass of your returned orders to set up the Claims Manager.
              </p>

              <div className="bg-gray-50 border rounded-xl p-8 text-center">
                <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
                <h3 className="text-lg font-bold mb-2">Returns Seeded</h3>
                <p className="text-gray-500 text-sm">
                  Initial returns sync was automatically processed during your store connection.
                </p>
              </div>

              <div className="pt-4">
                <button 
                  onClick={() => advanceStep(5)}
                  className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-3 rounded-lg font-medium transition-colors"
                >
                  Finish Setup
                </button>
              </div>
            </div>
          )}

          {step === 5 && (
            <div className="space-y-6 text-center py-12">
              <Rocket className="w-20 h-20 text-orange-500 mx-auto mb-6" />
              <h2 className="text-3xl font-bold text-gray-900">You&apos;re All Set!</h2>
              <p className="text-lg text-gray-600 max-w-md mx-auto">
                Your account is fully configured. Start exploring your profit metrics and managing claims.
              </p>
              <div className="pt-8">
                <button 
                  onClick={() => router.push("/stores")}
                  className="bg-orange-500 hover:bg-orange-600 text-white px-10 py-4 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transition-all"
                >
                  Go to Dashboard
                </button>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default function OnboardingPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <OnboardingContent />
    </Suspense>
  );
}
