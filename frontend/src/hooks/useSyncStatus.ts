import { useState, useEffect } from 'react';
import api from '../lib/api';

export type SyncWindow = {
  id: number;
  date_from: string;
  date_to: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  attempts: number;
  last_error: string;
  records_imported: number;
};

export type SyncJob = {
  id: number;
  kind: string;
  status: 'queued' | 'running' | 'done' | 'failed' | 'cancelled';
  progress_pct: number;
  total_windows: number;
  completed_windows: number;
  started_at: string | null;
  finished_at: string | null;
  error: string;
  counters: { [key: string]: number };
  windows: SyncWindow[];
};

export function useSyncStatus(storeId: number | null) {
  const [syncJob, setSyncJob] = useState<SyncJob | null>(null);
  const [isPolling, setIsPolling] = useState(false);

  useEffect(() => {
    if (!storeId) return;

    let timeoutId: NodeJS.Timeout;
    let pollInterval = 3000; // start with 3s

    const poll = async () => {
      try {
        const res = await api.get(`/stores/${storeId}/sync-status/`);
        
        if (res.data && res.data.status) {
          setSyncJob(res.data);
          
          if (res.data.status === 'running' || res.data.status === 'queued') {
            setIsPolling(true);
            // back off to 15s if it runs for a long time
            if (pollInterval < 15000) pollInterval += 1000; 
            timeoutId = setTimeout(poll, pollInterval);
          } else {
            setIsPolling(false);
          }
        } else {
          setIsPolling(false);
        }
      } catch {
        setIsPolling(false);
      }
    };

    poll();

    return () => clearTimeout(timeoutId);
  }, [storeId]);

  const rebuildHistory = async () => {
    if (!storeId) return;
    await api.post(`/stores/${storeId}/rebuild-history/`);
    // re-trigger poll
    setSyncJob((prev) => prev ? { ...prev, status: 'queued' } : null);
  };

  return { syncJob, isPolling, rebuildHistory };
}
