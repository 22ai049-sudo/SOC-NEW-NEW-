import { useEffect, useState } from 'react';
import api from '../services/api';

export default function CasesPage(){
 const [cases,setCases]=useState([]); useEffect(()=>{api.get('/api/cases').then(setCases);},[]);
 return <div className='panel'><h3>Cases</h3>{cases.map(c=><div className='table-row' key={c.id}>{c.id} - {c.status}</div>)}</div>;
}
