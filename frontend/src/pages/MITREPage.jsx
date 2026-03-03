import { useEffect, useState } from 'react';
import api from '../services/api';
export default function MITREPage(){ const [data,setData]=useState([]); useEffect(()=>{const map={MITRE:'/api/incidents',Intel:'/api/incidents',Ingestion:'/api/dashboard/metrics',Agents:'/api/agents/activity',SIEM:'/api/siem/status',Audit:'/api/audit'}; api.get(map['MITRE']).then(setData);},[]); return <div className='panel'><h3>MITRE</h3><pre>{JSON.stringify(data,null,2)}</pre></div>; }
