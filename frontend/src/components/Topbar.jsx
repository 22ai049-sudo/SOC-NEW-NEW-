export default function Topbar({ wsConnected, tenant, onTenantSwitch, role }) {
  return (
    <div className="topbar">
      <strong>NEXUS SOC Command Center</strong>
      <div>
        <span className="badge pulse">{wsConnected ? 'LIVE' : 'OFFLINE'}</span>{' '}
        <span className="badge">{role}</span>{' '}
        <select value={tenant} onChange={(e) => onTenantSwitch(e.target.value)}>
          <option value="tenant-a">tenant-a</option>
          <option value="tenant-b">tenant-b</option>
        </select>
      </div>
    </div>
  );
}
