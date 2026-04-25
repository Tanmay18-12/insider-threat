import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield } from 'lucide-react';
import { useAuthStore } from '../store/useAuthStore';
import api from '../api/axios';

export default function Login() {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('Admin123!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const login = useAuthStore(state => state.login);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      const res = await api.post('/auth/login', formData);
      login(res.data.access_token);
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-primary flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-card border border-border rounded-xl shadow-2xl p-8 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-danger via-warning to-info" />
        
        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-danger/10 rounded-2xl flex items-center justify-center mb-4 border border-danger/20">
            <Shield className="w-8 h-8 text-danger" />
          </div>
          <h1 className="text-2xl font-bold text-text">Insider Threat System</h1>
          <p className="text-muted text-sm mt-1">Sign in to your dashboard</p>
        </div>

        {error && (
          <div className="bg-danger/10 border border-danger/50 text-danger text-sm p-3 rounded-lg mb-6 text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-muted mb-1.5">Username</label>
            <input 
              type="text" 
              value={username}
              onChange={e => setUsername(e.target.value)}
              className="w-full bg-primary border border-border rounded-lg px-4 py-2.5 text-text focus:outline-none focus:border-info focus:ring-1 focus:ring-info transition-colors"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-muted mb-1.5">Password</label>
            <input 
              type="password" 
              value={password}
              onChange={e => setPassword(e.target.value)}
              className="w-full bg-primary border border-border rounded-lg px-4 py-2.5 text-text focus:outline-none focus:border-info focus:ring-1 focus:ring-info transition-colors"
              required
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-info hover:bg-blue-600 text-white font-medium py-2.5 rounded-lg transition-colors flex justify-center"
          >
            {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
}
