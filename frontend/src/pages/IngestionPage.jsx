import { useState } from 'react';
import api from '../services/api';

export default function IngestionPage() {
  const [rawLog, setRawLog] = useState('Failed password brute force detected from 203.0.113.47');
  const [result, setResult] = useState(null);

  async function ingestManual() {
    const res = await api.post('/api/ingest/manual', {
      source: 'manual-ui',
      raw_log: rawLog,
      asset_criticality: 1.3,
    });
    setResult(res);
  }

  async function ingestDataset() {
    const res = await api.post('/api/ingest/dataset/start');
    setResult(res);
  }

  async function toggleScheduler() {
    const res = await api.post('/api/ingest/scheduler/toggle');
    setResult(res);
  }

  return (
    <div className="panel">
      <h3>Ingestion</h3>
      <textarea value={rawLog} onChange={(e) => setRawLog(e.target.value)} rows={4} style={{ width: '100%', marginBottom: 12 }} />
      <div style={{ display: 'flex', gap: 8 }}>
        <button onClick={ingestManual}>Ingest Manual Log</button>
        <button onClick={ingestDataset}>Start Dataset Ingestion</button>
        <button onClick={toggleScheduler}>Toggle Scheduler</button>
      </div>
      <pre>{JSON.stringify(result, null, 2)}</pre>
    </div>
  );
}
