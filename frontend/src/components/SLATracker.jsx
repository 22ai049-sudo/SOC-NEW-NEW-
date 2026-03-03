export default function SLATracker({children,data}){ return <div className="panel"><h4>SLATracker</h4><pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(data,null,2)}</pre>{children}</div>; }
