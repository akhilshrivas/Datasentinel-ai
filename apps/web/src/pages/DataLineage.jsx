import React, { useEffect, useState, useRef } from 'react';
import { api } from '../api';
import { GitCommit, RefreshCw, AlertTriangle, Database, Activity, HardDrive, Terminal, X } from 'lucide-react';

const LAYER_ORDER = ['Source', 'Bronze', 'Silver', 'Gold', 'Real-time', 'Serving'];

const getEntityIcon = (entity) => {
  const iconProps = { size: 14 };
  switch (entity) {
    case 'source': return <HardDrive {...iconProps} style={{ color: '#a1a1aa' }} />;
    case 'table': return <Database {...iconProps} style={{ color: '#60a5fa' }} />;
    case 'stream': return <Activity {...iconProps} style={{ color: '#c084fc' }} />;
    case 'kql_db': return <Database {...iconProps} style={{ color: '#22d3ee' }} />;
    case 'api': return <Terminal {...iconProps} style={{ color: '#4ade80' }} />;
    default: return <Database {...iconProps} style={{ color: '#a1a1aa' }} />;
  }
};

const DataLineage = () => {
  const [data, setData] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);

  const containerRef = useRef(null);
  const [nodeRefs, setNodeRefs] = useState({});
  const [edgePaths, setEdgePaths] = useState([]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getLineage();
      if (res && res.error) {
        setError(res.error);
        setData({ nodes: [], edges: [] });
      } else if (res && res.nodes) {
        setData(res);
      } else {
        setError("Invalid lineage data received");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const registerNodeRef = (id, el) => {
    if (el) {
      setNodeRefs(prev => {
        if (prev[id] === el) return prev;
        return { ...prev, [id]: el };
      });
    }
  };

  const drawEdges = () => {
    if (!containerRef.current || !data.edges || data.edges.length === 0) return;
    
    const containerRect = containerRef.current.getBoundingClientRect();
    const paths = [];

    data.edges.forEach(edge => {
      const srcEl = nodeRefs[edge.source];
      const tgtEl = nodeRefs[edge.target];
      if (srcEl && tgtEl) {
        const srcRect = srcEl.getBoundingClientRect();
        const tgtRect = tgtEl.getBoundingClientRect();

        const startX = srcRect.right - containerRect.left;
        const startY = srcRect.top + srcRect.height / 2 - containerRect.top;
        const endX = tgtRect.left - containerRect.left;
        const endY = tgtRect.top + tgtRect.height / 2 - containerRect.top;

        const controlOffset = Math.max(Math.abs(endX - startX) / 2, 20);
        const d = `M ${startX} ${startY} C ${startX + controlOffset} ${startY}, ${endX - controlOffset} ${endY}, ${endX} ${endY}`;
        
        let isHighlighted = false;
        let isDimmed = false;
        if (selectedNode) {
          if (edge.source === selectedNode.id || edge.target === selectedNode.id) {
            isHighlighted = true;
          } else {
            isDimmed = true;
          }
        }

        paths.push({
          id: `${edge.source}-${edge.target}`,
          d,
          isHighlighted,
          isDimmed
        });
      }
    });
    setEdgePaths(paths);
  };

  useEffect(() => {
    const timer = setTimeout(drawEdges, 100);
    window.addEventListener('resize', drawEdges);
    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', drawEdges);
    };
  }, [data, nodeRefs, selectedNode]);

  const nodesByLayer = {};
  LAYER_ORDER.forEach(l => nodesByLayer[l] = []);
  
  data.nodes.forEach(n => {
    const layer = n.layer || 'Source';
    if (!nodesByLayer[layer]) nodesByLayer[layer] = [];
    nodesByLayer[layer].push(n);
  });

  return (
    <div className="page-scroll">
      <style>{`
        .lin-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .lin-alert { border: 1px solid var(--danger); background: var(--danger-muted); color: var(--danger); padding: 16px; border-radius: 6px; display: flex; gap: 12px; margin-bottom: 24px; }
        .lin-layout { display: flex; gap: 16px; align-items: flex-start; }
        .lin-graph-container { flex: 1; background: var(--bg-panel); border: 1px solid var(--border); border-radius: 6px; overflow-x: auto; overflow-y: hidden; min-height: 600px; }
        .lin-canvas { position: relative; min-width: max-content; height: 100%; min-height: 600px; }
        .lin-svg { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; }
        .lin-columns { display: flex; flex-direction: row; justify-content: space-between; height: 100%; gap: 32px; position: relative; z-index: 10; padding: 32px 16px; }
        .lin-column { display: flex; flex-direction: column; gap: 16px; width: 180px; flex-shrink: 0; }
        .lin-col-title { font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 700; letter-spacing: 1px; text-align: center; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 8px; margin-top: 0; }
        .lin-nodes-wrap { display: flex; flex-direction: column; gap: 12px; }
        .lin-node { padding: 12px; border-radius: 6px; border: 1px solid var(--border); background: var(--bg-app); font-size: 12px; cursor: pointer; transition: all 0.2s; }
        .lin-node:hover { border-color: #6b7280; background: var(--bg-panel-hover); }
        .lin-node.selected { background: rgba(59, 130, 246, 0.15); border-color: var(--accent); box-shadow: 0 0 10px rgba(59, 130, 246, 0.3); }
        .lin-node.dimmed { background: #111827; border-color: #1f2937; opacity: 0.4; }
        .lin-node-header { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
        .lin-node-name { font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .lin-node-meta { display: flex; justify-content: space-between; align-items: center; color: var(--text-muted); font-size: 10px; }
        .lin-node-rows { background: var(--bg-panel); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); }
        .lin-sidebar { width: 300px; background: var(--bg-panel); border: 1px solid var(--border); border-radius: 6px; padding: 16px; }
        .lin-sb-header { font-weight: 600; border-bottom: 1px solid var(--border); padding-bottom: 8px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
        .lin-sb-close { cursor: pointer; color: var(--text-muted); background: none; border: none; }
        .lin-sb-close:hover { color: var(--text-main); }
        .lin-sb-id { display: flex; align-items: center; gap: 8px; color: var(--accent); font-family: var(--font-mono); font-size: 13px; margin-bottom: 16px; word-break: break-all; }
        .lin-sb-grid { display: flex; flex-direction: column; gap: 12px; font-size: 13px; }
        .lin-sb-label { color: var(--text-muted); font-size: 11px; margin-bottom: 4px; }
        .lin-sb-val { font-weight: 500; text-transform: capitalize; }
        .lin-sb-mono { font-family: var(--font-mono); }
        .lin-sb-deps { border-top: 1px solid var(--border); padding-top: 12px; margin-top: 12px; }
        .lin-sb-list { margin: 0; padding-left: 16px; font-size: 12px; color: var(--text-main); }
        .lin-path { transition: all 0.3s ease; }
        @keyframes lin-spin { 100% { transform: rotate(360deg); } }
      `}</style>
      
      <div className="lin-header">
        <h1 className="page-title flex items-center gap-2" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <GitCommit style={{ color: 'var(--accent)' }} /> Data Lineage
        </h1>
        <button onClick={fetchData} className="btn" disabled={loading}>
          <RefreshCw size={14} style={loading ? { animation: 'lin-spin 1s linear infinite' } : {}} />
          Refresh Lineage
        </button>
      </div>

      {error && (
        <div className="lin-alert">
          <AlertTriangle size={18} />
          <div>
            <div style={{ fontWeight: 'bold' }}>Error loading lineage graph</div>
            <div style={{ fontSize: '12px', opacity: 0.8 }}>{error}</div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="card" style={{ padding: '80px', textAlign: 'center', color: 'var(--text-muted)' }}>
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}>
            <RefreshCw size={18} style={{ animation: 'lin-spin 1s linear infinite' }} /> 
            Rendering Architecture...
          </div>
        </div>
      ) : data.nodes.length === 0 ? (
        <div className="card" style={{ padding: '80px', textAlign: 'center', color: 'var(--text-muted)' }}>
          No lineage data available.
        </div>
      ) : (
        <div className="lin-layout">
          <div className="lin-graph-container" onScroll={drawEdges}>
            <div className="lin-canvas" ref={containerRef}>
              <svg className="lin-svg">
                <defs>
                  <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                    <polygon points="0 0, 6 3, 0 6" fill="#4B5563" />
                  </marker>
                  <marker id="arrowhead-highlight" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
                    <polygon points="0 0, 6 3, 0 6" fill="#3B82F6" />
                  </marker>
                </defs>
                {edgePaths.map(p => (
                  <path 
                    key={p.id} 
                    d={p.d} 
                    fill="none" 
                    stroke={p.isHighlighted ? '#3B82F6' : p.isDimmed ? '#1F2937' : '#4B5563'} 
                    strokeWidth={p.isHighlighted ? 2 : 1}
                    markerEnd={`url(#${p.isHighlighted ? 'arrowhead-highlight' : 'arrowhead'})`}
                    className="lin-path"
                  />
                ))}
              </svg>
              
              <div className="lin-columns">
                {LAYER_ORDER.map(layer => {
                  const layerNodes = nodesByLayer[layer];
                  if (!layerNodes || layerNodes.length === 0) return null;
                  
                  return (
                    <div key={layer} className="lin-column">
                      <h3 className="lin-col-title">{layer}</h3>
                      <div className="lin-nodes-wrap">
                        {layerNodes.map(node => {
                          const isSelected = selectedNode && selectedNode.id === node.id;
                          let isDimmed = false;
                          if (selectedNode && !isSelected) {
                            const connected = data.edges.some(e => 
                              (e.source === node.id && e.target === selectedNode.id) ||
                              (e.target === node.id && e.source === selectedNode.id)
                            );
                            if (!connected) isDimmed = true;
                          }

                          let nodeClass = "lin-node";
                          if (isSelected) nodeClass += " selected";
                          else if (isDimmed) nodeClass += " dimmed";

                          return (
                            <div 
                              key={node.id}
                              ref={el => registerNodeRef(node.id, el)}
                              onClick={() => setSelectedNode(isSelected ? null : node)}
                              className={nodeClass}
                            >
                              <div className="lin-node-header">
                                {getEntityIcon(node.entity)}
                                <span className="lin-node-name" title={node.name}>{node.name}</span>
                              </div>
                              <div className="lin-node-meta">
                                <span>{node.status === 'unknown' ? 'Metadata' : 'Verified'}</span>
                                {node.rows !== undefined && (
                                  <span className="lin-node-rows">
                                    {node.rows === null ? 'N/A' : node.rows.toLocaleString()}
                                  </span>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
          
          {selectedNode && (
            <div className="lin-sidebar">
              <div className="lin-sb-header">
                Node Details
                <button onClick={() => setSelectedNode(null)} className="lin-sb-close"><X size={16} /></button>
              </div>
              
              <div className="lin-sb-id">
                {getEntityIcon(selectedNode.entity)}
                <span>{selectedNode.id}</span>
              </div>
              
              <div className="lin-sb-grid">
                <div>
                  <div className="lin-sb-label">Layer</div>
                  <div className="lin-sb-val">{selectedNode.layer}</div>
                </div>
                
                <div>
                  <div className="lin-sb-label">Entity Type</div>
                  <div className="lin-sb-val">{selectedNode.entity.replace('_', ' ')}</div>
                </div>
                
                <div>
                  <div className="lin-sb-label">Status</div>
                  <div className="lin-sb-val">
                    {selectedNode.status === 'unknown' ? (
                      <span style={{ color: 'var(--warning)' }}>Metadata-based (Unknown)</span>
                    ) : (
                      <span style={{ color: 'var(--success)' }}>Verified</span>
                    )}
                  </div>
                </div>
                
                {selectedNode.rows !== undefined && (
                  <div>
                    <div className="lin-sb-label">Row Count</div>
                    <div className="lin-sb-val lin-sb-mono">
                      {selectedNode.rows === null ? 'N/A' : selectedNode.rows.toLocaleString()}
                    </div>
                  </div>
                )}
                
                <div className="lin-sb-deps">
                  <div className="lin-sb-label">Downstream Dependencies</div>
                  <ul className="lin-sb-list">
                    {data.edges.filter(e => e.source === selectedNode.id).map(e => (
                      <li key={e.target}>{e.target}</li>
                    ))}
                    {data.edges.filter(e => e.source === selectedNode.id).length === 0 && (
                      <li style={{ listStyle: 'none', marginLeft: '-16px', color: 'var(--text-muted)' }}>None</li>
                    )}
                  </ul>
                </div>
                
                <div className="lin-sb-deps">
                  <div className="lin-sb-label">Upstream Sources</div>
                  <ul className="lin-sb-list">
                    {data.edges.filter(e => e.target === selectedNode.id).map(e => (
                      <li key={e.source}>{e.source}</li>
                    ))}
                    {data.edges.filter(e => e.target === selectedNode.id).length === 0 && (
                      <li style={{ listStyle: 'none', marginLeft: '-16px', color: 'var(--text-muted)' }}>None</li>
                    )}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DataLineage;
