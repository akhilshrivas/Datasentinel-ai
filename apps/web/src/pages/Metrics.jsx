import React, { useEffect, useState } from 'react';
import { api } from '../api';
import { TrendingUp, Users, ShoppingCart, DollarSign } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { formatDate } from '../utils/formatters';

const Metrics = () => {
  const [data, setData] = useState({ kpis: {}, trend: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await api.getMetrics();
        if (response && response.error) {
          setError(response.error);
        } else {
          // Handle both new composite object {kpis, trend} and legacy array fallback
          if (response && !Array.isArray(response) && response.kpis) {
            setData(response);
          } else if (Array.isArray(response)) {
            setData({ kpis: {}, trend: response });
          } else {
            setData({ kpis: {}, trend: [] });
          }
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className='page-scroll mono'>[SYSTEM] Aggregating BI endpoints from Lakehouse...</div>;
  if (error) return <div className='page-scroll mono' style={{color: 'var(--danger)'}}>[ERROR] {error}</div>;

  const { kpis, trend } = data;
  
  // Convert for chart: reverse to show oldest to newest left-to-right
  const chartData = [...trend].reverse().map(m => ({
    ...m,
    display_date: m.date || 'Unknown',
    display_orders: m.orders || 0,
    display_revenue: m.revenue || 0
  }));

  const formatCurrency = (val) => val == null ? 'N/A' : `$${Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const formatNumber = (val) => val == null ? 'N/A' : Number(val).toLocaleString();

  return (
    <>
      <div className='page-header'>
        <h1 className='page-title'>Business Metrics (KPIs)</h1>
        <div className='mono text-muted'>source: gold.daily_revenue, gold.customer_metrics</div>
      </div>
      
      <div className='page-scroll'>
        
        {/* KPI Cards */}
        <div className='grid grid-cols-4' style={{ marginBottom: '24px' }}>
          <div className='card'>
            <div className='card-header'>
              <h3 className='card-title'><ShoppingCart size={14}/> Total Orders</h3>
              <span className='badge badge-neutral'>{kpis.period_label || 'SELECTED PERIOD'}</span>
            </div>
            <p className='metric-value'>{formatNumber(kpis.total_orders)}</p>
          </div>
          
          <div className='card'>
            <div className='card-header'>
              <h3 className='card-title'><DollarSign size={14}/> Total Revenue</h3>
              <span className='badge badge-neutral'>{kpis.period_label || 'SELECTED PERIOD'}</span>
            </div>
            <p className='metric-value'>{formatCurrency(kpis.total_revenue)}</p>
          </div>

          <div className='card'>
            <div className='card-header'>
              <h3 className='card-title'><TrendingUp size={14}/> Avg Order Value</h3>
              <span className='badge badge-neutral'>{kpis.period_label || 'SELECTED PERIOD'}</span>
            </div>
            <p className='metric-value'>{formatCurrency(kpis.average_order_value)}</p>
          </div>

          <div className='card'>
            <div className='card-header'>
              <h3 className='card-title'><Users size={14}/> Unique Customers</h3>
              <span className='badge badge-neutral'>{kpis.period_label || 'SELECTED PERIOD'}</span>
            </div>
            <p className='metric-value'>{formatNumber(kpis.unique_customers)}</p>
          </div>
        </div>

        {/* Chart Section */}
        <div className='grid grid-cols-2'>
          <div className='card' style={{ height: '400px' }}>
            <h3 className='card-title'>Orders Trendline</h3>
            <div style={{ flex: 1, marginTop: '16px' }}>
              <ResponsiveContainer width='100%' height='100%'>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray='3 3' stroke='var(--border)' vertical={false} />
                  <XAxis dataKey='display_date' stroke='var(--text-muted)' fontSize={11} tickFormatter={(v) => (v && !isNaN(Date.parse(v))) ? formatDate(v) : v} />
                  <YAxis stroke='var(--text-muted)' fontSize={11} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--bg-panel)', border: '1px solid var(--border)', fontFamily: 'var(--font-mono)', fontSize: '11px' }} />
                  <Line type='step' dataKey='display_orders' name='Orders' stroke='var(--accent)' strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className='card' style={{ height: '400px' }}>
            <h3 className='card-title'>Revenue Trendline</h3>
            <div style={{ flex: 1, marginTop: '16px' }}>
              <ResponsiveContainer width='100%' height='100%'>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray='3 3' stroke='var(--border)' vertical={false} />
                  <XAxis dataKey='display_date' stroke='var(--text-muted)' fontSize={11} tickFormatter={(v) => (v && !isNaN(Date.parse(v))) ? formatDate(v) : v} />
                  <YAxis stroke='var(--text-muted)' fontSize={11} tickFormatter={(v) => `$${v}`} />
                  <Tooltip contentStyle={{ backgroundColor: 'var(--bg-panel)', border: '1px solid var(--border)', fontFamily: 'var(--font-mono)', fontSize: '11px' }} formatter={(val) => [`$${val}`, 'Revenue']} />
                  <Line type='monotone' dataKey='display_revenue' name='Revenue' stroke='var(--success)' strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

      </div>
    </>
  );
};

export default Metrics;
