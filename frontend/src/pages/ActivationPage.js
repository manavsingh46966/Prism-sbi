import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, formatPersona } from '../utils/api';
 
// Same fix as EngagementPage.js: these reference REAL individuals from the
// dataset (verified persona match) instead of fabricated IDs 1,2,3,8 that
// collided with real dataset records — id=8 for example is actually a
// real NRI individual, not "Sunita Devi." Day/status/churn/products below
// remain illustrative journey-stage labels (no real "day in journey" field
// exists in the dataset), but the id/name/persona/language now correctly
// match one real, consistent individual end to end.
const DEMO = [
  { id:146, name:'Himmat Kar', persona:'farmer', lang:'Bhojpuri', day:7, status:'active', churn:'Low', products:['SAVINGS ACCOUNT','UPI','LOW CHURN RISK'] },
  { id:5, name:'Fateh Varty', persona:'gig_worker', lang:'Hindi', day:14, status:'active', churn:'Low', products:['SAVINGS ACCOUNT','UPI','RD','LOW CHURN RISK'] },
  { id:20, name:'Lakshit Kashyap', persona:'kirana', lang:'Hindi', day:30, status:'active', churn:'Low', products:['CURRENT ACCOUNT','MERCHANT UPI','LOW CHURN RISK'] },
  { id:47, name:'Rohan Rajan', persona:'first_timer', lang:'Hindi', day:5, status:'at_risk', churn:'High', products:['SAVINGS ACCOUNT','HIGH CHURN RISK'] },
];
 
const personaEmoji = {farmer:'🚜',gig_worker:'🛵',kirana:'🏪',first_timer:'👤',nri:'✈️'};
 
export default function ActivationPage() {
  const [selected, setSelected] = useState(null);
  const [activation, setActivation] = useState(null);
  const navigate = useNavigate();
 
  const load = async (id) => {
    setSelected(id);
    try {
      const r = await api.get(`/activate/${id}`);
      setActivation(r);
    } catch { const r = await api.post(`/activate/${id}`); setActivation(r); }
  };
 
  const typeColor = t => ({milestone:'#3182ce',nudge:'#d97706',suggestion:'#6b46c1',success:'#38a169'}[t]||'#718096');
 
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Activation Tracker</h1>
        <p className="page-subtitle">90-day <strong>intelligent</strong> activation journeys — ensuring every new customer becomes an active product user</p>
      </div>
 
      <div className="stats-grid">
        {[
          {label:'TOTAL ACTIVATED',value:'89',sub:'Accounts opened'},
          {label:'ACTIVE CUSTOMERS',value:'67',color:'stat-blue',sub:'75% activation rate'},
          {label:'AT RISK',value:'14',color:'stat-red',sub:'Intervention needed',danger:true},
          {label:'AVG DAYS TO 1ST TXN',value:'4.2',sub:'Days post account open'},
          {label:'AVG PRODUCTS / CUSTOMER',value:'1.8',sub:'Cross-sell success'},
          {label:'NUDGES SENT',value:'312',sub:'Personalised messages'},
        ].map((s,i)=>(
          <div key={i} className={`stat-card${s.danger?' danger':''}`}>
            <div className="stat-label">{s.label}</div>
            <div className={`stat-value ${s.color||''}`}>{s.value}</div>
            <div className="stat-sub">{s.sub}</div>
          </div>
        ))}
      </div>
 
      <div style={{marginBottom:16,fontSize:11,color:'#718096',textTransform:'uppercase',letterSpacing:'0.8px',fontWeight:600}}>ACTIVE JOURNEYS</div>
 
      <div style={{display:'grid',gridTemplateColumns:selected?'1fr 400px':'1fr',gap:16}}>
        <div>
          {DEMO.map(a=>(
            <div key={a.id} className={`journey-card${selected===a.id?' selected':''}`} onClick={()=>load(a.id)}>
              <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:8}}>
                <div>
                  <div style={{fontSize:16,fontWeight:600,color:'#1a202c'}}>{a.name}</div>
                  <div style={{fontSize:12,color:'#718096'}}>{personaEmoji[a.persona]} {formatPersona(a.persona)} • {a.lang}</div>
                </div>
                <span className={`tag ${a.status==='active'?'tag-green':'tag-red'}`}>
                  <span className="active-dot" style={{background:a.status==='active'?'#38a169':'#e53e3e'}}></span>
                  {a.status==='active'?'ACTIVE':'AT RISK'}
                </span>
              </div>
              <div style={{fontSize:12,color:'#718096',marginBottom:6}}>Day {a.day} of 90 <span style={{float:'right'}}>{Math.round(a.day/90*100)}%</span></div>
              <div className="journey-progress-bar"><div className="journey-progress-fill" style={{width:`${a.day/90*100}%`,background:a.status==='active'?'#1a3a5c':'#e53e3e'}}/></div>
              <div style={{display:'flex',gap:6,flexWrap:'wrap',marginTop:8}}>
                {a.products.map((p,i)=><span key={i} className="tag tag-gray" style={{fontSize:10}}>{p}</span>)}
              </div>
            </div>
          ))}
          <button className="btn btn-outline" style={{width:'100%',justifyContent:'center',marginTop:4}} onClick={()=>navigate('/leads')}>+ Add Customer to Journey</button>
        </div>
 
        {selected && activation && (
          <div className="card">
            <div style={{marginBottom:16}}>
              <div style={{fontSize:16,fontWeight:700,color:'#1a202c'}}>{activation.individual_name}</div>
              <div style={{fontSize:12,color:'#718096'}}>Day {activation.current_day} · Activation Score: <strong style={{color:'#38a169'}}>{activation.activation_score}</strong></div>
            </div>
            {activation.next_nudge && (
              <div style={{background:'#ebf8ff',border:'1px solid #bee3f8',borderRadius:8,padding:14,marginBottom:16}}>
                <div style={{fontSize:10,color:'#3182ce',marginBottom:6,fontWeight:600,textTransform:'uppercase',letterSpacing:'0.5px'}}>NEXT AUTOMATED NUDGE</div>
                <div style={{fontSize:13,color:'#1a202c',marginBottom:6}}>{activation.next_nudge.message}</div>
                <div style={{display:'flex',gap:6}}>
                  <span className="tag tag-blue">{activation.next_nudge.channel}</span>
                  <span className="tag tag-amber">🕐 {activation.next_nudge.timing}</span>
                </div>
              </div>
            )}
            <div style={{fontSize:11,color:'#718096',textTransform:'uppercase',letterSpacing:'0.8px',fontWeight:600,marginBottom:12}}>JOURNEY TIMELINE</div>
            <div className="timeline">
              {activation.timeline?.map((event,i)=>(
                <div key={i} className="timeline-item">
                  <div className="timeline-dot" style={{background:typeColor(event.type)}}></div>
                  <div className="timeline-date">Day {event.day} · {event.date}</div>
                  <div className="timeline-event">{event.icon} {event.event}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
 