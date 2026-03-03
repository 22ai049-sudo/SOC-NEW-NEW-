import { Link, Outlet } from 'react-router-dom';
import Topbar from './Topbar';

export default function Layout(props){
  return <div className="layout"><aside className="sidebar">{['/','/incidents','/cases','/mitre','/intel','/ingestion','/agents','/siem','/audit'].map((p)=><div key={p}><Link to={p}>{p}</Link></div>)}</aside><main><Topbar {...props}/><div className="content"><Outlet/></div></main></div>;
}
