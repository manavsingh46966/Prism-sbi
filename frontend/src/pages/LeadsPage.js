import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api, formatPersona, formatChannel } from '../utils/api';
 
const avatarColors = ['#1a3a5c','#276749','#92400e','#553c9a','#9b2c2c'];
const personaEmoji={farmer:'🚜',gig_worker:'🛵',kirana:'🏪',first_timer:'👤',nri:'✈️'};
 
export default function LeadsPage() {
  const [individuals,setIndividuals]=useState([]);
  const [personaStats,setPersonaStats]=useState({});
  const [loading,setLoading]=useState(true);
  const [filters,setFilters]=useState({persona:'all',min_score:0,search:''});
  const [searchParams]=useSearchParams();
  const navigate=useNavigate();
  const pincode=searchParams.get('pincode');
 
  useEffect(()=>{
    const p=new URLSearchParams();
    if(pincode) p.set('pincode',pincode);
    if(filters.persona!=='all') p.set('persona',filters.persona);
    if(filters.min_score>0) p.set('min_score',filters.min_score);
    p.set('limit','500');
    api.get(`/individuals?${p}`).then(d=>{setIndividuals(d.individuals);setPersonaStats(d.persona_stats);}).finally(()=>setLoading(false));
  },[filters,pincode]);
 
  const filtered=individuals.filter(i=>!filters.search||i.name.toLowerCase().includes(filters.search.toLowerCase())||i.occupation.toLowerCase().includes(filters.search.toLowerCase()));
  const scoreColor=s=>s>=70?'#38a169':s>=50?'#d97706':'#e53e3e';
  const getInitials=name=>name.split(' ').map(n=>n[0]).join('').slice(0,2).toUpperCase();
 
  return (
    <div>
      <div className="page-header">
        <p style={{fontSize:13,color:'#718096'}}>Total <strong>high-readiness</strong> leads across Varanasi district</p>
        <p style={{fontSize:13,color:'#3182ce',fontWeight:500}}>{filtered.length} Active Profiles</p>
      </div>
 
      {/* Persona Cards */}
      <div style={{display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:12,marginBottom:20}}>
        {Object.entries(personaStats).map(([persona,stats],idx)=>(
          <div key={persona} className="card" style={{cursor:'pointer',border:filters.persona===persona?'1.5px solid #3182ce':'1px solid #e2e8f0',padding:'14px 16px'}}
            onClick={()=>setFilters(f=>({...f,persona:f.persona===persona?'all':persona}))}>
            <div style={{display:'flex',alignItems:'center',gap:6,marginBottom:8}}>
              <span style={{fontSize:16}}>{personaEmoji[persona]}</span>
              <span style={{fontSize:11,fontWeight:700,color:'#1a202c',textTransform:'uppercase',letterSpacing:'0.5px'}}>{persona.replace('_',' ')}</span>
              <span style={{width:7,height:7,borderRadius:'50%',background:idx===0?'#38a169':idx===1?'#d97706':idx===2?'#3182ce':idx===3?'#6b46c1':'#e53e3e',marginLeft:'auto'}}></span>
            </div>
            <div style={{fontSize:22,fontWeight:700,color:'#1a202c',marginBottom:4}}>{stats.count}</div>
            <div style={{fontSize:11,color:'#718096'}}>Avg Score: {stats.avg_score}</div>
            <div style={{fontSize:11,color:'#718096'}}>Est: ₹{stats.avg_income?.toLocaleString()}/mo</div>
          </div>
        ))}
      </div>
 
      {/* Filters */}
      <div className="filters">
        <div className="search-wrap">
          <span className="search-ico">🔍</span>
          <input className="search-input" placeholder="Search by name, occupation..." value={filters.search} onChange={e=>setFilters(f=>({...f,search:e.target.value}))} />
        </div>
        <select className="filter-select" value={filters.persona} onChange={e=>setFilters(f=>({...f,persona:e.target.value}))}>
          <option value="all">All Personas</option>
          <option value="farmer">🚜 Farmer</option>
          <option value="gig_worker">🛵 Gig Worker</option>
          <option value="kirana">🏪 Kirana Owner</option>
          <option value="first_timer">👤 First Timer</option>
          <option value="nri">✈️ NRI</option>
        </select>
        <select className="filter-select" value={filters.min_score} onChange={e=>setFilters(f=>({...f,min_score:Number(e.target.value)}))}>
          <option value={0}>All Scores</option>
          <option value={70}>High (70+)</option>
          <option value={80}>Very High (80+)</option>
        </select>
        <button className="btn btn-primary btn-sm">⊞ Apply Filters</button>
        {pincode&&<button className="btn btn-outline btn-sm" onClick={()=>navigate('/leads')}>✕ Clear pincode</button>}
      </div>
 
      {loading?<div className="loading"><div className="spinner"></div>Scoring individuals...</div>:(
        <div className="card" style={{padding:0}}>
          <div className="table-wrap">
            <table>
              <thead><tr><th>NAME</th><th>PERSONA</th><th>LOCATION</th><th>READINESS</th><th>INCOME EST.</th><th>CHANNEL</th><th>ACTIONS</th></tr></thead>
              <tbody>
                {filtered.slice(0,100).map((ind,idx)=>(
                  <tr key={ind.id} style={{cursor:'pointer'}} onClick={()=>navigate(`/leads/${ind.id}`)}>
                    <td>
                      <div style={{display:'flex',alignItems:'center',gap:10}}>
                        <div className="avatar" style={{background:avatarColors[idx%5],width:32,height:32,fontSize:11}}>{getInitials(ind.name)}</div>
                        <div>
                          <div style={{color:'#1a202c',fontWeight:500,fontSize:13}}>{ind.name}</div>
                          <div style={{fontSize:11,color:'#718096'}}>{ind.age}y • {ind.gender} • {ind.occupation?.slice(0,20)}</div>
                        </div>
                      </div>
                    </td>
                    <td><span className={`persona-pill persona-${ind.persona_type}`}>{formatPersona(ind.persona_type)}</span></td>
                    <td><div style={{fontSize:13,color:'#1a202c'}}>{ind.area}</div><div style={{fontSize:11,color:'#3182ce'}}>{ind.pincode}</div></td>
                    <td>
                      <div className="score-bar">
                        <div className="score-track"><div className="score-fill" style={{width:`${ind.financial_readiness_score}%`,background:scoreColor(ind.financial_readiness_score)}}/></div>
                        <span className="score-num" style={{color:scoreColor(ind.financial_readiness_score)}}>{Math.round(ind.financial_readiness_score)}</span>
                      </div>
                    </td>
                    <td style={{fontSize:13}}>₹{ind.income_estimate?.toLocaleString()}</td>
                    <td>
                      <span style={{fontSize:12,color:'#3182ce',display:'flex',alignItems:'center',gap:4}}>
                        {ind.preferred_channel==='whatsapp'?'💬 WhatsApp':ind.preferred_channel==='voice'?'📞 Voice Call':ind.preferred_channel==='ussd'?'📱 USSD':'🔔 In-App'}
                      </span>
                    </td>
                    <td><button className="btn btn-outline btn-sm" onClick={e=>{e.stopPropagation();navigate(`/leads/${ind.id}`);}}>Profile</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {filtered.length>100&&<div style={{padding:'12px 16px',fontSize:12,color:'#718096',textAlign:'center',borderTop:'1px solid #e2e8f0'}}>Showing top 100 of {filtered.length} leads</div>}
        </div>
      )}
    </div>
  );
}