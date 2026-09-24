import React, { useState } from 'react';
import { api } from '../api';
import { Send, ChevronRight, Activity } from 'lucide-react';

import { formatTime } from '../utils/formatters';

const AIInvestigation = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = { role: 'user', content: query, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMessage]);
    setQuery('');
    setLoading(true);
    setError(null);

    const startTime = Date.now();

    try {
      const response = await api.chatWithAgent(userMessage.content);
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);
      
      const agentMessage = { 
        role: 'agent', 
        content: response.reply,
        toolCalls: response.tool_calls || [],
        elapsed,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, agentMessage]);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || err.message || 'Connection error.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div className='page-header'>
        <h1 className='page-title'>Agent Workspace</h1>
        <div className='mono text-muted'>session_id: 0x8F9A2B</div>
      </div>

      <div className='page-scroll' style={{ display: 'flex', flexDirection: 'column', padding: '24px' }}>
        <div className='workspace'>
          <div className='workspace-log'>
            {messages.length === 0 && (
              <div style={{ color: 'var(--text-muted)' }}>
                [System] Initialization complete.<br/>
                [System] Agent 'DataSentinel-Zero' ready for commands.<br/><br/>
                <span style={{color: 'var(--accent)'}}>Suggested commands:</span><br/>
                - Analyze recent revenue drop<br/>
                - Check pipeline bronze_ingest status<br/>
                - Correlate anomalies with data quality failures
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={idx} className='log-entry'>
                <span className='log-time'>{formatTime(msg.timestamp)}</span>
                <span className={msg.role === 'user' ? 'log-user' : 'log-agent'}>
                  {msg.role === 'user' ? 'op_admin@local' : 'agent@datasentinel'}
                </span>
                <span className='text-muted'>$</span>
                <div style={{ marginTop: '8px', lineHeight: '1.6' }}>
                  {msg.content}
                </div>
                
                {msg.toolCalls && msg.toolCalls.length > 0 && (
                  <div style={{ marginTop: '16px' }}>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px' }}>
                      <Activity size={12} style={{display: 'inline', marginRight: '4px'}}/>
                      Telemetry Ops Executed ({msg.elapsed}s)
                    </div>
                    {msg.toolCalls.map((tool, tIdx) => (
                      <div key={tIdx} className='log-tool'>
                        <span style={{ color: 'var(--accent)' }}>func:</span> {tool.name}<br/>
                        <span style={{ color: 'var(--text-muted)' }}>args:</span> <span style={{ color: 'var(--warning)' }}>{JSON.stringify(tool.arguments || tool.args || {})}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
            
            {loading && (
              <div className='log-entry'>
                <span className='log-time'>{formatTime(new Date().toISOString())}</span>
                <span className='log-agent'>agent@datasentinel</span>
                <span className='text-muted'>$</span>
                <div style={{ marginTop: '8px', color: 'var(--text-muted)' }}>
                  Processing intelligence protocol... <span style={{ animation: 'pulse 1.5s infinite' }}>_</span>
                </div>
              </div>
            )}
            
            {error && (
              <div className='log-entry' style={{ backgroundColor: 'var(--danger-muted)', padding: '12px', borderLeft: '3px solid var(--danger)' }}>
                <span style={{ color: 'var(--danger)' }}>[FATAL EXCEPTION] {error}</span>
              </div>
            )}
          </div>
          
          <div style={{ padding: '12px 16px', borderTop: '1px solid var(--border)', background: 'var(--bg-panel)' }}>
            <form onSubmit={handleSubmit} style={{ display: 'flex', alignItems: 'center' }}>
              <ChevronRight size={18} className='text-muted' style={{ marginRight: '8px' }} />
              <input 
                type='text' 
                style={{ flex: 1, background: 'transparent', border: 'none', color: 'var(--text-main)', fontFamily: 'var(--font-mono)', fontSize: '13px', outline: 'none' }}
                placeholder='Enter agent command...' 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={loading}
                autoFocus
              />
              <button type='submit' style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--accent)' }} disabled={loading || !query.trim()}>
                <Send size={16} />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIInvestigation;
