import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { ShieldAlert, ShieldCheck, Database, Layers, CheckCircle, AlertTriangle } from 'lucide-react';
import { formatDateTime } from '../utils/formatters';

const DataQuality = () => {
  const [quality, setQuality] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await api.getLatestQuality();
        if (data && data.error) {
          setError(data.error);
          setQuality([]);
        } else {
          setQuality(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className='page-scroll mono'>[SYSTEM] Validating dataset constraints against Lakehouse...</div>;
  if (error) return <div className='page-scroll mono' style={{color: 'var(--danger)'}}>[ERROR] {error}</div>;

  const tablesChecked = quality.length;
  const totalRows = quality.reduce((acc, curr) => acc + (curr.total_rows || 0), 0);
  const tablesWithIssues = quality.filter(q => q.status === 'failed' || q.status === 'warn').length;
  const tablesPassing = tablesChecked - tablesWithIssues;

  return (
    <>
      <div className='page-header' style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h1 className='page-title'>Data Quality Enforcement</h1>
          <div className='mono text-muted'>sys.active_checks: {tablesChecked}</div>
        </div>
      </div>
      
      <div className='page-scroll'>
        <div className='grid grid-cols-4' style={{marginBottom: '24px'}}>
          <div className='card'>
            <div className='card-header'>
              <h3 className='card-title'><Database size={14}/> Tables Checked</h3>
              <span className='badge badge-neutral'>TOTAL</span>
            </div>
            <p className='metric-value'>{tablesChecked}</p>
          </div>
          <div className='card'>
            <div className='card-header'>
              <h3 className='card-title'><Layers size={14}/> Total Rows</h3>
              <span className='badge badge-neutral'>SCANNED</span>
            </div>
            <p className='metric-value'>{totalRows.toLocaleString()}</p>
          </div>
          <div className='card'>
            <div className='card-header'>
              <h3 className='card-title'><CheckCircle size={14}/> Tables Passing</h3>
              <span className='badge badge-success'>STABLE</span>
            </div>
            <p className='metric-value'>{tablesPassing}</p>
          </div>
          <div className='card'>
            <div className='card-header'>
              <h3 className='card-title'><AlertTriangle size={14}/> Tables With Issues</h3>
              <span className={`badge ${tablesWithIssues > 0 ? 'badge-danger' : 'badge-success'}`}>
                {tablesWithIssues > 0 ? 'CRITICAL' : 'CLEAR'}
              </span>
            </div>
            <p className='metric-value'>{tablesWithIssues}</p>
          </div>
        </div>

        <div className='table-container'>
          <table>
            <thead>
              <tr>
                <th>Dataset</th>
                <th>Rule Name</th>
                <th>Status</th>
                <th>Total Rows</th>
                <th>Failed Keys</th>
                <th>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {quality.map((q, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 500 }}>{q.dataset_name ?? 'Unavailable'}</td>
                  <td className='mono' style={{ fontSize: '12px' }}>{q.rule_name ?? 'Unavailable'}</td>
                  <td>
                    {q.status === 'failed' 
                      ? <span className='badge badge-danger'><ShieldAlert size={12} style={{marginRight:'4px'}}/> Failed</span>
                      : q.status === 'warn'
                      ? <span className='badge badge-warning'><ShieldAlert size={12} style={{marginRight:'4px'}}/> Warn</span>
                      : <span className='badge badge-success'><ShieldCheck size={12} style={{marginRight:'4px'}}/> Passed</span>
                    }
                  </td>
                  <td>{q.total_rows != null ? Number(q.total_rows).toLocaleString() : 'N/A'}</td>
                  <td style={{ color: q.failed_rows > 0 ? 'var(--danger)' : 'inherit' }}>
                    {q.failed_rows == null ? 'Not reported' : Number(q.failed_rows).toLocaleString()}
                    {q.failed_rows > 0 && (
                      <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
                        (Nulls: {q.null_keys || 0}, Dups: {q.duplicate_keys || 0})
                      </div>
                    )}
                  </td>
                  <td>{formatDateTime(q.execution_time)}</td>
                </tr>
              ))}
              {quality.length === 0 && (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>No quality rules executed in Lakehouse.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
};

export default DataQuality;
