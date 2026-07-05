import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api, formatPersona, formatChannel } from '../utils/api';

const personaEmoji = { farmer:'🚜', gig_worker:'🛵', kirana:'🏪', first_timer:'👤', nri:'✈️' };
const avatarColors = ['#1a3a5c','#276749','#92400e','#553c9a','#9b2c2c'];
const getInitials = name => name?.split(' ').map(n=>n[0]).join('').slice(0,2).toUpperCase();
const scoreColor = s => s >= 70 ? '#38a169' : s >= 50 ? '#d97706' : '#e53e3e';

export default function IndividualProfile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [engaging, setEngaging] = useState(false);
  const [engagementResult, setEngagementResult] = useState(null);
  const [activating, setActivating] = useState(false);
  const [activation, setActivation] = useState(null);

  useEffect(() => {
    setLoading(true);
    setProfile(null);
    setEngagementResult(null);
    setActivation(null);
    api.get(`/individuals/${id}`).then(setProfile).finally(() => setLoading(false));
  }, [id]);

  const triggerEngagement = async () => {
    setEngaging(true);
    try { const r = await api.post(`/engage/${id}`); setEngagementResult(r); }
    catch (e) { console.error(e); }
    finally { setEngaging(false); }
  };

  const triggerActivation = async () => {
    setActivating(true);
    try { const r = await api.post(`/activate/${id}`); setActivation(r); }
    catch (e) { console.error(e); }
    finally { setActivating(false); }
  };

  if (loading) return <div className="loading"><div className="spinner"></div>Loading profile...</div>;
  if (!profile) return <div className="loading">Profile not found</div>;

  const { individual: ind, signals, recommendations, engagement_plan, risk_factors, ai_narrative, ai_generated, agent_mode } = profile;
  const typeColor = t => ({ milestone:'#3182ce', nudge:'#d97706', suggestion:'#6b46c1', success:'#38a169' }[t] || '#718096');

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <button className="btn btn-outline btn-sm" onClick={() => navigate('/leads')}>← Back to Leads</button>
      </div>

      {/* Header Card */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
            <div className="avatar" style={{ width: 56, height: 56, fontSize: 20, background: avatarColors[parseInt(id) % 5] }}>
              {getInitials(ind.name)}
            </div>
            <div>
              <div style={{ fontSize: 20, fontWeight: 700, color: '#1a202c' }}>{ind.name}</div>
              <div style={{ fontSize: 13, color: '#718096' }}>{ind.occupation} · {ind.age}y · {ind.gender}</div>
              <div style={{ fontSize: 12, color: '#3182ce', marginTop: 2 }}>{ind.area}, Varanasi · {ind.pincode}</div>
              <div style={{ marginTop: 6 }}>
                <span className={`persona-pill persona-${ind.persona_type}`}>{personaEmoji[ind.persona_type]} {formatPersona(ind.persona_type)}</span>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
            <div style={{ textAlign: 'center', padding: '12px 20px', background: '#f7f9fb', border: '1px solid #e2e8f0', borderRadius: 10 }}>
              <div style={{ fontSize: 36, fontWeight: 700, color: scoreColor(ind.financial_readiness_score) }}>{Math.round(ind.financial_readiness_score)}</div>
              <div style={{ fontSize: 10, color: '#718096', textTransform: 'uppercase', letterSpacing: '0.5px' }}>READINESS SCORE</div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <button className="btn btn-primary" onClick={triggerEngagement} disabled={engaging}>
                {engaging ? '⏳ Triggering...' : `${formatChannel(ind.preferred_channel)} — Engage Now`}
              </button>
              <button className="btn btn-outline" onClick={triggerActivation} disabled={activating}>
                {activating ? '⏳ Setting up...' : '⚡ Create Activation Journey'}
              </button>
            </div>
          </div>
        </div>

        {/* Key Stats Row */}
        <div style={{ display: 'flex', gap: 12, marginTop: 16, flexWrap: 'wrap', paddingTop: 16, borderTop: '1px solid #e2e8f0' }}>
          {[
            { label: 'Language', value: ind.language },
            { label: 'Income Est.', value: `₹${ind.income_estimate?.toLocaleString()}/mo` },
            { label: 'Channel', value: formatChannel(ind.preferred_channel) },
            { label: 'Smartphone', value: ind.has_smartphone ? '✅ Yes' : '❌ No' },
            { label: 'UPI Active', value: ind.upi_active ? '✅ Yes' : '❌ No' },
            { label: 'DBT Recipient', value: ind.dbt_recipient ? '✅ Yes' : '❌ No' },
            { label: 'Bank Account', value: ind.has_bank_account ? '✅ Yes' : '❌ No — TARGET' },
          ].map((s, i) => (
            <div key={i} style={{ padding: '8px 14px', background: '#f7f9fb', border: '1px solid #e2e8f0', borderRadius: 8 }}>
              <div style={{ fontSize: 10, color: '#718096', marginBottom: 3, textTransform: 'uppercase', letterSpacing: '0.5px' }}>{s.label}</div>
              <div style={{ fontSize: 13, color: '#1a202c', fontWeight: 500 }}>{s.value}</div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Analyst Narrative */}
      {ai_narrative && (
        <div className="card" style={{ marginBottom: 16, border: '1px solid #c3dafe', background: '#f5f7ff' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: '#4c51bf', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              🤖 AI Analyst Read — Signal Agent (Layer 2)
            </div>
            <span className="tag tag-green" style={{ fontSize: 10 }}>live agentic AI</span>
          </div>
          <div style={{ fontSize: 13, color: '#2d3748', lineHeight: 1.5 }}>{ai_narrative}</div>
        </div>
      )}
      {ai_generated === false && (
        <div style={{ fontSize: 11, color: '#a0aec0', marginBottom: 12 }}>
          ⓘ Running in rule-based fallback mode (no GEMINI_API_KEY configured) — signals above are computed by PRISM's rule engine, not live AI.
        </div>
      )}

      {/* Engagement Result */}
      {engagementResult && (
        <div className="card" style={{ marginBottom: 16, border: '1px solid #c6f6d5', background: '#f0fff4' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
            <div style={{ fontSize: 14, fontWeight: 600, color: '#276749' }}>✅ Engagement Triggered — {engagementResult.id}</div>
            <div style={{ display: 'flex', gap: 6 }}>
              {engagementResult.ai_generated && <span className="tag tag-green" style={{ fontSize: 10 }}>🤖 live AI</span>}
              {engagementResult.voice_delivery_real && <span className="tag tag-green" style={{ fontSize: 10 }}>🔊 real audio</span>}
              {engagementResult.whatsapp_delivery_real && <span className="tag tag-green" style={{ fontSize: 10 }}>✅ real WhatsApp</span>}
              <span className="tag tag-green">{engagementResult.status?.replace('_', ' ')}</span>
            </div>
          </div>
          <div style={{ fontSize: 12, color: '#718096', marginBottom: 8 }}>
            Channel: {formatChannel(engagementResult.channel)} · Language: {engagementResult.language} · {engagementResult.demo_note}
          </div>
          <div className="message-bubble">{engagementResult.message}</div>
          {engagementResult.audio_base64 && (
            <div style={{ marginTop: 10 }}>
              <audio
                controls
                style={{ width: '100%' }}
                src={`data:audio/${engagementResult.audio_format || 'wav'};base64,${engagementResult.audio_base64}`}
              />
              <div style={{ fontSize: 11, color: '#718096', marginTop: 4 }}>
                🔊 Real synthesized audio via Sarvam AI ({engagementResult.voice_model})
              </div>
            </div>
          )}
          {engagementResult.whatsapp_message_id && (
            <div style={{ fontSize: 11, color: '#276749', marginTop: 6 }}>
              ✅ Delivered to WhatsApp — message ID: {engagementResult.whatsapp_message_id}
            </div>
          )}
          {engagementResult.agent_reasoning && (
            <div style={{ fontSize: 11, color: '#4c51bf', marginTop: 8, fontStyle: 'italic' }}>
              🤖 Agent reasoning: {engagementResult.agent_reasoning}
            </div>
          )}
          <div style={{ display: 'flex', gap: 6, marginTop: 10, flexWrap: 'wrap' }}>
            {engagementResult.compliance_checks?.map((c, i) => (
              <span key={i} className={`tag ${c.status === 'passed' ? 'tag-green' : 'tag-amber'}`} style={{ fontSize: 10 }}>
                {c.status === 'passed' ? '✓' : '!'} {c.rule}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Activation Result */}
      {activation && (
        <div className="card" style={{ marginBottom: 16, border: '1px solid #bee3f8' }}>
          <div style={{ fontSize: 14, fontWeight: 600, color: '#3182ce', marginBottom: 14 }}>⚡ 90-Day Activation Journey Created</div>
          <div className="timeline">
            {activation.timeline?.map((event, i) => (
              <div key={i} className="timeline-item">
                <div className="timeline-dot" style={{ background: typeColor(event.type) }}></div>
                <div className="timeline-date">Day {event.day} · {event.date}</div>
                <div className="timeline-event">{event.icon} {event.event}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid-2" style={{ marginBottom: 16 }}>
        {/* Signals */}
        <div className="card">
          <div className="card-title">Intelligence Signals</div>
          <div style={{ marginTop: 12 }}>
            {signals?.map((s, i) => (
              <div key={i} style={{ display: 'flex', gap: 10, padding: '10px 0', borderBottom: i < signals.length - 1 ? '1px solid #edf2f7' : 'none', alignItems: 'flex-start' }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: s.strength === 'High' ? '#38a169' : '#d97706', marginTop: 5, flexShrink: 0 }} />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, color: '#1a202c' }}>{s.signal}</div>
                  <div style={{ fontSize: 11, color: '#718096', marginTop: 2 }}>Source: {s.source}</div>
                </div>
                <span className={`tag ${s.strength === 'High' ? 'tag-green' : 'tag-amber'}`}>{s.strength}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendations */}
        <div className="card">
          <div className="card-title">Recommended Products</div>
          <div style={{ marginTop: 12 }}>
            {recommendations?.map((r, i) => (
              <div key={i} style={{ display: 'flex', gap: 12, padding: '10px 0', borderBottom: i < recommendations.length - 1 ? '1px solid #edf2f7' : 'none', alignItems: 'flex-start' }}>
                <div style={{ width: 26, height: 26, background: '#1a3a5c', borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 11, color: '#fff', fontWeight: 700, flexShrink: 0 }}>#{r.priority}</div>
                <div>
                  <div style={{ fontSize: 13, color: '#1a202c', fontWeight: 500 }}>{r.product}</div>
                  <div style={{ fontSize: 11, color: '#718096', marginTop: 2 }}>{r.reason}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid-2">
        {/* Engagement Plan */}
        <div className="card">
          <div className="card-title">Engagement Plan</div>
          {engagement_plan && (
            <div style={{ marginTop: 12 }}>
              {[
                { label: 'Primary Channel', value: formatChannel(engagement_plan.channel) },
                { label: 'Language', value: engagement_plan.language },
                { label: 'Optimal Timing', value: engagement_plan.optimal_timing },
                { label: 'Consent Method', value: engagement_plan.consent_method === 'missed_call' ? '📞 Missed Call' : '🔒 Digital Consent' },
                { label: 'BC Agent Required', value: engagement_plan.bc_dispatch_required ? '✅ Yes — dispatching' : '❌ Not needed' },
              ].map((item, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '9px 0', borderBottom: '1px solid #edf2f7', fontSize: 13 }}>
                  <span style={{ color: '#718096' }}>{item.label}</span>
                  <span style={{ color: '#1a202c', fontWeight: 500 }}>{item.value}</span>
                </div>
              ))}
              <div style={{ marginTop: 12 }}>
                <div style={{ fontSize: 10, color: '#718096', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>MESSAGE PREVIEW</div>
                <div className="message-bubble">{engagement_plan.message_preview}</div>
              </div>
            </div>
          )}
        </div>

        {/* Risk Factors */}
        <div className="card">
          <div className="card-title">Risk Factors & Compliance</div>
          <div style={{ marginTop: 12 }}>
            {risk_factors?.length > 0 ? risk_factors.map((r, i) => (
              <div key={i} style={{ display: 'flex', gap: 8, padding: '8px 10px', background: '#fffbeb', border: '1px solid #fde68a', borderRadius: 8, marginBottom: 8, fontSize: 12, color: '#92400e' }}>
                ⚠️ {r}
              </div>
            )) : (
              <div style={{ fontSize: 13, color: '#38a169', padding: '8px 0' }}>✅ No significant risk factors identified</div>
            )}
            <div style={{ marginTop: 12, padding: 12, background: '#ebf8ff', borderRadius: 8, border: '1px solid #bee3f8' }}>
              <div style={{ fontSize: 10, color: '#3182ce', marginBottom: 8, fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.5px' }}>COMPLIANCE STATUS</div>
              <div style={{ fontSize: 12, color: '#276749' }}>✓ DPDP consent required before engagement</div>
              <div style={{ fontSize: 12, color: '#276749', marginTop: 4 }}>✓ RBI fair practice code applies</div>
              <div style={{ fontSize: 12, color: '#276749', marginTop: 4 }}>✓ Data stored India-only (DPDP Act §16)</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
