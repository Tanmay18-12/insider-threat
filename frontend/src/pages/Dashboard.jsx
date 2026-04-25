import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { ShieldAlert, Users, TrendingUp, AlertTriangle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import api from '../api/axios';

export default function Dashboard() {
  const { data: summary, isLoading: sumLoading } = useQuery({
    queryKey: ['summary'],
    queryFn: () => api.get('/analytics/summary').then(res => res.data)
  });

  const { data: topThreats, isLoading: threatsLoading } = useQuery({
    queryKey: ['top-threats'],
    queryFn: () => api.get('/analytics/top-threats').then(res => res.data)
  });

  const { data: trend, isLoading: trendLoading } = useQuery({
    queryKey: ['trend'],
    queryFn: () => api.get('/analytics/trend').then(res => res.data)
  });

  const StatCard = ({ title, value, icon: Icon, color }) => (
    <div className="bg-card border border-border rounded-xl p-6 relative overflow-hidden">
      <div className={`absolute -right-4 -top-4 w-24 h-24 rounded-full opacity-10 bg-${color}`} />
      <div className="flex items-start justify-between">
        <div>
          <p className="text-muted text-sm font-medium">{title}</p>
          <h3 className="text-3xl font-bold text-text mt-2">{value ?? '-'}</h3>
        </div>
        <div className={`p-3 rounded-lg bg-${color}/10 border border-${color}/20`}>
          <Icon className={`w-6 h-6 text-${color}`} />
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold tracking-tight">Security Overview</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard title="Total Users" value={summary?.total_users} icon={Users} color="info" />
        <StatCard title="Active Alerts" value={summary?.active_alerts} icon={ShieldAlert} color="danger" />
        <StatCard title="High-Risk Users" value={summary?.high_risk_count} icon={AlertTriangle} color="warning" />
        <StatCard title="Avg Risk Score" value={summary?.avg_risk?.toFixed(1)} icon={TrendingUp} color="success" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart */}
        <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6">
          <h3 className="font-semibold mb-6">30-Day Anomaly Trend</h3>
          <div className="h-72">
            {!trendLoading && (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trend}>
                  <defs>
                    <linearGradient id="colorAnomalies" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#F85149" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#F85149" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" stroke="#8B949E" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#8B949E" fontSize={12} tickLine={false} axisLine={false} />
                  <RechartsTooltip 
                    contentStyle={{ backgroundColor: '#161B22', borderColor: '#30363D', color: '#E6EDF3' }}
                    itemStyle={{ color: '#F85149' }}
                  />
                  <Area type="monotone" dataKey="anomalies" stroke="#F85149" fillOpacity={1} fill="url(#colorAnomalies)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Top Threats */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="font-semibold mb-6">Top High-Risk Users</h3>
          <div className="space-y-4">
            {!threatsLoading && topThreats?.map((user, i) => (
              <div key={user.user_id} className="flex items-center justify-between p-3 rounded-lg hover:bg-border/50 transition-colors border border-transparent hover:border-border cursor-pointer">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-danger to-warning flex items-center justify-center text-xs font-bold shadow-lg">
                    {user.username.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-sm">{user.username}</p>
                    <p className="text-xs text-muted">Risk: {user.risk_score.toFixed(1)}</p>
                  </div>
                </div>
                <div className="w-16 h-2 bg-primary rounded-full overflow-hidden">
                  <div className="h-full bg-danger rounded-full" style={{ width: `${user.risk_score}%` }} />
                </div>
              </div>
            ))}
            {topThreats?.length === 0 && <p className="text-muted text-sm">No high-risk users detected.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
