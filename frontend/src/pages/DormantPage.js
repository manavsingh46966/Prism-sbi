import React, { useState, useEffect } from 'react';
import { api, formatPersona } from '../utils/api';

const avatarColors = ['#1a3a5c','#276749','#92400e','#553c9a','#9b2c2c'];
const getInitials = name => name.split(' ').map(n=>n[0]).join('').slice(0,2).toUpperCase();

export default function DormantPage() {
  const [accounts, setAccounts] = useState([]);
  const [stats, setStats] = useState(null);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reactivating, setReactivating] = useState(null);
  const [results, setResults] = useState({});
  const [filters, setFilters] = useState({ persona: 'all', min_score: 0 });

  useEffect(() => {
    const p = new URLSearchParams();
    if (filters.persona !== 'all') p.set('persona', filters.persona);
    if (filters.min_score > 0) p.set('min_score', filters.min_score);
    p.set('limit', '200');
    api.get(`/dormant?${p}`).then(d => { setAccounts(d.accounts || []); setStats(d.stats); }).finally(() => setLoading(false));
  }, [filters]);

  const loadDetail = async (id) => {
    setSelected(id);
    const d = await api.get(`/dormant/${id}`);
    setDetail(d);
  };

  const reactivate = async (id) => {
    setReactivating(id);
    try { const r = await api.post(`/dormant/reactivate/${id}`); setResults(p => ({ ...p, [id]: r })); }
    catch (e) { console.error(e); }
    finally { setReactivating(null); }
  };

  const scoreColor = s => s >= 70 ? '#38a169' : s >= 50 ? '#d97706' : '#e53e3e';
  const daysColor = d => d > 500 ? '#e53e3e' : d > 300 ? '#d97706' : '#718096';

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dormant Account Recovery</h1>
        <p className="page-subtitle">Reactivate existing SBI customers who went dormant — zero KYC, zero new consent, ₹12 cost vs ₹1,200 for new acquisition</p>
      </div>

      {/* Why This Matters */}
      <div style={{ background: '#fff', border: '1px solid #e2e8f0', borderLeft: '4px solid #3182ce', borderRadius: 8, padding: '16px 20px', marginBottom: 20 }}>
        <div style={{ fontSize: 11, color: '#3182ce', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600, marginBottom: 8 }}>⚡ WHY THIS MATTERS</div>
        <p style={{ fontSize: 13, color: '#4a5568', lineHeight: 1.7 }}>
          SBI has opened accounts for millions of customers who never transacted. These people already completed KYC. Consent is already on the file. Reactivating them costs <strong style={{ color: '#3182ce' }}>₹12</strong> vs <strong style={{ color: '#e53e3e' }}>₹1,200</strong> to acquire a new customer. This is the highest ROI opportunity in SBI's entire acquisition funnel — and almost nobody is working on it.
        </p>
      </div>

      {/* Stats */}
      {stats && (
        <div className="stats-grid" style={{ marginBottom: 20 }}>
          {[
            { label: 'DORMANT ACCOUNTS', value: stats.total_dormant_accounts },
            { label: 'HIGH PRIORITY', value: stats.high_priority, sub: 'Score 70+' },
            { label: 'AVG DAYS DORMANT', value: stats.avg_days_dormant, color: 'stat-red', sub: 'Days since last txn' },
            { label: 'IDLE BALANCE', value: stats.total_idle_balance, sub: 'Sitting unused' },
            { label: 'REACTIVATION COST', value: stats.cost_per_reactivation, color: 'stat-teal', sub: `vs ${stats.vs_new_acquisition_cost} new` },
            { label: 'TRIGGERED', value: stats.reactivations_triggered },
          ].map((s, i) => (
            <div key={i} className="stat-card">
              <div className="stat-label">{s.label}</div>
              <div className={`stat-value ${s.color || ''}`}>{s.value}</div>
              {s.sub && <div className="stat-sub">{s.sub}</div>}
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="filters">
        <select className="filter-select" value={filters.persona} onChange={e => setFilters(f => ({ ...f, persona: e.target.value }))}>
          <option value="all">All Personas</option>
          <option value="farmer">🚜 Farmer</option>
          <option value="gig_worker">🛵 Gig Worker</option>
          <option value="kirana">🏪 Kirana Owner</option>
          <option value="first_timer">👤 First Timer</option>
          <option value="nri">✈️ NRI</option>
        </select>
        <select className="filter-select" value={filters.min_score} onChange={e => setFilters(f => ({ ...f, min_score: Number(e.target.value) }))}>
          <option value={0}>All Scores</option>
          <option value={70}>High (70+)</option>
          <option value={80}>Very High (80+)</option>
        </select>
        <button className="btn btn-primary btn-sm" style={{ marginLeft: 'auto' }}>↓ Export List</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: selected ? '1fr 380px' : '1fr', gap: 16 }}>
        {/* Table */}
        <div className="card" style={{ padding: 0 }}>
          {loading ? <div className="loading"><div className="spinner"></div>Scanning dormant accounts...</div> : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr><th>CUSTOMER</th><th>ACCOUNT</th><th>PERSONA</th><th>DAYS DORMANT</th><th>BALANCE</th><th>REACTIVATION SCORE</th><th>OFFER</th><th>ADVANTAGE</th><th></th></tr>
                </thead>
                <tbody>
                  {accounts.slice(0, 80).map((acc, idx) => (
                    <tr key={acc.id} style={{ cursor: 'pointer', background: selected === acc.id ? '#ebf8ff' : '' }}
                      onClick={() => loadDetail(acc.id)}>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <div className="avatar" style={{ background: avatarColors[idx % 5], width: 32, height: 32, fontSize: 11 }}>{getInitials(acc.name)}</div>
                          <div>
                            <div style={{ color: '#1a202c', fontWeight: 500, fontSize: 13 }}>{acc.name}</div>
                            <div style={{ fontSize: 11, color: '#718096' }}>{acc.language}</div>
                          </div>
                        </div>
                      </td>
                      <td style={{ fontSize: 11, color: '#3182ce', fontFamily: 'monospace' }}>{acc.account_number?.slice(-6)}</td>
                      <td><span className={`persona-pill persona-${acc.persona_type}`}>{formatPersona(acc.persona_type)}</span></td>
                      <td style={{ color: daysColor(acc.days_dormant), fontWeight: 700 }}>{acc.days_dormant}d</td>
                      <td style={{ fontSize: 13 }}>₹{acc.account_balance?.toFixed(0)}</td>
                      <td>
                        <div className="score-bar">
                          <div className="score-track"><div className="score-fill" style={{ width: `${acc.reactivation_score}%`, background: scoreColor(acc.reactivation_score) }} /></div>
                          <span className="score-num" style={{ color: scoreColor(acc.reactivation_score) }}>{Math.round(acc.reactivation_score)}</span>
                        </div>
                      </td>
                      <td style={{ fontSize: 11, color: '#718096', maxWidth: 150 }}>{acc.reactivation_offer?.offer?.slice(0, 35)}...</td>
                      <td>
                        <div style={{ display: 'flex', gap: 4, flexDirection: 'column' }}>
                          <span className="tag tag-green" style={{ fontSize: 9 }}>✓ KYC done</span>
                          <span className="tag tag-green" style={{ fontSize: 9 }}>✓ Consent</span>
                        </div>
                      </td>
                      <td>
                        {results[acc.id] ? (
                          <span className="tag tag-green">✅ Sent</span>
                        ) : (
                          <button className="btn btn-primary btn-sm"
                            onClick={e => { e.stopPropagation(); reactivate(acc.id); }}
                            disabled={reactivating === acc.id}>
                            {reactivating === acc.id ? '...' : 'Reactivate'}
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Detail Panel */}
        {selected && detail && (
          <div className="card" style={{ overflowY: 'auto', maxHeight: 620 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
              <div>
                <div style={{ fontSize: 16, fontWeight: 700, color: '#1a202c' }}>{detail.account?.name}</div>
                <div style={{ fontSize: 11, color: '#718096', fontFamily: 'monospace' }}>{detail.account?.account_number}</div>
              </div>
              <button onClick={() => { setSelected(null); setDetail(null); }} style={{ background: 'none', border: 'none', color: '#718096', cursor: 'pointer', fontSize: 18 }}>×</button>
            </div>

            {/* Dormancy */}
            <div style={{ background: '#fff5f5', border: '1px solid #fed7d7', borderRadius: 8, padding: 12, marginBottom: 12 }}>
              <div style={{ fontSize: 10, color: '#e53e3e', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase' }}>DORMANCY DIAGNOSIS</div>
              <div style={{ fontSize: 13, color: '#1a202c', marginBottom: 4 }}>⏱ Dormant for {detail.account?.days_dormant} days</div>
              <div style={{ fontSize: 12, color: '#718096' }}>Reason: {detail.account?.dormancy_reason_label}</div>
            </div>

            {/* Offer */}
            <div style={{ background: '#f0fff4', border: '1px solid #c6f6d5', borderRadius: 8, padding: 12, marginBottom: 12 }}>
              <div style={{ fontSize: 10, color: '#276749', marginBottom: 6, fontWeight: 600, textTransform: 'uppercase' }}>REACTIVATION OFFER</div>
              <div style={{ fontSize: 13, color: '#1a202c', fontWeight: 500, marginBottom: 4 }}>{detail.account?.reactivation_offer?.offer}</div>
              <div style={{ fontSize: 12, color: '#718096' }}>Why: {detail.account?.reactivation_offer?.reason}</div>
            </div>

            {/* Advantage */}
            <div style={{ background: '#ebf8ff', border: '1px solid #bee3f8', borderRadius: 8, padding: 12, marginBottom: 12 }}>
              <div style={{ fontSize: 10, color: '#3182ce', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase' }}>PRISM ADVANTAGE</div>
              {[
                { label: 'KYC Required', value: '❌ Already done', color: '#38a169' },
                { label: 'New Consent', value: '❌ Already on file', color: '#38a169' },
                { label: 'Cost', value: '₹12 (vs ₹1,200 new)', color: '#38a169' },
                { label: 'Time to reactivate', value: '48 hours', color: '#3182ce' },
              ].map((item, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, padding: '5px 0', borderBottom: '1px solid #bee3f8' }}>
                  <span style={{ color: '#718096' }}>{item.label}</span>
                  <span style={{ color: item.color, fontWeight: 600 }}>{item.value}</span>
                </div>
              ))}
            </div>

            {/* Journey */}
            {detail.journey && (
              <div style={{ marginBottom: 16 }}>
                <div style={{ fontSize: 10, color: '#718096', textTransform: 'uppercase', letterSpacing: '0.8px', fontWeight: 600, marginBottom: 10 }}>30-DAY REACTIVATION JOURNEY</div>
                <div className="timeline">
                  {detail.journey.journey?.map((step, i) => (
                    <div key={i} className="timeline-item">
                      <div className="timeline-dot" style={{ background: step.type === 'success' ? '#38a169' : step.type === 'milestone' ? '#3182ce' : step.type === 'escalation' ? '#d97706' : '#718096' }}></div>
                      <div className="timeline-date">Day {step.day}</div>
                      <div className="timeline-event">{step.icon} {step.action}</div>
                    </div>
                  ))}
                </div>
                <div style={{ fontSize: 11, color: '#38a169', marginTop: 10, padding: '8px 10px', background: '#f0fff4', borderRadius: 6, border: '1px solid #c6f6d5' }}>
                  💡 {detail.journey.advantage}
                </div>
              </div>
            )}

            {results[selected] ? (
              <div style={{ padding: 12, background: '#f0fff4', border: '1px solid #c6f6d5', borderRadius: 8 }}>
                <div style={{ color: '#38a169', fontWeight: 600, marginBottom: 6 }}>✅ Reactivation Triggered — {results[selected].id}</div>
                <div className="message-bubble" style={{ fontSize: 12 }}>{results[selected].message}</div>
              </div>
            ) : (
              <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}
                onClick={() => reactivate(selected)} disabled={reactivating === selected}>
                {reactivating === selected ? '⏳ Triggering...' : `📨 Trigger Reactivation via ${detail.account?.preferred_channel}`}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
