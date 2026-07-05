import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { api } from '../utils/api';
import 'leaflet/dist/leaflet.css';

export default function HeatmapPage() {
  const [heatmap, setHeatmap] = useState([]);
  const [territories, setTerritories] = useState([]);
  const [selected, setSelected] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([api.get('/territories/heatmap'), api.get('/territories')])
      .then(([h, t]) => { setHeatmap(h.heatmap); setTerritories(t.territories); })
      .finally(() => setLoading(false));
  }, []);

  const selectTerritory = async (t) => {
    setSelected(t);
    const ins = await api.get(`/territories/${t.pincode}`);
    setInsights(ins);
  };

  const scoreColor = (s) => s >= 70 ? '#3182ce' : s >= 50 ? '#0694a2' : '#e53e3e';
  const scoreTagClass = (s) => s >= 70 ? 'tag-blue' : s >= 50 ? 'tag-gray' : 'tag-red';

  if (loading) return <div className="loading"><div className="spinner"></div>Loading territory intelligence...</div>;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Acquisition Opportunity Heatmap</h1>
        <p className="page-subtitle">Real-time opportunity scoring across Varanasi district — pincode level intelligence</p>
      </div>

      {/* Map */}
      <div className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 20 }}>
        <div style={{ padding: '10px 16px', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#f7f9fb' }}>
          <span style={{ fontSize: 12, color: '#718096' }}>Click any zone to view insights</span>
          <div style={{ display: 'flex', gap: 16, fontSize: 12 }}>
            <span style={{ color: '#3182ce' }}>● High (70+)</span>
            <span style={{ color: '#0694a2' }}>● Medium (50-70)</span>
            <span style={{ color: '#e53e3e' }}>● Low (&lt;50)</span>
          </div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: selected ? '1fr 340px' : '1fr' }}>
          <div style={{ height: 420 }}>
            <MapContainer center={[25.317, 82.974]} zoom={11} style={{ height: '100%', width: '100%' }}>
              <TileLayer url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png" attribution='&copy; CartoDB' />
              {heatmap.map(t => (
                <CircleMarker key={t.pincode} center={[t.latitude, t.longitude]}
                  radius={Math.max(16, t.unbanked_population / 900)}
                  fillColor={scoreColor(t.opportunity_score)} color={scoreColor(t.opportunity_score)}
                  weight={1.5} opacity={0.9} fillOpacity={selected?.pincode === t.pincode ? 0.85 : 0.4}
                  eventHandlers={{ click: () => selectTerritory(t) }}>
                  <Popup>
                    <div style={{ fontSize: 12, minWidth: 140 }}>
                      <div style={{ fontWeight: 700, marginBottom: 4 }}>{t.area_name}</div>
                      <div style={{ color: scoreColor(t.opportunity_score), fontSize: 18, fontWeight: 700 }}>{t.opportunity_score}/100</div>
                      <div style={{ color: '#718096', marginTop: 4 }}>Unbanked: {t.unbanked_population?.toLocaleString()}</div>
                    </div>
                  </Popup>
                </CircleMarker>
              ))}
            </MapContainer>
          </div>

          {/* Insights Panel */}
          {selected && insights && (
            <div style={{ borderLeft: '1px solid #e2e8f0', padding: 20, overflowY: 'auto', maxHeight: 420 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 14 }}>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 15, color: '#1a202c' }}>{selected.area_name}</div>
                  <div style={{ fontSize: 12, color: '#718096' }}>Pincode {selected.pincode}</div>
                </div>
                <button onClick={() => { setSelected(null); setInsights(null); }} style={{ background: 'none', border: 'none', color: '#718096', cursor: 'pointer', fontSize: 18 }}>×</button>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 14 }}>
                {[
                  { label: 'Opportunity', value: selected.opportunity_score, color: scoreColor(selected.opportunity_score) },
                  { label: 'Unbanked', value: selected.unbanked_population?.toLocaleString(), color: '#1a202c' },
                  { label: 'DBT Level', value: `${Math.round(selected.dbt_disbursement * 100)}%`, color: '#6b46c1' },
                  { label: 'Telecom', value: `${Math.round(selected.telecom_penetration * 100)}%`, color: '#3182ce' },
                ].map((s, i) => (
                  <div key={i} style={{ background: '#f7f9fb', border: '1px solid #e2e8f0', borderRadius: 8, padding: '10px 12px' }}>
                    <div style={{ fontSize: 10, color: '#718096', marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.5px' }}>{s.label}</div>
                    <div style={{ fontSize: 20, fontWeight: 700, color: s.color }}>{s.value}</div>
                  </div>
                ))}
              </div>

              {insights.ai_strategic_brief?.available && (
                <div style={{ marginBottom: 14 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <div style={{ fontSize: 10, color: '#718096', textTransform: 'uppercase', letterSpacing: '0.8px', fontWeight: 600 }}>🤖 AI Strategic Brief</div>
                    <span className="tag tag-green" style={{ fontSize: 9 }}>live agentic AI</span>
                  </div>
                  <div style={{ background: '#f5f7ff', border: '1px solid #c3dafe', borderRadius: 6, padding: '10px 12px', fontSize: 12, color: '#2d3748', lineHeight: 1.6 }}>
                    {insights.ai_strategic_brief.brief}
                  </div>
                </div>
              )}

              {insights.real_government_data?.available && (
                <div style={{ marginBottom: 14 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                    <div style={{ fontSize: 10, color: '#718096', textTransform: 'uppercase', letterSpacing: '0.8px', fontWeight: 600 }}>🏛️ Real Government Data</div>
                    <span className="tag tag-green" style={{ fontSize: 9 }}>data.gov.in — district level</span>
                  </div>
                  <div style={{ background: '#f0fff4', border: '1px solid #c6f6d5', borderRadius: 6, padding: '10px 12px', fontSize: 11, color: '#276749' }}>
                    {insights.real_government_data.agmarknet_mandi_prices?.length > 0 && (
                      <div style={{ marginBottom: 6 }}>
                        <strong>Agmarknet mandi prices ({insights.real_government_data.source_district}):</strong>
                        {insights.real_government_data.agmarknet_mandi_prices.slice(0, 2).map((p, i) => (
                          <div key={i}>{p.commodity} — ₹{p.modal_price} ({p.market}, {p.arrival_date})</div>
                        ))}
                      </div>
                    )}
                    {insights.real_government_data.pmjdy_financial_inclusion?.record_count > 0 && (
                      <div>
                        <strong>PMJDY financial inclusion ({insights.real_government_data.source_state}):</strong> {insights.real_government_data.pmjdy_financial_inclusion.record_count} district records fetched
                      </div>
                    )}
                  </div>
                </div>
              )}

              {insights.insights?.length > 0 && (
                <div style={{ marginBottom: 14 }}>
                  <div style={{ fontSize: 10, color: '#718096', textTransform: 'uppercase', letterSpacing: '0.8px', fontWeight: 600, marginBottom: 8 }}>Rule-Based Signals</div>
                  {insights.insights.map((ins, i) => (
                    <div key={i} style={{ background: '#ebf8ff', border: '1px solid #bee3f8', borderRadius: 6, padding: '8px 10px', marginBottom: 6, fontSize: 12, color: '#2c5282', lineHeight: 1.5 }}>
                      💡 {ins}
                    </div>
                  ))}
                </div>
              )}

              {insights.recommended_channels && (
                <div style={{ marginBottom: 14 }}>
                  <div style={{ fontSize: 10, color: '#718096', textTransform: 'uppercase', letterSpacing: '0.8px', fontWeight: 600, marginBottom: 8 }}>Recommended Channels</div>
                  <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                    {insights.recommended_channels.map((ch, i) => <span key={i} className="tag tag-blue">{ch}</span>)}
                  </div>
                </div>
              )}

              {insights.estimated_conversion && (
                <div style={{ background: '#f0fff4', border: '1px solid #c6f6d5', borderRadius: 8, padding: 12, marginBottom: 12 }}>
                  <div style={{ fontSize: 10, color: '#276749', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase' }}>PROJECTED IMPACT</div>
                  {[
                    { label: 'Est. leads', value: insights.estimated_conversion.estimated_leads?.toLocaleString() },
                    { label: 'Projected conversions', value: insights.estimated_conversion.projected_conversions?.toLocaleString(), color: '#38a169' },
                    { label: 'Est. CAC', value: insights.estimated_conversion.estimated_cac, color: '#38a169' },
                  ].map((item, i) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
                      <span style={{ color: '#718096' }}>{item.label}</span>
                      <span style={{ color: item.color || '#1a202c', fontWeight: 600 }}>{item.value}</span>
                    </div>
                  ))}
                </div>
              )}

              <button className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}
                onClick={() => navigate(`/leads?pincode=${selected.pincode}`)}>
                View Leads in This Zone →
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Territory Table */}
      <div style={{ fontSize: 11, color: '#718096', textTransform: 'uppercase', letterSpacing: '0.8px', fontWeight: 600, marginBottom: 12 }}>ALL TERRITORY ZONES — RANKED BY OPPORTUNITY</div>
      <div className="card" style={{ padding: 0 }}>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>ZONE</th><th>PINCODE</th><th>TYPE</th><th>OPPORTUNITY SCORE</th><th>UNBANKED POP.</th><th>DBT LEVEL</th><th>TELECOM</th><th>PRIORITY CHANNELS</th><th></th></tr>
            </thead>
            <tbody>
              {[...territories].sort((a, b) => b.opportunity_score - a.opportunity_score).map(t => (
                <tr key={t.pincode} style={{ cursor: 'pointer' }} onClick={() => selectTerritory(t)}>
                  <td style={{ color: '#1a202c', fontWeight: 500 }}>{t.area_name}</td>
                  <td style={{ color: '#3182ce', fontFamily: 'monospace', fontSize: 12 }}>{t.pincode}</td>
                  <td><span className={`tag ${t.is_rural ? 'tag-green' : 'tag-blue'}`}>{t.is_rural ? 'RURAL' : 'URBAN'}</span></td>
                  <td>
                    <div className="score-bar">
                      <div className="score-track"><div className="score-fill" style={{ width: `${t.opportunity_score}%`, background: scoreColor(t.opportunity_score) }} /></div>
                      <span className="score-num" style={{ color: scoreColor(t.opportunity_score) }}>{t.opportunity_score}</span>
                    </div>
                  </td>
                  <td style={{ fontWeight: 500 }}>{t.unbanked_population?.toLocaleString()}</td>
                  <td>{Math.round(t.dbt_disbursement * 100)}%</td>
                  <td>{Math.round(t.telecom_penetration * 100)}%</td>
                  <td>
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                      {t.is_rural && <span className="tag tag-amber">Voice</span>}
                      {t.telecom_penetration > 0.5 && <span className="tag tag-green">WhatsApp</span>}
                      {t.telecom_penetration < 0.4 && <span className="tag tag-blue">USSD</span>}
                    </div>
                  </td>
                  <td><button className="btn btn-outline btn-sm">View →</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
