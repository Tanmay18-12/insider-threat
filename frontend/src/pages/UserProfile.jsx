import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { ShieldAlert, FileText, Clock, MapPin, CheckCircle2 } from 'lucide-react';
import { format } from 'date-fns';
import api from '../api/axios';

const RiskBadge = ({ score }) => {
  if (score === undefined || score === null) score = 0;
  let color = 'bg-success/10 text-success border-success/20';
  let label = 'Low';
  if (score > 25) { color = 'bg-warning/10 text-warning border-warning/20'; label = 'Medium'; }
  if (score > 50) { color = 'bg-orange-500/10 text-orange-500 border-orange-500/20'; label = 'High'; }
  if (score > 75) { color = 'bg-danger/10 text-danger border-danger/20'; label = 'Critical'; }
  
  return (
    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold border ${color}`}>
      {label}
    </span>
  );
};

export default function UserProfile() {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState('activity');

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ['user', id],
    queryFn: () => api.get(`/users/${id}`).then(res => res.data)
  });

  const { data: activity, isLoading: activityLoading } = useQuery({
    queryKey: ['userActivity', id],
    queryFn: () => api.get(`/users/${id}/activity`).then(res => res.data)
  });

  const { data: anomalies, isLoading: anomaliesLoading } = useQuery({
    queryKey: ['userAnomalies', id],
    queryFn: () => api.get(`/users/${id}/anomalies`).then(res => res.data)
  });

  const { data: riskHistory } = useQuery({
    queryKey: ['userRiskHistory', id],
    queryFn: () => api.get(`/users/${id}/risk-history`).then(res => res.data)
  });

  if (profileLoading) return <div className="p-6 text-center text-muted">Loading profile...</div>;
  if (!profile) return <div className="p-6 text-center text-danger">User not found.</div>;

  const { user, baseline, active_alerts } = profile;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-card border border-border rounded-xl p-6 flex flex-col md:flex-row gap-6 justify-between items-start md:items-center">
        <div className="flex items-center gap-6">
          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-info to-blue-600 flex items-center justify-center text-3xl font-bold shadow-lg border-2 border-card">
            {user.username.charAt(0).toUpperCase()}
          </div>
          <div>
            <h1 className="text-3xl font-bold">{user.username}</h1>
            <div className="flex flex-wrap gap-3 mt-2 text-sm text-muted">
              <span className="flex items-center gap-1"><FileText className="w-4 h-4" /> {user.department}</span>
              <span className="flex items-center gap-1"><CheckCircle2 className="w-4 h-4 text-success" /> {user.role}</span>
              <span className="flex items-center gap-1"><ShieldAlert className="w-4 h-4 text-danger" /> {active_alerts} Active Alerts</span>
            </div>
          </div>
        </div>
        
        <div className="bg-primary border border-border rounded-lg p-4 flex items-center gap-4 min-w-[200px]">
          <div>
            <p className="text-xs text-muted font-medium uppercase tracking-wider">Overall Risk</p>
            <div className="flex items-end gap-3 mb-2">
              <span className="text-4xl font-bold text-text">
                {profile?.user?.latest_risk_score?.toFixed(0) || '0'}
              </span>
              <RiskBadge score={profile?.user?.latest_risk_score || 0} />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Col: Risk Chart & Baseline */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-card border border-border rounded-xl p-6">
            <h3 className="font-semibold mb-4">Risk History (30 Days)</h3>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={riskHistory}>
                  <XAxis dataKey="date" hide />
                  <YAxis hide domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#161B22', borderColor: '#30363D' }}
                    labelStyle={{ color: '#8B949E' }}
                  />
                  <Line type="monotone" dataKey="avg_risk" stroke="#F85149" strokeWidth={3} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-card border border-border rounded-xl p-6">
            <h3 className="font-semibold mb-4">Baseline Profile</h3>
            {baseline ? (
              <div className="space-y-4">
                <div>
                  <p className="text-xs text-muted mb-1 flex items-center gap-1"><Clock className="w-3 h-3" /> Typical Hours</p>
                  <div className="flex flex-wrap gap-1">
                    {baseline.typical_hours?.map(h => (
                      <span key={h} className="px-2 py-1 bg-primary rounded text-xs border border-border">{h}:00</span>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-xs text-muted mb-1 flex items-center gap-1"><MapPin className="w-3 h-3" /> Common Resources</p>
                  <ul className="text-sm space-y-1">
                    {baseline.common_resources?.map((r, i) => (
                      <li key={i} className="truncate bg-primary px-2 py-1 rounded border border-border" title={r}>{r}</li>
                    ))}
                  </ul>
                </div>
                <div className="pt-2 border-t border-border">
                  <p className="text-sm flex justify-between">
                    <span className="text-muted">Avg Daily Logins</span>
                    <span className="font-medium">{baseline.avg_daily_logins?.toFixed(1)}</span>
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-sm text-muted">Baseline not computed yet.</p>
            )}
          </div>
        </div>

        {/* Right Col: Activity Log */}
        <div className="lg:col-span-2 bg-card border border-border rounded-xl overflow-hidden flex flex-col">
          <div className="p-4 border-b border-border flex gap-4">
            <button 
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${activeTab === 'activity' ? 'bg-primary text-text' : 'text-muted hover:text-text'}`}
              onClick={() => setActiveTab('activity')}
            >
              Recent Activity
            </button>
            <button 
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${activeTab === 'anomalies' ? 'bg-danger/10 text-danger' : 'text-muted hover:text-danger'}`}
              onClick={() => setActiveTab('anomalies')}
            >
              Anomalies Only
            </button>
          </div>
          
          <div className="flex-1 overflow-auto p-0">
            <table className="w-full text-left text-sm">
              <thead className="bg-border/30 text-muted uppercase text-xs sticky top-0 backdrop-blur-md">
                <tr>
                  <th className="px-6 py-3 font-semibold">Timestamp</th>
                  <th className="px-6 py-3 font-semibold">Event</th>
                  <th className="px-6 py-3 font-semibold">Resource</th>
                  <th className="px-6 py-3 font-semibold">Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {activeTab === 'activity' ? (
                  activityLoading ? (
                    <tr><td colSpan="4" className="p-6 text-center text-muted">Loading activity...</td></tr>
                  ) : activity?.length > 0 ? (
                    activity.map((log) => (
                      <tr key={log.id} className={`${log.is_anomalous ? 'bg-danger/5 hover:bg-danger/10' : 'hover:bg-border/30'} transition-colors`}>
                        <td className="px-6 py-3 whitespace-nowrap text-muted text-xs">
                          {format(new Date(log.timestamp), 'MMM dd, HH:mm:ss')}
                        </td>
                        <td className="px-6 py-3">
                          <span className="font-mono text-xs">{log.event_type}</span>
                          {log.is_anomalous && <span className="ml-2 px-1.5 py-0.5 bg-danger text-white rounded text-[10px] font-bold">ANOMALY</span>}
                        </td>
                        <td className="px-6 py-3 truncate max-w-[200px]" title={log.resource_accessed}>
                          {log.resource_accessed || '-'}
                        </td>
                        <td className="px-6 py-3">
                          {log.risk_score?.toFixed(1) || '-'}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr><td colSpan="4" className="p-6 text-center text-muted">No activity found.</td></tr>
                  )
                ) : (
                  anomaliesLoading ? (
                    <tr><td colSpan="4" className="p-6 text-center text-muted">Loading anomalies...</td></tr>
                  ) : anomalies?.length > 0 ? (
                    anomalies.map((log) => (
                      <tr key={log.id} className="bg-danger/5 hover:bg-danger/10 transition-colors">
                        <td className="px-6 py-3 whitespace-nowrap text-muted text-xs">
                          {format(new Date(log.timestamp), 'MMM dd, HH:mm:ss')}
                        </td>
                        <td className="px-6 py-3">
                          <span className="font-mono text-xs">{log.event_type}</span>
                          <span className="ml-2 px-1.5 py-0.5 bg-danger text-white rounded text-[10px] font-bold">ANOMALY</span>
                        </td>
                        <td className="px-6 py-3 truncate max-w-[200px]" title={log.resource_accessed}>
                          {log.resource_accessed || '-'}
                        </td>
                        <td className="px-6 py-3">
                          {log.risk_score?.toFixed(1) || '-'}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr><td colSpan="4" className="p-6 text-center text-muted">No anomalies found.</td></tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
