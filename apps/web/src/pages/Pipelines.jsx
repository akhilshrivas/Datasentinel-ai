import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { Database, Info } from 'lucide-react';
import { formatDateTime } from '../utils/formatters';

const Pipelines = () => {
  const [pipelines, setPipelines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('All');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await api.getPipelines();
        if (data && data.error) {
          setError(data.error);
          setPipelines([]);
        } else {
          setPipelines(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className='page-scroll mono'>[SYSTEM] Fetching pipeline state...</div>;
  if (error) return <div className='page-scroll mono' style={{color: 'var(--danger)'}}>[ERROR] {error}</div>;

  const resolvePipelineName = (run) => {
    if (run.id && !run.item_id) return run.id; 
    if (run.item_id === '9544e045-6914-49b8-92ca-56cb8cd64185') return 'DataSentinel_Batch_Pipeline';
    return run.item_id ? `Pipeline_${run.item_id.substring(0, 8)}` : 'Unknown Pipeline';
  };

  const getStatusBadge = (status) => {
    const s = (status || '').toLowerCase();
    if (['success', 'completed'].includes(s)) return 'badge-success';
    if (['failed', 'error'].includes(s)) return 'badge-danger';
    return 'badge-warning';
  };

  const isFailed = (status) => ['failed', 'error'].includes((status || '').toLowerCase());

  const filteredPipelines = pipelines.filter(p => {
    if (filter === 'All') return true;
    if (filter === 'Failed') return isFailed(p.status);
    if (filter === 'Completed') return ['success', 'completed'].includes((p.status || '').toLowerCase());
    return true;
  });

  const steps = [
    { name: 'Source', type: 'Ingestion', status: 'success' },
    { name: 'Bronze', type: 'Raw Data', status: 'success' },
    { name: 'Silver', type: 'Cleaned', status: 'success' },
    { name: 'Gold', type: 'Aggregated', status: 'warning' },
    { name: 'Serving', type: 'API', status: 'success' }
  ];

  return (
    <>
      <div className='page-header' style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className='page-title'>Pipeline Operations</h1>
          <div className='mono text-muted'>sys.active_nodes: {pipelines.length}</div>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {['All', 'Completed', 'Failed'].map(f => (
            <button 
              key={f}
              onClick={() => setFilter(f)}
              style={{
                background: filter === f ? 'var(--accent)' : 'var(--bg-panel)',
                color: filter === f ? '#000' : 'var(--text-main)',
                border: '1px solid var(--border)',
                padding: '4px 12px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontFamily: 'var(--font-mono)',
                fontSize: '11px'
              }}
            >
              {f}
            </button>
          ))}
        </div>
      </div>
      
      <div className='page-scroll'>
        <div className='card' style={{ marginBottom: '24px' }}>
          <h3 className='card-title'>Logical Lineage Map</h3>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '32px 16px' }}>
            {steps.map((step, idx) => (
              <React.Fragment key={idx}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
                  <div style={{ 
                    width: '64px', height: '64px', borderRadius: '50%', 
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: step.status === 'success' ? 'var(--success-muted)' : 'var(--warning-muted)',
                    border: `2px solid ${step.status === 'success' ? 'var(--success)' : 'var(--warning)'}`
                  }}>
                    <Database size={24} color={step.status === 'success' ? 'var(--success)' : 'var(--warning)'} />
                  </div>
                  <div style={{ fontWeight: '600' }}>{step.name}</div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{step.type}</div>
                </div>
                {idx < steps.length - 1 && (
                  <div style={{ flex: 1, height: '2px', background: 'var(--border)', margin: '0 16px', position: 'relative' }}>
                    <div style={{ position: 'absolute', right: '-4px', top: '-4px', borderTop: '5px solid transparent', borderBottom: '5px solid transparent', borderLeft: '5px solid var(--border)' }}></div>
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
        
        <div className='table-container'>
          <table>
            <thead>
              <tr>
                <th>Pipeline</th>
                <th>Status</th>
                <th>Started</th>
                <th>Invoke Type</th>
              </tr>
            </thead>
            <tbody>
              {filteredPipelines.map((run, i) => (
                <tr key={i}>
                  <td>
                    <div style={{ fontWeight: 500 }}>{resolvePipelineName(run)}</div>
                    {isFailed(run.status) && run.failure_reason && (
                      <div style={{ fontSize: '11px', color: 'var(--danger)', marginTop: '6px', background: 'var(--danger-muted)', padding: '8px', borderRadius: '4px', borderLeft: '2px solid var(--danger)' }}>
                        <Info size={12} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }}/>
                        {typeof run.failure_reason === 'string' 
                          ? run.failure_reason 
                          : (run.failure_reason?.message || JSON.stringify(run.failure_reason))}
                      </div>
                    )}
                  </td>
                  <td>
                    <span className={`badge ${getStatusBadge(run.status)}`}>
                      {run.status || 'UNKNOWN'}
                    </span>
                  </td>
                  <td>{run.start_time ? formatDateTime(run.start_time) : (run.timestamp ? formatDateTime(run.timestamp) : 'Unavailable')}</td>
                  <td>{run.invoke_type || 'Manual'}</td>
                </tr>
              ))}
              {filteredPipelines.length === 0 && (
                <tr>
                  <td colSpan="4" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>No pipelines match the current filter.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
};

export default Pipelines;
