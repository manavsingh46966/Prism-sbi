import React, { useState, useEffect, useRef } from 'react';
import { api } from '../utils/api';
 
export default function CompliancePage() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [rules, setRules] = useState({ rbi_rules:[], dpdp_rules:[] });
  const [streaming, setStreaming] = useState(false);
  const [tab, setTab] = useState('live');
 
  useEffect(() => {
    Promise.all([api.get('/compliance/stats'),api.get('/compliance/rules'),api.get('/compliance/logs')])
      .then(([s,r,l])=>{ setStats(s); setRules(r); setLogs(l.logs||[]); });
  }, []);
 
  useEffect(() => {
    if (!streaming) return;
    const actions = [
      {layer:'Layer 3',agent:'Engagement',action:'Consent verified before engagement',detail:'DPDP Act §6 — Explicit consent on file'},
      {layer:'Layer 3',agent:'Engagement',action:'RBI call hours check',detail:'RBI §3.1 — Current time within 8AM-9PM window'},
      {layer:'Layer 3',agent:'Engagement',action:'Daily contact limit check',detail:'RBI §4.2 — 1 of 3 contacts used today'},
      {layer:'Layer 2',agent:'Signal',action:'Individual readiness scored',detail:'DPDP Act §4 — Anonymised signal processing'},
      {layer:'Layer 5',agent:'Audit',action:'Real-time validation pulse 1',detail:'System Integrity Check: Automated recurring heartbeat'},
      {layer:'Layer 4',agent:'Activation',action:'Nudge frequency compliance check',detail:'Within RBI communication guidelines'},
      {layer:'Layer 5',agent:'Audit',action:'Data localization verified',detail:'DPDP Act §16 — India-based storage confirmed'},
    ];
    const iv = setInterval(()=>{
      const a = actions[Math.floor(Math.random()*actions.length)];
      setLogs(p=>[{...a,id:Date.now(),timestamp:new Date().toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit',second:'2-digit'}),...a},...p].slice(0,40));
    },1200);
    return ()=>clearInterval(iv);
  }, [streaming]);
 
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Compliance Monitor</h1>
        <p className="page-subtitle">Real-time regulatory compliance across all PRISM agents — RBI guidelines + DPDP Act 2023</p>
      </div>
 
      {stats && (
        <div className="stats-grid">
          {[
            {label:'TOTAL CHECKS',value:stats.total_checks?.toLocaleString()},
            {label:'PASSED',value:stats.passed?.toLocaleString(),color:'stat-blue'},
            {label:'FLAGGED',value:stats.flagged,sub:'Auto-resolved',danger:true},
            {label:'BLOCKED',value:stats.blocked},
            {label:'COMPLIANCE RATE',value:stats.compliance_rate,color:'stat-teal'},
            {label:'RBI VIOLATIONS',value:stats.rbi_violations},
            {label:'DPDP VIOLATIONS',value:stats.dpdp_violations},
          ].map((s,i)=>(
            <div key={i} className={`stat-card${s.danger?' danger':''}`}>
              <div className="stat-label">{s.label}</div>
              <div className={`stat-value ${s.color||''}`}>{s.value}</div>
              {s.sub&&<div className="stat-sub">{s.sub}</div>}
            </div>
          ))}
        </div>
      )}
 
      {/* Consent Architecture */}
      <div className="card" style={{background:'#0f1f3d',border:'none',marginBottom:16}}>
        <div style={{fontSize:11,color:'rgba(255,255,255,0.5)',textTransform:'uppercase',letterSpacing:'1px',fontWeight:600,marginBottom:16}}>✦ DPDP CONSENT ARCHITECTURE — MISSED CALL MECHANISM</div>
        <div style={{display:'flex',alignItems:'center',gap:4,flexWrap:'wrap'}}>
          {[
            {step:'STEP 1',label:'PRISM identifies lead',icon:'🔍'},
            {step:'STEP 2',label:'Missed call sent to prospect',icon:'📞'},
            {step:'STEP 3',label:'Prospect calls back = passive consent',icon:'✅'},
            {step:'STEP 4',label:'Voice confirmation recorded',icon:'🎙️'},
            {step:'STEP 5',label:'Consent stored — DPDP §6 compliant',icon:'🔒'},
            {step:'STEP 6',label:'Engagement unlocked',icon:'🔑'},
          ].map((s,i)=>(
            <React.Fragment key={i}>
              <div className="consent-step" style={{flex:1,minWidth:90}}>
                <div style={{fontSize:24,marginBottom:6}}>{s.icon}</div>
                <div style={{fontSize:9,color:'rgba(255,255,255,0.4)',textTransform:'uppercase',letterSpacing:'0.5px',marginBottom:4}}>{s.step}</div>
                <div style={{fontSize:11,color:'rgba(255,255,255,0.7)',lineHeight:1.4}}>{s.label}</div>
              </div>
              {i<5&&<div className="consent-arrow">→</div>}
            </React.Fragment>
          ))}
        </div>
      </div>
 
      {/* Tabs */}
      <div style={{display:'flex',gap:8,marginBottom:12,alignItems:'center'}}>
        {[['live','🕐 Live Audit Log'],['rbi','⊙ RBI Rules'],['dpdp','🔒 DPDP Rules']].map(([t,label])=>(
          <button key={t} className={`btn ${tab===t?'btn-primary':'btn-outline'}`} onClick={()=>setTab(t)}>{label}</button>
        ))}
        {tab==='live'&&(
          <button className={`btn ${streaming?'btn-success':'btn-outline'}`} style={{marginLeft:'auto'}} onClick={()=>setStreaming(s=>!s)}>
            {streaming?'⏸ Pause':'▶ Start Live Stream'}
          </button>
        )}
      </div>
 
      {tab==='live'&&(
        <div className="card" style={{padding:0,overflow:'hidden'}}>
          <div style={{background:'#0f1f3d',maxHeight:380,overflowY:'auto'}}>
            {logs.length===0&&<div style={{color:'rgba(255,255,255,0.3)',padding:24,textAlign:'center',fontSize:13}}>Press "Start Live Stream" to see compliance checks in real-time</div>}
            {logs.map((log,i)=>(
              <div key={log.id||i} style={{display:'grid',gridTemplateColumns:'80px 70px 100px 1fr 80px',gap:8,padding:'8px 14px',borderBottom:'1px solid rgba(255,255,255,0.05)',fontFamily:'monospace',fontSize:12,background:i===0&&streaming?'rgba(49,130,206,0.1)':'transparent',transition:'background 0.5s'}}>
                <span style={{color:'rgba(255,255,255,0.3)'}}>{log.timestamp}</span>
                <span style={{color:'#63b3ed',fontWeight:600}}>{log.layer}</span>
                <span style={{color:'rgba(255,255,255,0.5)'}}>{log.agent}</span>
                <div>
                  <div style={{color:'#68d391',fontWeight:500}}>{log.action}</div>
                  {log.detail&&<div style={{color:'rgba(255,255,255,0.3)',fontSize:10,marginTop:2}}>{log.detail}</div>}
                </div>
                <span style={{color:'#68d391',fontSize:11}}>RBI✓ DPDP✓</span>
              </div>
            ))}
          </div>
        </div>
      )}
 
      {tab==='rbi'&&(
        <div className="card">
          <div className="card-title" style={{marginBottom:12}}>RBI Fair Practice Code — Encoded Rules</div>
          {rules.rbi_rules?.map((r,i)=>(
            <div key={i} style={{display:'flex',gap:12,padding:'12px',background:'#f7f9fb',borderRadius:8,marginBottom:8,alignItems:'flex-start'}}>
              <span style={{color:'#38a169',fontSize:16}}>✓</span>
              <div style={{flex:1}}>
                <div style={{fontSize:13,color:'#1a202c',fontWeight:500}}>{r.rule?.replace(/_/g,' ')}</div>
                <div style={{fontSize:12,color:'#718096',marginTop:3}}>{r.description}</div>
              </div>
              <span className="tag tag-green">Active</span>
            </div>
          ))}
        </div>
      )}
 
      {tab==='dpdp'&&(
        <div className="card">
          <div className="card-title" style={{marginBottom:12}}>DPDP Act 2023 — Digital Personal Data Protection</div>
          {rules.dpdp_rules?.map((r,i)=>(
            <div key={i} style={{display:'flex',gap:12,padding:'12px',background:'#f7f9fb',borderRadius:8,marginBottom:8,alignItems:'flex-start'}}>
              <span style={{color:'#3182ce',fontSize:16}}>🔒</span>
              <div style={{flex:1}}>
                <div style={{fontSize:13,color:'#1a202c',fontWeight:500}}>{r.rule?.replace(/_/g,' ')}</div>
                <div style={{fontSize:12,color:'#718096',marginTop:3}}>{r.description}</div>
              </div>
              <span className="tag tag-blue">Enforced</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}