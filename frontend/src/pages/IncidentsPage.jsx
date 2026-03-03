import { useEffect, useState } from 'react';
import api from '../services/api';
import IncidentDrawer from '../components/IncidentDrawer';

export default function IncidentsPage() {
  const [inc, setInc] = useState([]);
  const [selected, setSelected] = useState(null);

  async function load() {
    const data = await api.get('/api/incidents');
    setInc(data);
  }

  useEffect(() => {
    load();
  }, []);

  async function executeMitigation(incidentId) {
    await api.post('/api/mitigation/execute', { incident_id: incidentId });
    await load();
    setSelected(null);
  }

  return (
    <>
      <div className="panel">
        <h3>Incidents</h3>
        {inc.map((i) => (
          <div className="table-row" key={i.id} onClick={() => setSelected(i)} style={{ cursor: 'pointer' }}>
            <span>{i.id} {i.title}</span>
            <span>{i.risk_score}</span>
          </div>
        ))}
      </div>
      <IncidentDrawer incident={selected} onClose={() => setSelected(null)} onExecute={executeMitigation} />
    </>
  );
}
