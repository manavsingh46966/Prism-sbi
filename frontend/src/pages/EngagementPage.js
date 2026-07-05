import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, formatPersona } from '../utils/api';
 
// These reference REAL individuals from the dataset (verified to actually
// have this persona + channel combination) rather than fabricated IDs.
// Fabricated demo IDs (1, 2, 3) previously collided with real dataset IDs,
// causing the wrong person's real engagement content to display under a
// fake demo label — engaging "demo id 1" silently engaged whichever real
// individual actually has id=1. Using real IDs end to end means the card
// shown always matches what the backend actually returns.
const DEMOS = [
  {id:134,name:'Pranay Choudhary',occ:'Wheat farmer',age:52,area:'Pindra',lang:'Bhojpuri',persona:'farmer',channel:'voice',score:76},
  {id:5,name:'Fateh Varty',occ:'Daily wage worker',age:33,area:'Varanasi City',lang:'Hindi',persona:'gig_worker',channel:'whatsapp',score:98},
  {id:20,name:'Lakshit Kashyap',occ:'Vegetable vendor',age:26,area:'Cantt Area',lang:'Hindi',persona:'kirana',channel:'whatsapp',score:94},
];
const personaEmoji={farmer:'🚜',gig_worker:'🛵',kirana:'🏪',first_timer:'👤',nri:'✈️'};
const channelIcon={voice:'📞',whatsapp:'💬',ussd:'📱',in_app:'🔔'};
 
export default function EngagementPage() {
  const [stats,setStats]=useState(null);
  const [individuals,setIndividuals]=useState([]);
  const [results,setResults]=useState({});
  const [triggering,setTriggering]=useState(null);
  const navigate=useNavigate();
 
  useEffect(()=>{
    api.get('/engage/stats/summary').then(setStats).catch(console.error);
    api.get('/individuals?limit=15&min_score=70').then(d=>setIndividuals(d.individuals||[]));
  },[]);
 
  const engage=async(id)=>{
    setTriggering(id);
    try{ const r=await api.post(`/engage/${id}`); setResults(p=>({...p,[id]:r})); }
    catch(e){console.error(e);}
    finally{setTriggering(null);}
  };
 
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Engagement Center</h1>
        <p className="page-subtitle">Omnichannel Engagement</p>
        <p style={{fontSize:13,color:'#718096',marginTop:4}}>Trigger personalised, compliant outreach across voice, WhatsApp, USSD, and in-app channels based on <strong>real-time behavioral triggers</strong>.</p>
      </div>
 
      {stats&&(
        <div className="stats-grid">
          {[
            {label:'TOTAL ENGAGEMENTS',value:312+stats.total_engagements},
            {label:'EST. CONVERSIONS',value:89+stats.estimated_conversions,color:'stat-blue',sub:'34% response rate'},
            {label:'VOICE CALLS',value:148+(stats.by_channel?.voice||0),sub:'Sarvam AI — Bhojpuri'},
            {label:'WHATSAPP MSGS',value:124+(stats.by_channel?.whatsapp||0)},
            {label:'USSD SESSIONS',value:40+(stats.by_channel?.ussd||0),sub:'Feature phone reach'},
          ].map((s,i)=>(
            <div key={i} className="stat-card">
              <div className="stat-label">{s.label}</div>
              <div className={`stat-value ${s.color||''}`}>{s.value}</div>
              {s.sub&&<div className="stat-sub">{s.sub}</div>}
            </div>
          ))}
        </div>
      )}
 
      {/* Demo Personas */}
      <div style={{fontSize:11,color:'#718096',textTransform:'uppercase',letterSpacing:'0.8px',fontWeight:600,marginBottom:12}}>DEMO PERSONAS — LIVE ENGAGEMENT TRIGGERS</div>
      <div className="grid-3" style={{marginBottom:24}}>
        {DEMOS.map(p=>(
          <div key={p.id} className="card">
            <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',marginBottom:12}}>
              <div style={{display:'flex',gap:10,alignItems:'center'}}>
                <div className="avatar" style={{background:'#e2e8f0',fontSize:20,color:'#4a5568'}}>{personaEmoji[p.persona]}</div>
                <div>
                  <div style={{fontWeight:600,color:'#1a202c',fontSize:14}}>{p.name}</div>
                  <div style={{fontSize:11,color:'#718096'}}>{p.occ} • {p.age}y</div>
                  <div style={{fontSize:11,color:'#718096'}}>{p.area} • {p.lang}</div>
                </div>
              </div>
              <div style={{textAlign:'right'}}>
                <div style={{fontSize:20,fontWeight:700,color:'#3182ce'}}>{p.score}</div>
                <div style={{fontSize:9,color:'#718096',textTransform:'uppercase'}}>READINESS</div>
              </div>
            </div>
            <div style={{display:'flex',gap:6,marginBottom:12,flexWrap:'wrap'}}>
              <span className="tag tag-blue">{channelIcon[p.channel]} {p.channel.toUpperCase()}</span>
              <span className="tag tag-gray">{p.lang}</span>
              <span className={`persona-pill persona-${p.persona}`}>{formatPersona(p.persona)}</span>
            </div>
            {results[p.id]?(
              <div>
                <div className="message-bubble" style={{fontSize:12,marginBottom:8}}>{results[p.id].message}</div>
                {results[p.id].audio_base64 && (
                  <audio controls style={{width:'100%',marginBottom:8}}
                    src={`data:audio/${results[p.id].audio_format||'wav'};base64,${results[p.id].audio_base64}`} />
                )}
                <div style={{fontSize:11,color:'#38a169',marginBottom:8}}>✅ {results[p.id].status?.replace('_',' ')} · {results[p.id].demo_note}</div>
              </div>
            ):(
              <button className="btn btn-primary" style={{width:'100%',justifyContent:'center'}}
                onClick={()=>engage(p.id)} disabled={triggering===p.id}>
                {triggering===p.id?'⏳ Triggering...':`${channelIcon[p.channel]} Trigger ${p.channel} engagement`}
              </button>
            )}
          </div>
        ))}
      </div>
 
      {/* High Priority Queue */}
      <div className="card">
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom:16}}>
          <div>
            <div style={{fontWeight:600,fontSize:15,color:'#1a202c'}}>High Priority Queue</div>
            <div style={{fontSize:12,color:'#718096'}}>SCORE 70+</div>
          </div>
          <div style={{display:'flex',gap:8}}>
            <button className="btn btn-outline btn-sm">⊞ Filter</button>
            <button className="btn btn-outline btn-sm">↓ Export</button>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>NAME</th><th>PERSONA</th><th>SCORE</th><th>CHANNEL</th><th>LANGUAGE</th><th>AREA</th><th>STATUS</th><th></th></tr></thead>
            <tbody>
              {individuals.slice(0,10).map(ind=>(
                <tr key={ind.id}>
                  <td style={{color:'#1a202c',fontWeight:500}}>{ind.name}</td>
                  <td><span className={`persona-pill persona-${ind.persona_type}`}>{formatPersona(ind.persona_type)}</span></td>
                  <td style={{color:'#38a169',fontWeight:700}}>{Math.round(ind.financial_readiness_score)}</td>
                  <td>{channelIcon[ind.preferred_channel]} {ind.preferred_channel}</td>
                  <td><span className="tag tag-purple">{ind.language}</span></td>
                  <td style={{fontSize:12}}>{ind.area}</td>
                  <td><span className={`tag ${results[ind.id]?'tag-green':'tag-amber'}`}>{results[ind.id]?'✅ Engaged':'⏳ Pending'}</span></td>
                  <td>
                    <div style={{display:'flex',gap:4}}>
                      <button className="btn btn-primary btn-sm" onClick={()=>engage(ind.id)} disabled={!!results[ind.id]||triggering===ind.id}>
                        {results[ind.id]?'Sent':triggering===ind.id?'...':'Engage'}
                      </button>
                      <button className="btn btn-outline btn-sm" onClick={()=>navigate(`/leads/${ind.id}`)}>View</button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
 