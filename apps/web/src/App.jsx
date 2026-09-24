import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { Activity, Database, AlertTriangle, TrendingUp, Terminal, ShieldCheck, GitCommit } from 'lucide-react';
import Overview from './pages/Overview';
import AIInvestigation from './pages/AIInvestigation';
import DataQuality from './pages/DataQuality';
import Pipelines from './pages/Pipelines';
import Anomalies from './pages/Anomalies';
import Metrics from './pages/Metrics';
import DataLineage from './pages/DataLineage';

const Sidebar = () => (
  <div className='sidebar'>
    <div className='sidebar-header'>
      <Terminal size={18} className='text-accent' />
      DATAPULSE OPS
    </div>
    <div className='nav-links'>
      <NavLink to='/' className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>
        <Activity size={16} /> Overview
      </NavLink>
      <NavLink to='/pipelines' className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>
        <Database size={16} /> Pipeline Operations
      </NavLink>
      <NavLink to='/quality' className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>
        <ShieldCheck size={16} /> Data Quality
      </NavLink>
      <NavLink to='/anomalies' className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>
        <AlertTriangle size={16} /> Anomaly Detection
      </NavLink>
      <NavLink to='/business' className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>
        <TrendingUp size={16} /> Business Metrics
      </NavLink>
      <NavLink to='/investigate' className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>
        <Terminal size={16} /> AI Assistant
      </NavLink>
      <NavLink to='/lineage' className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}>
        <GitCommit size={16} /> Data Lineage
      </NavLink>
    </div>
  </div>
);

const App = () => {
  return (
    <Router>
      <div className='app-container'>
        <Sidebar />
        <div className='main-content'>
          <Routes>
            <Route path='/' element={<Overview />} />
            <Route path='/pipelines' element={<Pipelines />} />
            <Route path='/quality' element={<DataQuality />} />
            <Route path='/anomalies' element={<Anomalies />} />
            <Route path='/business' element={<Metrics />} />
            <Route path='/investigate' element={<AIInvestigation />} />
            <Route path='/lineage' element={<DataLineage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

export default App;
