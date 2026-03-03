export default function MetricsRow({children,data}){ return <div className="panel"><h4>MetricsRow</h4><pre style={{whiteSpace:'pre-wrap'}}>{JSON.stringify(data,null,2)}</pre>{children}</div>; }
