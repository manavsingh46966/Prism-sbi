import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { api } from './utils/api';
import Dashboard from './pages/Dashboard';
import DormantPage from './pages/DormantPage';
import HeatmapPage from './pages/HeatmapPage';
import LeadsPage from './pages/LeadsPage';
import IndividualProfile from './pages/IndividualProfile';
import EngagementPage from './pages/EngagementPage';
import ActivationPage from './pages/ActivationPage';
import CompliancePage from './pages/CompliancePage';
import './App.css';
 
const NAV = [
  { path: '/',           label: 'Overview',          icon: 'dashboard',               exact: true },
  { path: '/dormant',    label: 'Dormant Recovery',  icon: 'settings_backup_restore', badge: 'L0' },
  { path: '/heatmap',    label: 'Territory Intel',   icon: 'map',                     badge: 'L1' },
  { path: '/leads',      label: 'Lead Intelligence', icon: 'person_search',           badge: 'L2' },
  { path: '/engagement', label: 'Engagement',        icon: 'analytics',               badge: 'L3' },
  { path: '/activation', label: 'Activation',        icon: 'bolt',                    badge: 'L4' },
  { path: '/compliance', label: 'Compliance',        icon: 'verified_user',           badge: 'L5' },
];
 
const TOPBAR_LABELS = {
  '/': { tag: 'PRISM — Predictive Regional Intelligence', search: 'Search Intel...' },
  '/dormant': { tag: 'Agent 0 — Dormant Recovery Agent', search: 'Search accounts...' },
  '/heatmap': { tag: 'Layer 1 — Territory Intelligence Agent', search: 'Search districts...' },
  '/leads': { tag: 'Level 2  Lead Intelligence Dashboard', search: 'Search leads...' },
  '/engagement': { tag: 'Layer 3 — Contextual Agent', search: 'Search accounts...' },
  '/activation': { tag: 'Layer 4 — Activation Intelligence Agent', search: 'Search accounts...' },
  '/compliance': { tag: 'Layer 5 — Compliance & Consent Orchestrator', search: 'Search logs...' },
};
 
function AiStatusBadge() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    let mounted = true;
    api.get('/ai/status')
      .then(s => { if (mounted) setStatus(s); })
      .catch(() => { if (mounted) setStatus({ ai_enabled: false, mode: 'unreachable' }); });
    return () => { mounted = false; };
  }, []);

  if (!status) return null;

  const live = status.ai_enabled;
  return (
    <div
      className="topbar-icon-btn"
      title={live
        ? `Live agentic AI — model: ${status.model} — ${status.calls_made} calls made`
        : 'Rule-based fallback — set ANTHROPIC_API_KEY in backend/.env to enable live AI'}
      style={{
        display: 'flex', alignItems: 'center', gap: 6, padding: '4px 10px',
        borderRadius: 999, fontSize: 12, fontWeight: 600,
        background: live ? 'rgba(0,212,160,0.12)' : 'rgba(245,166,35,0.12)',
        color: live ? '#00d4a0' : '#f5a623',
        border: `1px solid ${live ? '#00d4a0' : '#f5a623'}`,
      }}
    >
      <span style={{ width: 7, height: 7, borderRadius: '50%', background: live ? '#00d4a0' : '#f5a623', display: 'inline-block' }} />
      {live ? 'Live AI' : 'Rule-based fallback'}
    </div>
  );
}

function Topbar() {
  const location = useLocation();
  const key = Object.keys(TOPBAR_LABELS).find(k => location.pathname === k) || '/';
  const { tag, search } = TOPBAR_LABELS[key];
  return (
    <div className="topbar">
      <div className="topbar-breadcrumb">
        <span className="breadcrumb-tag">⊙ {tag}</span>
      </div>
      <div className="topbar-search">
        <span className="search-icon material-symbols-outlined">search</span>
        <input placeholder={search} />
      </div>
      <div className="topbar-actions">
        <AiStatusBadge />
        <div className="topbar-icon-btn material-symbols-outlined">notifications</div>
        <div className="topbar-icon-btn material-symbols-outlined">account_circle</div>
      </div>
    </div>
  );
}
 
function App() {
  return (
    <Router>
      <div className="app">
        <aside className="sidebar">
          <div className="sidebar-header">
            <div className="logo">
              <span className="logo-name">PRISM</span>
              <span className="logo-sub">Financial Intelligence</span>
            </div>
          </div>
          <nav className="sidebar-nav">
            {NAV.map(item => (
              <NavLink key={item.path} to={item.path} end={item.exact}
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
                <span className="nav-icon material-symbols-outlined">{item.icon}</span>
                <span className="nav-label">{item.label}</span>
                {item.badge && <span className="nav-badge">{item.badge}</span>}
              </NavLink>
            ))}
            <div className="sidebar-divider" />
            <div className="nav-item"><span className="nav-icon material-symbols-outlined">help</span><span className="nav-label">Support</span></div>
            <div className="nav-item"><span className="nav-icon material-symbols-outlined">settings</span><span className="nav-label">Settings</span></div>
          </nav>
          <div className="user-section">
            <div className="user-avatar">AR</div>
            <div>
              <div className="user-name">Alex Rivera</div>
              <div className="user-role">Administrator</div>
            </div>
          </div>
        </aside>
        <div className="main-content">
          <Topbar />
          <div className="page-content">
            <Routes>
              <Route path="/"           element={<Dashboard />} />
              <Route path="/dormant"    element={<DormantPage />} />
              <Route path="/heatmap"    element={<HeatmapPage />} />
              <Route path="/leads"      element={<LeadsPage />} />
              <Route path="/leads/:id"  element={<IndividualProfile />} />
              <Route path="/engagement" element={<EngagementPage />} />
              <Route path="/activation" element={<ActivationPage />} />
              <Route path="/compliance" element={<CompliancePage />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}
export default App;