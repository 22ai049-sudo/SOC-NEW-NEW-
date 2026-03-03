import { useEffect, useState } from 'react';
import api from '../services/api';
import MetricsRow from '../components/MetricsRow';
import LiveIncidentFeed from '../components/LiveIncidentFeed';
import RiskGauge from '../components/RiskGauge';
import PipelineFlow from '../components/PipelineFlow';

export default function DashboardPage({live}){
  const [metrics,setMetrics]=useState({}); const [inc,setInc]=useState([]);
  useEffect(()=>{api.get('/api/dashboard/metrics').then(setMetrics); api.get('/api/incidents').then(setInc);},[]);
  useEffect(()=>{if(live?.type==='incident_feed') setInc((s)=>[live.data,...s]);},[live]);
  return <div className='grid'><MetricsRow data={metrics}/><RiskGauge data={metrics}/><PipelineFlow data={live}/><LiveIncidentFeed data={inc}/></div>;
}
