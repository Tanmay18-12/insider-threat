import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, AreaChart, Area } from 'recharts';
import api from '../api/axios';

export default function Analytics() {
  const { data: deptRisk, isLoading: deptLoading } = useQuery({
    queryKey: ['dept-risk'],
    queryFn: () => api.get('/analytics/department').then(res => res.data)
  });

  const { data: heatmap, isLoading: heatmapLoading } = useQuery({
    queryKey: ['heatmap'],
    queryFn: () => api.get('/analytics/risk-heatmap').then(res => res.data)
  });

  const { data: trend, isLoading: trendLoading } = useQuery({
    queryKey: ['trend'],
    queryFn: () => api.get('/analytics/trend').then(res => res.data)
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold tracking-tight">Analytics Center</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Dept Breakdown */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="font-semibold mb-6">Department Risk Score (Last 24h)</h3>
          <div className="h-72">
            {!deptLoading && (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={deptRisk} layout="vertical" margin={{ top: 0, right: 30, left: 20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#30363D" />
                  <XAxis type="number" stroke="#8B949E" fontSize={12} domain={[0, 'dataMax + 10']} />
                  <YAxis dataKey="department" type="category" stroke="#8B949E" fontSize={12} width={80} />
                  <Tooltip 
                    cursor={{fill: '#30363D', opacity: 0.4}}
                    contentStyle={{ backgroundColor: '#161B22', borderColor: '#30363D' }}
                  />
                  <Bar dataKey="avg_risk" fill="#58A6FF" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* 30 Day Trend Area */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="font-semibold mb-6">30-Day Total Anomalies</h3>
          <div className="h-72">
            {!trendLoading && (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={trend}>
                  <defs>
                    <linearGradient id="colorTrend" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#D29922" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#D29922" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#30363D" />
                  <XAxis dataKey="date" stroke="#8B949E" fontSize={12} />
                  <YAxis stroke="#8B949E" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#161B22', borderColor: '#30363D' }}
                  />
                  <Area type="monotone" dataKey="anomalies" stroke="#D29922" fillOpacity={1} fill="url(#colorTrend)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Risk Heatmap (simplified rendering since real matrix needs d3 or heavy css) */}
        <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6">
          <h3 className="font-semibold mb-6">User Risk Heatmap (Last 24h)</h3>
          {!heatmapLoading && (
            <div className="overflow-x-auto pb-4">
              <div className="min-w-[800px]">
                <div className="grid grid-cols-25 gap-1 mb-1">
                  <div className="col-span-1"></div>
                  {Array.from({length: 24}).map((_, i) => (
                    <div key={i} className="text-center text-[10px] text-muted">{i}h</div>
                  ))}
                </div>
                {/* Just taking top 10 for display to avoid huge DOM */}
                {Object.entries(heatmap?.reduce((acc, curr) => {
                  if(!acc[curr.user_id]) acc[curr.user_id] = Array(24).fill(0);
                  acc[curr.user_id][curr.hour] = curr.avg_risk;
                  return acc;
                }, {}) || {}).slice(0, 10).map(([uid, hours]) => (
                  <div key={uid} className="grid grid-cols-25 gap-1 mb-1 items-center">
                    <div className="col-span-1 text-xs text-muted truncate pr-2" title={uid}>
                      User {uid.substring(0,4)}
                    </div>
                    {hours.map((val, i) => {
                      let opacity = Math.min(val / 100, 1);
                      if(opacity === 0) opacity = 0.05;
                      return (
                        <div 
                          key={i} 
                          className="h-6 rounded-sm border border-transparent hover:border-border cursor-crosshair transition-colors"
                          style={{ backgroundColor: `rgba(248, 81, 73, ${opacity})` }}
                          title={`Risk: ${val.toFixed(1)} at ${i}:00`}
                        />
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
