import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';
 
export default function Dashboard() {
  const [data, setData] = useState(null);
  const navigate = useNavigate();
 
  useEffect(() => { api.get('/dashboard').then(setData).catch(console.error); }, []);
 
  if (!data) return <div className="loading"><div className="spinner"></div>Loading PRISM...</div>;
  const { territory_stats, persona_stats, impact, compliance_stats } = data;
 
  const personaEmoji = { farmer:'🚜', gig_worker:'🛵', kirana:'🏪', first_timer:'👤', nri:'✈️' };
  const personaLabel = { farmer:'Farmer', gig_worker:'Gig', kirana:'Kirana', first_timer:'First Timer', nri:'NRI' };
  const personaColor = { farmer:'#38a169', gig_worker:'#d97706', kirana:'#3182ce', first_timer:'#6b46c1', nri:'#e53e3e' };
 
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Command Center</h1>
        <p className="page-subtitle">Varanasi District, Uttar Pradesh — <strong>Real-time acquisition intelligence</strong></p>
      </div>
 
      {/* Impact Banner */}
      <div className="impact-banner">
        <div className="impact-label">⚡ LIVE BUSINESS IMPACT</div>
        <div className="impact-grid">
          {[
            { label: 'Unbanked Identified', value: '1,87,432', color: '' },
            { label: 'Leads Generated', value: impact.new_leads_generated, color: 'impact-green' },
            { label: 'Accounts Opened', value: impact.accounts_opened, color: 'impact-green' },
            { label: 'Acquisition Cost', value: impact.new_acquisition_cac, sub: `vs ${impact.traditional_cac} trad`, color: '' },
            { label: 'Cost Saved', value: impact.total_cost_saved || '--', color: '' },
            { label: 'Compliance Rate', value: impact.compliance_rate, color: 'impact-green' },
          ].map((item, i) => (
            <div key={i}>
              <div className="impact-item-label">{item.label}</div>
              <div className={`impact-item-value ${item.color}`}>{item.value}</div>
              {item.sub && <div className="impact-item-sub">{item.sub}</div>}
            </div>
          ))}
        </div>
      </div>
 
      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Territory Zones</div>
          <div className="stat-value">{territory_stats.total_territories}</div>
          <div className="stat-sub" style={{color:'#e53e3e'}}>{territory_stats.high_priority_zones} high priority</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Unbanked</div>
          <div className="stat-value">{territory_stats.total_unbanked?.toLocaleString()}</div>
          <div className="stat-sub">Varanasi district</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Opportunity Score</div>
          <div className="stat-value stat-teal">{territory_stats.avg_opportunity_score}</div>
          <div className="stat-sub">Out of 100</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">RBI Violations</div>
          <div className="stat-value stat-red">0</div>
          <div className="stat-sub" style={{color:'#38a169'}}>Full compliance maintained</div>
        </div>
      </div>
 
      <div className="grid-2" style={{marginBottom:16}}>
        {/* Persona */}
        <div className="card">
          <div className="card-title">Lead Intelligence by Persona</div>
          <div style={{marginTop:12}}>
            {Object.entries(persona_stats).map(([persona, stats]) => (
              <div key={persona} style={{display:'flex',alignItems:'center',gap:12,marginBottom:14}}>
                <div style={{width:100,fontSize:13,color:'#4a5568',display:'flex',alignItems:'center',gap:6}}>
                  <span>{personaEmoji[persona]}</span>{personaLabel[persona]}
                </div>
                <div style={{flex:1}}>
                  <div style={{height:6,background:'#edf2f7',borderRadius:3,overflow:'hidden'}}>
                    <div style={{height:'100%',width:`${(stats.count/500)*100}%`,background:personaColor[persona],borderRadius:3}}/>
                  </div>
                </div>
                <div style={{fontSize:12,color:'#1a202c',fontWeight:600,minWidth:24}}>{stats.count}</div>
                <div style={{fontSize:11,color:'#718096',minWidth:60}}>avg {stats.avg_score}</div>
              </div>
            ))}
          </div>
        </div>
 
        {/* Agent Status */}
        <div className="card">
          <div className="card-title">PRISM Agent Status</div>
          <div style={{marginTop:12}}>
            {[
              {badge:'L1',name:'Territory Intelligence',detail:'12 zones analyzed'},
              {badge:'L2',name:'Individual Signal Agent',detail:'500 leads scored'},
              {badge:'L3',name:'Engagement Agent',detail:'Voice + WhatsApp + USSD'},
              {badge:'L4',name:'Activation Agent',detail:'90-day journeys running'},
              {badge:'L5',name:'Compliance Orchestrator',detail:'99.3% clearance rate'},
            ].map((item,i) => (
              <div key={i} style={{display:'flex',alignItems:'center',gap:12,padding:'10px 0',borderBottom:i<4?'1px solid #edf2f7':'none'}}>
                <div style={{width:28,height:28,background:'#1a3a5c',borderRadius:6,display:'flex',alignItems:'center',justifyContent:'center',fontSize:9,color:'#fff',fontWeight:700}}>{item.badge}</div>
                <div style={{flex:1}}>
                  <div style={{fontSize:13,color:'#1a202c',fontWeight:500}}>{item.name}</div>
                  <div style={{fontSize:11,color:'#718096'}}>{item.detail}</div>
                </div>
                <span className="tag tag-green"><span className="active-dot"></span>Active</span>
              </div>
            ))}
          </div>
        </div>
      </div>
 
      {/* Quick Actions */}
      <div className="card">
        <div className="card-title" style={{marginBottom:12}}>Quick Actions</div>
        <div style={{display:'flex',gap:10,flexWrap:'wrap'}}>
          <button className="btn btn-primary" onClick={()=>navigate('/heatmap')}>⊡ View Territory Heatmap</button>
          <button className="btn btn-outline" onClick={()=>navigate('/leads')}>⊛ Browse Leads</button>
          <button className="btn btn-outline" onClick={()=>navigate('/engagement')}>⊕ Engagement Center</button>
          <button className="btn btn-outline" onClick={()=>navigate('/compliance')}>⊙ Compliance Monitor</button>
        </div>
      </div>
    </div>
  );
}
 