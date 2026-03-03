import { useEffect, useState } from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import IncidentsPage from './pages/IncidentsPage';
import CasesPage from './pages/CasesPage';
import MITREPage from './pages/MITREPage';
import IntelPage from './pages/IntelPage';
import IngestionPage from './pages/IngestionPage';
import AgentsPage from './pages/AgentsPage';
import SIEMPage from './pages/SIEMPage';
import AuditPage from './pages/AuditPage';
import { AuthProvider, useAuth } from './context/AuthContext';
import api from './services/api';
import './styles/theme.css';

function Shell() {
  const { user, login } = useAuth();
  const [live, setLive] = useState(null);
  const [wsConnected, setWs] = useState(false);
  const [tenant, setTenant] = useState('tenant-a');

  useEffect(() => {
    if (!user) return;
    setTenant(user.tenant_id);
  }, [user]);

  useEffect(() => {
    if (!user) return;
    const ws = new WebSocket((import.meta.env.VITE_WS_URL) || 'ws://localhost:8000/ws/live');
    ws.onopen = () => setWs(true);
    ws.onmessage = (e) => setLive(JSON.parse(e.data));
    ws.onclose = () => setWs(false);
    const t = setInterval(() => ws.readyState === 1 && ws.send('ping'), 3000);
    return () => {
      clearInterval(t);
      ws.close();
    };
  }, [user]);

  async function handleTenantSwitch(nextTenant) {
    await api.post('/api/tenant/switch', { tenant_id: nextTenant });
    setTenant(nextTenant);
  }

  if (!user) {
    return <div className='panel' style={{ maxWidth: 320, margin: '80px auto' }}><h3>Login</h3><button onClick={() => login('admin', 'admin123')}>Login as admin</button></div>;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path='/' element={<Layout wsConnected={wsConnected} tenant={tenant} role={user.role} onTenantSwitch={handleTenantSwitch} />}>
          <Route index element={<DashboardPage live={live} />} />
          <Route path='incidents' element={<IncidentsPage />} />
          <Route path='cases' element={<CasesPage />} />
          <Route path='mitre' element={<MITREPage />} />
          <Route path='intel' element={<IntelPage />} />
          <Route path='ingestion' element={<IngestionPage />} />
          <Route path='agents' element={<AgentsPage />} />
          <Route path='siem' element={<SIEMPage />} />
          <Route path='audit' element={<AuditPage />} />
        </Route>
        <Route path='*' element={<Navigate to='/' />} />
      </Routes>
    </BrowserRouter>
  );
}

export default function App() {
  return <AuthProvider><Shell /></AuthProvider>;
}
