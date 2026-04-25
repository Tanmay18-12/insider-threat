import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
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
      {label} ({score.toFixed(0)})
    </span>
  );
};

export default function Users() {
  const [dept, setDept] = useState('');
  const [search, setSearch] = useState('');
  const navigate = useNavigate();

  const { data: users, isLoading } = useQuery({
    queryKey: ['users', dept],
    queryFn: () => api.get(`/users${dept ? `?dept=${dept}` : ''}`).then(res => res.data)
  });

  const filteredUsers = users?.filter(u => u.username.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase())) || [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-2xl font-bold tracking-tight">Users Directory</h1>
        
        <div className="flex items-center gap-3 w-full sm:w-auto">
          <div className="relative flex-1 sm:w-64">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
            <input 
              type="text" 
              placeholder="Search users..." 
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full bg-card border border-border rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:border-info"
            />
          </div>
          <select 
            value={dept} 
            onChange={e => setDept(e.target.value)}
            className="bg-card border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-info"
          >
            <option value="">All Depts</option>
            <option value="Engineering">Engineering</option>
            <option value="Finance">Finance</option>
            <option value="HR">HR</option>
            <option value="Operations">Operations</option>
            <option value="Legal">Legal</option>
          </select>
        </div>
      </div>

      <div className="bg-card border border-border rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-border/30 text-muted uppercase text-xs">
              <tr>
                <th className="px-6 py-4 font-semibold">User</th>
                <th className="px-6 py-4 font-semibold">Department</th>
                <th className="px-6 py-4 font-semibold">Role</th>
                <th className="px-6 py-4 font-semibold">Status</th>
                <th className="px-6 py-4 font-semibold">Risk Score</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading ? (
                <tr><td colSpan="5" className="p-6 text-center text-muted">Loading users...</td></tr>
              ) : filteredUsers.map((user) => (
                <tr 
                  key={user.id} 
                  onClick={() => navigate(`/users/${user.id}`)}
                  className="hover:bg-border/30 cursor-pointer transition-colors"
                >
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center font-bold border border-border">
                        {user.username.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="font-medium">{user.username}</div>
                        <div className="text-xs text-muted">{user.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">{user.department}</td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-primary border border-border rounded text-xs">{user.role}</span>
                  </td>
                  <td className="px-6 py-4">
                    {user.is_active ? 
                      <span className="flex items-center gap-1.5 text-success"><span className="w-2 h-2 rounded-full bg-success"></span>Active</span> : 
                      <span className="flex items-center gap-1.5 text-muted"><span className="w-2 h-2 rounded-full bg-muted"></span>Inactive</span>
                    }
                  </td>
                  <td className="px-6 py-4">
                    <RiskBadge score={user.latest_risk_score || 0} />
                  </td>
                </tr>
              ))}
              {!isLoading && filteredUsers.length === 0 && (
                <tr><td colSpan="5" className="p-6 text-center text-muted">No users found.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
