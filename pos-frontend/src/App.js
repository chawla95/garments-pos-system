import React, { useState, useEffect } from 'react';
import Dealers from './pages/Dealers';
import Brands from './pages/Brands';
import Products from './pages/Products';
import Inventory from './pages/Inventory';
import Checkout from './pages/Checkout';
import Dashboard from './pages/Dashboard';
import Returns from './pages/Returns';
import Login from './pages/Login';
import MLDashboard from './pages/MLDashboard';
import CashRegister from './pages/CashRegister';
import LoyaltySystem from './pages/LoyaltySystem';
import CRM from './pages/CRM';
import WhatsAppManager from './pages/WhatsAppManager';
import RBACManager from './pages/RBACManager';
import ConfigManager from './pages/ConfigManager';
import api from './api';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (token && savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        // Token is now handled by the API interceptor
      } catch (error) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    // Token cleanup is handled by the API interceptor
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '50px' }}>Loading...</div>;
  }

  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  const renderPage = () => {
    // Check if user has access to the current page
    const hasAccess = () => {
      switch (currentPage) {
        case 'dashboard':
          return user.role === 'admin';
        case 'dealers':
        case 'brands':
        case 'products':
          return user.role === 'admin';
        case 'inventory':
          return user.role === 'admin' || user.role === 'inventory_manager';
        case 'checkout':
        case 'returns':
          return user.role === 'admin' || user.role === 'cashier';
        case 'ml-dashboard':
          return user.role === 'admin';
        case 'cash-register':
          return user.role === 'admin' || user.role === 'cashier';
        case 'loyalty-system':
          return user.role === 'admin' || user.role === 'cashier';
        case 'crm':
          return user.role === 'admin' || user.role === 'cashier';
        case 'whatsapp':
          return user.role === 'admin' || user.role === 'cashier';
        case 'rbac':
          return user.role === 'admin';
        case 'config':
          return user.role === 'admin';
        default:
          return true;
      }
    };

    if (!hasAccess()) {
      return (
        <div style={{ 
          textAlign: 'center', 
          padding: '50px',
          color: '#f44336'
        }}>
          <h2>🚫 Access Denied</h2>
          <p>You don't have permission to access this page.</p>
          <p>Your role: {user.role}</p>
        </div>
      );
    }

    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'dealers':
        return <Dealers />;
      case 'brands':
        return <Brands />;
      case 'products':
        return <Products />;
      case 'inventory':
        return <Inventory />;
      case 'checkout':
        return <Checkout />;
      case 'returns':
        return <Returns />;
      case 'ml-dashboard':
        return <MLDashboard />;
      case 'cash-register':
        return <CashRegister />;
      case 'loyalty-system':
        return <LoyaltySystem />;
      case 'crm':
        return <CRM />;
              case 'whatsapp':
          return <WhatsAppManager />;
        case 'rbac':
          return <RBACManager />;
        case 'config':
          return <ConfigManager />;
        default:
          return <Dashboard />;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <h1>🏪 Garments POS System</h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div style={{ textAlign: 'right', color: '#fff' }}>
              <div>👤 {user.username}</div>
              <div style={{ fontSize: '12px', opacity: 0.8 }}>
                Role: {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
              </div>
            </div>
            <button
              onClick={handleLogout}
              style={{
                padding: '8px 16px',
                backgroundColor: '#f44336',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              🚪 Logout
            </button>
          </div>
        </div>
        <nav>
          {user.role === 'admin' && (
            <button
              className={`nav-btn ${currentPage === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dashboard')}
            >
              📊 Dashboard
            </button>
          )}
          {user.role === 'admin' && (
            <button
              className={`nav-btn ${currentPage === 'dealers' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dealers')}
            >
              📋 Dealers
            </button>
          )}
          {user.role === 'admin' && (
            <button
              className={`nav-btn ${currentPage === 'brands' ? 'active' : ''}`}
              onClick={() => setCurrentPage('brands')}
            >
              🏷️ Brands
            </button>
          )}
          {user.role === 'admin' && (
            <button
              className={`nav-btn ${currentPage === 'products' ? 'active' : ''}`}
              onClick={() => setCurrentPage('products')}
            >
              👕 Products
            </button>
          )}
          {(user.role === 'admin' || user.role === 'inventory_manager') && (
            <button
              className={`nav-btn ${currentPage === 'inventory' ? 'active' : ''}`}
              onClick={() => setCurrentPage('inventory')}
            >
              📦 Inventory
            </button>
          )}
          {(user.role === 'admin' || user.role === 'cashier') && (
            <button
              className={`nav-btn ${currentPage === 'checkout' ? 'active' : ''}`}
              onClick={() => setCurrentPage('checkout')}
            >
              🛒 Checkout
            </button>
          )}
          {(user.role === 'admin' || user.role === 'cashier') && (
            <button
              className={`nav-btn ${currentPage === 'returns' ? 'active' : ''}`}
              onClick={() => setCurrentPage('returns')}
            >
              🔄 Returns
            </button>
          )}
          {user.role === 'admin' && (
            <button
              className={`nav-btn ${currentPage === 'ml-dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentPage('ml-dashboard')}
            >
              🤖 ML Intelligence
            </button>
          )}
          {(user.role === 'admin' || user.role === 'cashier') && (
            <button
              className={`nav-btn ${currentPage === 'cash-register' ? 'active' : ''}`}
              onClick={() => setCurrentPage('cash-register')}
            >
              💰 Cash Register
            </button>
          )}
          {(user.role === 'admin' || user.role === 'cashier') && (
            <button
              className={`nav-btn ${currentPage === 'loyalty-system' ? 'active' : ''}`}
              onClick={() => setCurrentPage('loyalty-system')}
            >
              🎯 Loyalty System
            </button>
          )}
          {(user.role === 'admin' || user.role === 'cashier') && (
            <button
              className={`nav-btn ${currentPage === 'crm' ? 'active' : ''}`}
              onClick={() => setCurrentPage('crm')}
            >
              👥 CRM
            </button>
          )}
          {(user.role === 'admin' || user.role === 'cashier') && (
            <button
              className={`nav-btn ${currentPage === 'whatsapp' ? 'active' : ''}`}
              onClick={() => setCurrentPage('whatsapp')}
            >
              📱 WhatsApp
            </button>
          )}
          {user.role === 'admin' && (
            <button
              className={`nav-btn ${currentPage === 'rbac' ? 'active' : ''}`}
              onClick={() => setCurrentPage('rbac')}
            >
              🔐 RBAC
            </button>
          )}
          {user.role === 'admin' && (
            <button
              className={`nav-btn ${currentPage === 'config' ? 'active' : ''}`}
              onClick={() => setCurrentPage('config')}
            >
              ⚙️ Config
            </button>
          )}
        </nav>
      </header>
      <main>
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
// Updated Sat Sep 27 02:02:51 IST 2025
