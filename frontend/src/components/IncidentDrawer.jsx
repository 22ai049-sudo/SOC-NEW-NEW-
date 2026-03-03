export default function IncidentDrawer({ incident, onClose, onExecute }) {
  if (!incident) return null;
  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer" onClick={(e) => e.stopPropagation()}>
        <h3>{incident.id}</h3>
        <p>{incident.title}</p>
        <p><strong>Severity:</strong> {incident.severity}</p>
        <p><strong>Risk Score:</strong> {incident.risk_score}</p>
        <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(incident.details, null, 2)}</pre>
        <button onClick={() => onExecute(incident.id)}>Execute Mitigation</button>
      </div>
    </div>
  );
}
