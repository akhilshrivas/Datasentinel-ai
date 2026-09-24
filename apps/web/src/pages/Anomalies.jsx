import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { AlertTriangle, Activity, RefreshCw, BarChart2 } from 'lucide-react';
import { formatDateTime } from '../utils/formatters';

const PayloadDetails = ({ payload }) => {
  const [expanded, setExpanded] = useState(false);
  
  if (!payload) return <span className='text-muted'>N/A</span>;
  
  let parsedPayload = payload;
  if (typeof payload === 'string') {
    try {
      parsedPayload = JSON.parse(payload);
    } catch {
      // Keep as string if parsing fails
    }
  }

  const source = parsedPayload?.source || 'Unknown';
  const metric = parsedPayload?.random_metric !== undefined ? parsedPayload.random_metric : 'N/A';
  
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span>src: {source} | val: {metric}</span>
        <button 
          onClick={() => setExpanded(!expanded)} 
          style={{ background: 'none', border: '1px solid var(--border)', borderRadius: '3px', color: 'var(--text-main)', cursor: 'pointer', fontSize: '10px', padding: '2px 6px', marginLeft: '8px' }}
        >
          {expanded ? 'Hide' : 'Inspect'}
        </button>
      </div>
      {expanded && (
        <div style={{ marginTop: '8px', padding: '8px', background: 'var(--bg-panel)', border: '1px solid var(--border)', borderRadius: '4px', fontFamily: 'var(--font-mono)', fontSize: '10px', whiteSpace: 'pre-wrap', wordBreak: 'break-all', color: 'var(--text-muted)' }}>
          {typeof parsedPayload === 'object' ? JSON.stringify(parsedPayload, null, 2) : parsedPayload}
        </div>
      )}
    </div>
  );
};

const Anomalies = () => {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getAnomalies();
      if (data && data.error) {
        setError(data.error);
        setAnomalies([]);
      } else {
        setAnomalies(Array.isArray(data) ? data : []);
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch anomalies');
      setAnomalies([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const getAnomalyDistribution = () => {
    const dist = {};
    anomalies.forEach(a => {
      const type = a.anomaly || 'UNKNOWN';
      dist[type] = (dist[type] || 0) + 1;
    });
    return Object.entries(dist).sort((a, b) => b[1] - a[1]);
  };

  const distribution = getAnomalyDistribution();

  return (
    <>
      <div className='page-header' style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className='page-title'>Real-Time Anomaly Detection</h1>
          <div className='mono text-muted'>detected_count: {anomalies.length}</div>
        </div>
        <button 
          onClick={fetchData} 
          disabled={loading}
          style={{
            background: 'var(--bg-panel)',
            color: 'var(--text-main)',
            border: '1px solid var(--border)',
            padding: '6px 12px',
            borderRadius: '4px',
            cursor: loading ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontFamily: 'var(--font-mono)',
            fontSize: '11px'
          }}
        >
          <RefreshCw size={12} className={loading ? 'spin' : ''} />
          Refresh Stream
        </button>
      </div>
      
      <div className='page-scroll'>
        
        {/* KPI & Distribution Section */}
        <div className='grid grid-cols-3' style={{marginBottom: '24px'}}>
          <div className='card'>
            <div className='card-header'>
              <h3 className='card-title'><Activity size={14}/> Total Detected Events</h3>
              <span className='badge badge-neutral'>WINDOW</span>
            </div>
            <p className='metric-value'>{anomalies.length}</p>
          </div>
          
          <div className='card' style={{ gridColumn: 'span 2' }}>
            <div className='card-header'>
              <h3 className='card-title'><BarChart2 size={14}/> Event Distribution</h3>
              <span className='badge badge-neutral'>BY TYPE</span>
            </div>
            <div style={{ marginTop: '16px', display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
              {distribution.length === 0 ? (
                <span className='text-muted'>No data to distribute.</span>
              ) : (
                distribution.map(([type, count]) => (
                  <div key={type} style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'var(--bg-panel)', padding: '8px 12px', borderRadius: '4px', border: '1px solid var(--border)' }}>
                    <span className='badge badge-danger' style={{ fontSize: '10px' }}>{type}</span>
                    <span className='mono text-lg'>{count}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Main Error state overrides table if it entirely failed */}
        {error && !loading && (
          <div style={{ color: 'var(--danger)', padding: '16px', background: 'var(--danger-muted)', borderLeft: '3px solid var(--danger)', marginBottom: '24px', fontFamily: 'var(--font-mono)' }}>
            [API ERROR] {error}
          </div>
        )}

        <div className='table-container'>
          <table>
            <thead>
              <tr>
                <th>Time (Local)</th>
                <th>Event Type</th>
                <th>Entity ID</th>
                <th>Classification</th>
                <th>Status</th>
                <th>Payload details</th>
              </tr>
            </thead>
            <tbody>
              {loading && anomalies.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '24px' }} className='mono text-muted'>
                    [SYSTEM] Syncing realtime KQL streams...
                  </td>
                </tr>
              ) : anomalies.length === 0 && !error ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '24px' }} className='mono text-muted'>
                    No anomalies detected in the current window.
                  </td>
                </tr>
              ) : (
                anomalies.map((a, i) => {
                  const time = a.event_time || a.timestamp;
                  
                  return (
                    <tr key={i}>
                      <td>{formatDateTime(time)}</td>
                      <td>{a.event_type || 'Unknown'}</td>
                      <td className='mono' style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        {a.entity_id || 'N/A'}
                      </td>
                      <td>
                        <span style={{ color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 500 }}>
                          <AlertTriangle size={14} /> 
                          {a.anomaly || 'UNKNOWN'}
                        </span>
                      </td>
                      <td><span className='badge badge-warning'>Detected</span></td>
                      <td style={{ maxWidth: '300px' }}>
                        <PayloadDetails payload={a.payload} />
                      </td>
                    </tr>
                  )
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
};

export default Anomalies;
