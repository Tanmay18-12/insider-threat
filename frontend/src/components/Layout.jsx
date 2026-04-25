import React, { useState, useEffect } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Shield, Users, AlertTriangle, BarChart2, Bell, LogOut, Menu, Sun, Moon, User as UserIcon } from 'lucide-react';
import { useAuthStore, useAlertStore } from '../store/useAuthStore';
import { useWebSocket } from '../hooks/useWebSocket';

export default function Layout() {
  const location = useLocation();
  const logout = useAuthStore(state => state.logout);
  const { alerts, unreadCount, clearUnread } = useAlertStore();
  const [showToast, setShowToast] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  const [isDarkTheme, setIsDarkTheme] = useState(!document.documentElement.classList.contains('light-theme'));
  
  useWebSocket('ws://localhost:8000/ws/alerts');

  // Show toast when new alert comes
  useEffect(() => {
    if (alerts.length > 0) {
      setShowToast(true);
      const timer = setTimeout(() => setShowToast(false), 6000);
      return () => clearTimeout(timer);
    }
  }, [alerts]);

  const toggleTheme = () => {
    if (isDarkTheme) {
      document.documentElement.classList.add('light-theme');
      setIsDarkTheme(false);
    } else {
      document.documentElement.classList.remove('light-theme');
      setIsDarkTheme(true);
    }
  };

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: Shield },
    { name: 'Users', path: '/users', icon: Users },
    { name: 'Alerts', path: '/alerts', icon: AlertTriangle },
    { name: 'Analytics', path: '/analytics', icon: BarChart2 },
  ];

  return (
    <div className="flex h-screen bg-primary text-text overflow-hidden transition-colors duration-200">
      {/* Sidebar */}
      <div className="w-64 bg-card border-r border-border flex flex-col hidden md:flex transition-colors duration-200">
        <div className="p-4 flex items-center gap-2 border-b border-border">
          <Shield className="w-8 h-8 text-danger" />
          <span className="font-bold text-lg tracking-wider">THREAT<span className="text-muted">DEFEND</span></span>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => {
            const isActive = location.pathname.startsWith(item.path);
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  isActive ? 'bg-border text-info' : 'hover:bg-border/50 text-muted hover:text-text'
                }`}
              >
                <Icon className="w-5 h-5" />
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6 transition-colors duration-200">
          <div className="md:hidden">
             <Menu className="w-6 h-6 text-muted" />
          </div>
          <div className="hidden md:block"></div>
          
          <div className="flex items-center gap-4 relative">
            <Link to="/alerts" className="relative p-2 rounded-full hover:bg-border transition-colors" onClick={clearUnread}>
              <Bell className="w-5 h-5 text-muted" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-danger rounded-full ring-2 ring-card animate-pulse" />
              )}
            </Link>
            
            <button 
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              className="w-8 h-8 rounded-full bg-gradient-to-br from-info to-blue-600 border border-border focus:outline-none focus:ring-2 focus:ring-info focus:ring-offset-2 focus:ring-offset-card flex items-center justify-center text-white font-bold text-sm shadow-sm"
            >
              A
            </button>

            {/* Profile Dropdown */}
            {showProfileMenu && (
              <div className="absolute right-0 top-12 w-48 bg-card border border-border rounded-lg shadow-xl py-1 z-50">
                <div className="px-4 py-2 border-b border-border">
                  <p className="text-sm font-medium">admin</p>
                  <p className="text-xs text-muted">admin@company.com</p>
                </div>
                
                <button 
                  onClick={toggleTheme}
                  className="w-full text-left px-4 py-2 text-sm hover:bg-border/50 flex items-center gap-2 transition-colors"
                >
                  {isDarkTheme ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                  {isDarkTheme ? 'Light Mode' : 'Dark Mode'}
                </button>
                
                <button 
                  onClick={logout}
                  className="w-full text-left px-4 py-2 text-sm text-danger hover:bg-danger/10 flex items-center gap-2 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </button>
              </div>
            )}
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6 relative">
          <Outlet />

          {/* Alert Toast Stack */}
          {showToast && alerts[0] && (
            <div className="fixed top-20 right-6 z-50 animate-in slide-in-from-right fade-in duration-300">
              <div className="bg-card border-l-4 border-danger shadow-lg shadow-black/50 p-4 pr-12 rounded flex items-start gap-3 w-80">
                <AlertTriangle className="w-5 h-5 text-danger shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-sm">New High-Risk Alert</h4>
                  <p className="text-xs text-muted mt-1">{alerts[0].description || "Suspicious activity detected"}</p>
                </div>
                <button onClick={() => setShowToast(false)} className="absolute top-4 right-4 text-muted hover:text-text">&times;</button>
              </div>
            </div>
          )}
        </main>
      </div>
      
      {/* Click outside listener to close menu could be added here, but omitted for simplicity */}
      {showProfileMenu && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setShowProfileMenu(false)}
        />
      )}
    </div>
  );
}
