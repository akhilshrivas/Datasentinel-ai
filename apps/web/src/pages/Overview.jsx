import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, AlertTriangle, ShieldCheck, Database, Info } from 'lucide-react';
import { formatTime, formatDate } from '../utils/formatters';

const ErrorDetails = ({ failureReason }) => {
  const [expanded, setExpanded] = useState(false);
  
  if (!failureReason) return null;
  
  let summaryMessage = "Execution failed";
  const fullMessage = typeof failureReason === 'string' 
    ? failureReason 
    : (failureReason?.message || JSON.stringify(failureReason));
    
  if (fullMessage.includes('TooManyRequestsForCapacity') || fullMessage.includes('capacity compute limit')) {
    summaryMessage = "Spark capacity limit reached";
  } else if (fullMessage.length > 40) {
    summaryMessage = fullMessage.substring(0, 40) + '...';
  } else {
    summaryMessage = fullMessage;
  }

  return (
    <div style={{ fontSize: '11px', color: 'var(--danger)', marginTop: '6px', background: 'var(--danger-muted)', padding: '6px 8px', borderRadius: '4px', borderLeft: '2px solid var(--danger)' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '8px' }}>
        <span>
          <Info size={12} style={{ display: 'inline', marginRight: '4px', verticalAlign: 'text-bottom' }}/>
          {summaryMessage}
        </span>
        <button 
          onClick={() => setExpanded(!expanded)} 
          style={{ background: 'none', border: '1px solid var(--border)', borderRadius: '3px', color: 'var(--text-main)', cursor: 'pointer', fontSize: '10px', padding: '2px 6px', flexShrink: 0 }}
        >
          {expanded ? 'Hide' : 'View details'}
        </button>
      </div>
      {expanded && (
        <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid var(--border)', fontFamily: 'var(--font-mono)', fontSize: '10px', whiteSpace: 'pre-wrap', wordBreak: 'break-word', color: 'var(--text-main)' }}>
          {fullMessage}
        </div>
      )}
    </div>
  );
};

const Overview = () => {
  const [summary, setSummary] = useState(null);
  const [health, setHealth] = useState(null);
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sumData, healthData, anomData] = await Promise.all([
          api.getPlatformSummary(),
          api.getHealth().catch(() => ({ status: 'down' })),
          api.getAnomalies().catch(() => [])
        ]);
        setSummary(sumData);
        setHealth(healthData);
        setAnomalies(anomData || []);
      } catch (error) {
        console.error('Failed to fetch overview data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className='page-scroll mono'>[SYSTEM] Booting metrics telemetry...</div>;
  if (summary?.error) return <div className='page-scroll mono' style={{color: 'var(--danger)'}}>[ERROR] {summary.error}</div>;

  const isHealthy = health?.status === 'healthy';
  const incidentCount = anomalies.length;
  
  const pipelineRuns = summary?.pipeline_runs || [];
  const totalRuns = pipelineRuns.length;
  
  // Calculate Reliability Score
  let reliabilityScore = 'Unavailable';
  if (totalRuns > 0) {
    const successfulRuns = pipelineRuns.filter(r => ['success', 'Completed'].includes(r.status)).length;
    reliabilityScore = `${((successfulRuns / totalRuns) * 100).toFixed(1)}%`;
  }
  
  // Calculate Pipeline Freshness
  let pipelineFreshness = 'Unavailable';
  if (totalRuns > 0) {
    const validRuns = pipelineRuns.filter(r => r.start_time || r.timestamp);
    if (validRuns.length > 0) {
      const latestRun = validRuns.reduce((latest, run) => {
        const time = new Date(run.start_time || run.timestamp).getTime();
        return time > latest.time ? { time, run } : latest;
      }, { time: 0, run: null }).run;
      
      if (latestRun) {
        pipelineFreshness = formatTime(latestRun.start_time || latestRun.timestamp);
      }
    }
  }

  const resolvePipelineName = (run) => {
    if (run.id && !run.item_id) return run.id; // local fallback
    if (run.item_id === '9544e045-6914-49b8-92ca-56cb8cd64185') return 'DataSentinel_Batch_Pipeline';
    return run.item_id ? `Pipeline_${run.item_id.substring(0, 8)}` : 'Unknown Pipeline';
  };

  return (
    <>
      <div className='page-header'>
        <h1 className='page-title'>Platform Telemetry</h1>
        <div className='mono text-muted'>sys.uptime: {isHealthy ? '99.99%' : 'Degraded'}</div>
      </div>

      <div className='page-scroll'>
        <div className='grid grid-cols-4' style={{marginBottom: '24px'}}>
          <div className='card'>
            <div className='card-header'>
              <h3 className='card-title'><Activity size={14}/> Reliability</h3>
              <span className={`badge ${reliabilityScore !== 'Unavailable' ? 'badge-success' : 'badge-neutral'}`}>STABLE</span>
            </div>
            <p className='metric-value'>{reliabilityScore}</p>
          </div>
          <div className='card'>
            <div className='card-header'>
              <h3 className='card-title'><Database size={14}/> Pipeline Freshness</h3>
              <span className='badge badge-neutral'>LATEST RUN</span>
            </div>
            <p className='metric-value'>{pipelineFreshness}</p>
          </div>
          <div className='card'>
            <div className='card-header'>
              <h3 className='card-title'><AlertTriangle size={14}/> Active Incidents</h3>
              <span className={`badge ${incidentCount > 0 ? 'badge-danger' : 'badge-success'}`}>
                {incidentCount > 0 ? 'CRITICAL' : 'CLEAR'}
              </span>
            </div>
            <p className='metric-value'>{incidentCount}</p>
          </div>
          <div className='card'>
            <div className='card-header'>
              <h3 className='card-title'><ShieldCheck size={14}/> API Status</h3>
              <span className={`badge ${isHealthy ? 'badge-success' : 'badge-danger'}`}>
                {isHealthy ? 'ONLINE' : 'OFFLINE'}
              </span>
            </div>
            <p className='metric-value'>{isHealthy ? '200 OK' : 'Unavailable'}</p>
          </div>
        </div>

        <div className='grid grid-cols-2'>
          <div className='card' style={{height: '350px'}}>
            <h3 className='card-title'>Revenue Pipeline Flow (Last 7 Days)</h3>
            <div style={{ flex: 1, marginTop: '16px' }}>
              <ResponsiveContainer width='100%' height='100%'>
                <LineChart data={(summary?.revenue_trend || []).map(r => ({...r, display_revenue: r.daily_revenue ?? r.total_revenue ?? r.revenue ?? 0}))}>
                  <CartesianGrid strokeDasharray='3 3' stroke='var(--border)' vertical={false} />
                  <XAxis dataKey='date' stroke='var(--text-muted)' fontSize={11} tickFormatter={(v) => formatDate(v)} />
                  <YAxis stroke='var(--text-muted)' fontSize={11} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--bg-panel)', border: '1px solid var(--border)', fontFamily: 'var(--font-mono)', fontSize: '11px' }} />
                  <Line type='monotone' dataKey='display_revenue' stroke='var(--accent)' strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className='card' style={{height: '350px', overflowY: 'auto'}}>
            <h3 className='card-title'>Latest Pipeline Executions</h3>
            <table style={{marginTop: '12px'}}>
              <thead>
                <tr>
                  <th>Pipeline</th>
                  <th>Status</th>
                  <th>Started</th>
                  <th>Invoked By</th>
                </tr>
              </thead>
              <tbody>
                {pipelineRuns.map((run, i) => {
                  const isFailed = ['Failed', 'failed', 'Error'].includes(run.status);
                  return (
                    <tr key={i}>
                      <td>
                        <div style={{ fontWeight: 500 }}>{resolvePipelineName(run)}</div>
                        {isFailed && run.failure_reason && (
                          <ErrorDetails failureReason={run.failure_reason} />
                        )}
                      </td>
                      <td>
                        <span className={`badge ${['success', 'Completed'].includes(run.status) ? 'badge-success' : (isFailed ? 'badge-danger' : 'badge-warning')}`}>
                          {run.status || 'UNKNOWN'}
                        </span>
                      </td>
                      <td>
                        {run.start_time ? formatTime(run.start_time) : (run.timestamp ? formatTime(run.timestamp) : 'Unavailable')}
                      </td>
                      <td>{run.invoke_type || 'Manual'}</td>
                    </tr>
                  )
                })}
                {pipelineRuns.length === 0 && (
                  <tr>
                    <td colSpan="4" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>No pipeline executions found.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </>
  );
};

export default Overview;
