import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';
import { Check, ShieldAlert, AlertTriangle, AlertCircle, Info } from 'lucide-react';
import api from '../api/axios';

const SeverityIcon = ({ severity }) => {
  switch (severity) {
    case 'CRITICAL': return <ShieldAlert className="w-5 h-5 text-danger" />;
    case 'HIGH': return <AlertTriangle className="w-5 h-5 text-orange-500" />;
    case 'MEDIUM': return <AlertCircle className="w-5 h-5 text-warning" />;
    case 'LOW': return <Info className="w-5 h-5 text-info" />;
    default: return <Info className="w-5 h-5 text-muted" />;
  }
};

export default function Alerts() {
  const [filter, setFilter] = useState('ALL');
  const queryClient = useQueryClient();

  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => api.get('/alerts').then(res => res.data)
  });

  const ackMutation = useMutation({
    mutationFn: (id) => api.patch(`/alerts/${id}/acknowledge`),
    onSuccess: () => {
      queryClient.invalidateQueries(['alerts']);
      queryClient.invalidateQueries(['summary']);
    }
  });

  const filteredAlerts = alerts?.filter(a => {
    if (filter === 'UNACKNOWLEDGED') return !a.acknowledged;
    if (filter === 'CRITICAL') return a.severity === 'CRITICAL';
    return true;
  }) || [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold tracking-tight">Security Alerts</h1>
        
        <div className="flex gap-2 bg-card p-1 rounded-lg border border-border">
          {['ALL', 'UNACKNOWLEDGED', 'CRITICAL'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${
                filter === f ? 'bg-primary text-text shadow-sm border border-border' : 'text-muted hover:text-text'
              }`}
            >
              {f.charAt(0) + f.slice(1).toLowerCase()}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-card border border-border rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-border/30 text-muted uppercase text-xs">
              <tr>
                <th className="px-6 py-4 font-semibold w-16">Sev</th>
                <th className="px-6 py-4 font-semibold">Alert Type & Description</th>
                <th className="px-6 py-4 font-semibold">Triggered At</th>
                <th className="px-6 py-4 font-semibold">Status</th>
                <th className="px-6 py-4 font-semibold w-24 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading ? (
                <tr><td colSpan="5" className="p-6 text-center text-muted">Loading alerts...</td></tr>
              ) : filteredAlerts.map((alert) => (
                <tr key={alert.id} className={`hover:bg-border/30 transition-colors ${!alert.acknowledged && alert.severity === 'CRITICAL' ? 'bg-danger/5' : ''}`}>
                  <td className="px-6 py-4">
                    <SeverityIcon severity={alert.severity} />
                  </td>
                  <td className="px-6 py-4">
                    <div className="font-bold">{alert.alert_type}</div>
                    <div className="text-muted text-xs mt-0.5">{alert.description}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-muted text-xs">
                    {format(new Date(alert.triggered_at), 'MMM dd, HH:mm:ss')}
                  </td>
                  <td className="px-6 py-4">
                    {alert.acknowledged ? (
                      <span className="px-2 py-1 bg-success/10 text-success border border-success/20 rounded text-xs font-semibold">Ack'd</span>
                    ) : (
                      <span className="px-2 py-1 bg-warning/10 text-warning border border-warning/20 rounded text-xs font-semibold">Open</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    {!alert.acknowledged && (
                      <button 
                        onClick={() => ackMutation.mutate(alert.id)}
                        disabled={ackMutation.isLoading}
                        className="p-2 text-muted hover:text-success hover:bg-success/10 rounded-lg transition-colors border border-transparent hover:border-success/20"
                        title="Acknowledge"
                      >
                        <Check className="w-4 h-4" />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {!isLoading && filteredAlerts.length === 0 && (
                <tr><td colSpan="5" className="p-6 text-center text-muted">No alerts found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
