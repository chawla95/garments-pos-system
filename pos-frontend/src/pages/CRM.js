import React, { useState, useEffect } from 'react';
import api from '../api';

const CRM = () => {
  const [customers, setCustomers] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [customerHistory, setCustomerHistory] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('customers');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Export options
  const [exportOptions, setExportOptions] = useState({
    include_phone: true,
    include_email: true,
    include_address: true,
    include_loyalty: true,
    include_visit_history: true
  });

  useEffect(() => {
    fetchCustomers();
    fetchAnalytics();
  }, []);

  const fetchCustomers = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/customers/');
      setCustomers(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error fetching customers');
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/crm/analytics');
      setAnalytics(response.data);
    } catch (err) {
      console.error('Error fetching analytics:', err);
    }
  };

  const searchCustomers = async () => {
    if (!searchTerm.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      setLoading(true);
      const response = await api.post('/crm/search', {
        search_term: searchTerm
      });
      setSearchResults(response.data.customers);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error searching customers');
    } finally {
      setLoading(false);
    }
  };

  const handleCustomerSelect = async (customer) => {
    try {
      setLoading(true);
      const response = await api.get(`/crm/customers/${customer.id}/visits`);
      setCustomerHistory(response.data);
      setSelectedCustomer(customer);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error fetching customer history');
    } finally {
      setLoading(false);
    }
  };

  const exportCustomers = async () => {
    try {
      const params = new URLSearchParams(exportOptions);
      const response = await api.get(`/crm/customers/export?${params}`, {
        responseType: 'blob'
      });
      
      // Create download link
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `customers_export_${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error exporting customers');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleDateString();
  };

  const formatCurrency = (amount) => {
    return `₹${parseFloat(amount).toFixed(2)}`;
  };

  if (loading && customers.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <h3>👥 Loading CRM System...</h3>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
        👥 Customer Relationship Management (CRM)
      </h2>

      {error && (
        <div style={{
          backgroundColor: '#ffebee',
          color: '#c62828',
          padding: '15px',
          borderRadius: '8px',
          marginBottom: '20px',
          textAlign: 'center'
        }}>
          {error}
          <button 
            onClick={() => setError('')}
            style={{
              marginLeft: '10px',
              padding: '5px 10px',
              backgroundColor: '#c62828',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Navigation Tabs */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '30px' }}>
        <button
          className={`btn ${activeTab === 'customers' ? 'btn-success' : ''}`}
          onClick={() => setActiveTab('customers')}
        >
          👥 All Customers
        </button>
        <button
          className={`btn ${activeTab === 'search' ? 'btn-success' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          🔍 Search Customers
        </button>
        <button
          className={`btn ${activeTab === 'analytics' ? 'btn-success' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          📊 Analytics
        </button>
        <button
          className={`btn ${activeTab === 'export' ? 'btn-success' : ''}`}
          onClick={() => setActiveTab('export')}
        >
          📤 Export Data
        </button>
      </div>

      {/* All Customers Tab */}
      {activeTab === 'customers' && (
        <div>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>👥 All Customers ({customers.length})</h3>
          
          {customers.length > 0 ? (
            <div style={{ 
              backgroundColor: '#f5f5f5', 
              padding: '15px', 
              borderRadius: '8px',
              border: '1px solid #ddd',
              maxHeight: '600px',
              overflow: 'auto'
            }}>
              {customers.map((customer) => (
                <div 
                  key={customer.id} 
                  onClick={() => handleCustomerSelect(customer)}
                  style={{ 
                    padding: '15px', 
                    marginBottom: '10px', 
                    backgroundColor: 'white',
                    borderRadius: '8px',
                    border: '1px solid #ddd',
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    borderLeft: selectedCustomer?.id === customer.id ? '4px solid #2196f3' : '1px solid #ddd'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#f0f8ff'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = 'white'}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <strong style={{ fontSize: '16px' }}>
                        {customer.name || 'Anonymous Customer'}
                      </strong>
                      <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
                        📱 {customer.phone}
                      </div>
                      {customer.email && (
                        <div style={{ fontSize: '14px', color: '#666' }}>
                          📧 {customer.email}
                        </div>
                      )}
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ 
                        backgroundColor: '#4caf50', 
                        color: 'white', 
                        padding: '5px 10px',
                        borderRadius: '4px',
                        fontSize: '14px',
                        fontWeight: 'bold'
                      }}>
                        🎯 {customer.loyalty_points} pts
                      </div>
                      <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                        💰 {formatCurrency(customer.total_spent)}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        📦 {customer.total_orders} orders
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ 
              textAlign: 'center', 
              padding: '40px', 
              backgroundColor: '#f5f5f5',
              borderRadius: '8px',
              border: '1px solid #ddd'
            }}>
              <h4 style={{ color: '#666', marginBottom: '10px' }}>No Customers Found</h4>
              <p style={{ color: '#666' }}>Customers will be automatically created during checkout.</p>
            </div>
          )}
        </div>
      )}

      {/* Search Customers Tab */}
      {activeTab === 'search' && (
        <div>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>🔍 Search Customers</h3>
          
          <div style={{ marginBottom: '20px' }}>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search by name or phone number..."
                style={{
                  flex: 1,
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '4px',
                  fontSize: '16px'
                }}
                onKeyPress={(e) => e.key === 'Enter' && searchCustomers()}
              />
              <button
                onClick={searchCustomers}
                disabled={loading}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#2196f3',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>

          {searchResults.length > 0 && (
            <div style={{ 
              backgroundColor: '#f5f5f5', 
              padding: '15px', 
              borderRadius: '8px',
              border: '1px solid #ddd'
            }}>
              <h4 style={{ marginBottom: '15px' }}>Search Results ({searchResults.length})</h4>
              {searchResults.map((customer) => (
                <div 
                  key={customer.id} 
                  onClick={() => handleCustomerSelect(customer)}
                  style={{ 
                    padding: '15px', 
                    marginBottom: '10px', 
                    backgroundColor: 'white',
                    borderRadius: '8px',
                    border: '1px solid #ddd',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => e.target.style.backgroundColor = '#f0f8ff'}
                  onMouseLeave={(e) => e.target.style.backgroundColor = 'white'}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <strong style={{ fontSize: '16px' }}>
                        {customer.name || 'Anonymous Customer'}
                      </strong>
                      <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
                        📱 {customer.phone}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ 
                        backgroundColor: '#4caf50', 
                        color: 'white', 
                        padding: '5px 10px',
                        borderRadius: '4px',
                        fontSize: '14px',
                        fontWeight: 'bold'
                      }}>
                        🎯 {customer.loyalty_points} pts
                      </div>
                      <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                        💰 {formatCurrency(customer.total_spent)}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Analytics Tab */}
      {activeTab === 'analytics' && analytics && (
        <div>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>📊 CRM Analytics</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
            <div style={{
              backgroundColor: '#e3f2fd',
              padding: '20px',
              borderRadius: '8px',
              border: '1px solid #2196f3'
            }}>
              <h4 style={{ color: '#2196f3', margin: '0 0 10px 0' }}>👥 Total Customers</h4>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2196f3' }}>
                {analytics.total_customers}
              </div>
            </div>

            <div style={{
              backgroundColor: '#e8f5e8',
              padding: '20px',
              borderRadius: '8px',
              border: '1px solid #4caf50'
            }}>
              <h4 style={{ color: '#4caf50', margin: '0 0 10px 0' }}>📝 Named Customers</h4>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4caf50' }}>
                {analytics.named_customers}
              </div>
            </div>

            <div style={{
              backgroundColor: '#fff3e0',
              padding: '20px',
              borderRadius: '8px',
              border: '1px solid #ff9800'
            }}>
              <h4 style={{ color: '#ff9800', margin: '0 0 10px 0' }}>🆕 Recent (30 days)</h4>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ff9800' }}>
                {analytics.recent_customers_30_days}
              </div>
            </div>

            <div style={{
              backgroundColor: '#f3e5f5',
              padding: '20px',
              borderRadius: '8px',
              border: '1px solid #9c27b0'
            }}>
              <h4 style={{ color: '#9c27b0', margin: '0 0 10px 0' }}>💰 Avg Spent</h4>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#9c27b0' }}>
                {formatCurrency(analytics.average_spent)}
              </div>
            </div>
          </div>

          <div style={{ marginBottom: '30px' }}>
            <h4 style={{ marginBottom: '15px', color: '#333' }}>🏆 Top Customers by Spending</h4>
            <div style={{ 
              backgroundColor: '#f5f5f5', 
              padding: '15px', 
              borderRadius: '8px',
              border: '1px solid #ddd'
            }}>
              {analytics.top_customers.map((customer, index) => (
                <div key={customer.id} style={{ 
                  padding: '10px', 
                  marginBottom: '10px', 
                  backgroundColor: 'white',
                  borderRadius: '4px',
                  border: '1px solid #ddd'
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <strong>#{index + 1} {customer.name}</strong>
                      <div style={{ fontSize: '14px', color: '#666' }}>
                        📱 {customer.phone}
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#4caf50' }}>
                        {formatCurrency(customer.total_spent)}
                      </div>
                      <div style={{ fontSize: '12px', color: '#666' }}>
                        📦 {customer.total_orders} orders
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Export Tab */}
      {activeTab === 'export' && (
        <div>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>📤 Export Customer Data</h3>
          
          <div style={{ 
            backgroundColor: '#f5f5f5', 
            padding: '20px', 
            borderRadius: '8px',
            border: '1px solid #ddd',
            marginBottom: '20px'
          }}>
            <h4 style={{ marginBottom: '15px', color: '#333' }}>Export Options</h4>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input
                  type="checkbox"
                  checked={exportOptions.include_phone}
                  onChange={(e) => setExportOptions({...exportOptions, include_phone: e.target.checked})}
                />
                📱 Phone Number
              </label>
              
              <label style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input
                  type="checkbox"
                  checked={exportOptions.include_email}
                  onChange={(e) => setExportOptions({...exportOptions, include_email: e.target.checked})}
                />
                📧 Email Address
              </label>
              
              <label style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input
                  type="checkbox"
                  checked={exportOptions.include_address}
                  onChange={(e) => setExportOptions({...exportOptions, include_address: e.target.checked})}
                />
                🏠 Address
              </label>
              
              <label style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input
                  type="checkbox"
                  checked={exportOptions.include_loyalty}
                  onChange={(e) => setExportOptions({...exportOptions, include_loyalty: e.target.checked})}
                />
                🎯 Loyalty Data
              </label>
              
              <label style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <input
                  type="checkbox"
                  checked={exportOptions.include_visit_history}
                  onChange={(e) => setExportOptions({...exportOptions, include_visit_history: e.target.checked})}
                />
                📅 Visit History
              </label>
            </div>
            
            <button
              onClick={exportCustomers}
              style={{
                marginTop: '20px',
                padding: '12px 24px',
                backgroundColor: '#4caf50',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              📤 Export to CSV
            </button>
          </div>
        </div>
      )}

      {/* Customer History Sidebar */}
      {customerHistory && (
        <div style={{
          position: 'fixed',
          top: 0,
          right: 0,
          width: '400px',
          height: '100vh',
          backgroundColor: 'white',
          borderLeft: '1px solid #ddd',
          padding: '20px',
          overflow: 'auto',
          zIndex: 1000
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3 style={{ margin: 0, color: '#333' }}>Customer History</h3>
            <button
              onClick={() => setCustomerHistory(null)}
              style={{
                padding: '5px 10px',
                backgroundColor: '#f44336',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              ✕
            </button>
          </div>

          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ marginBottom: '10px', color: '#333' }}>
              {customerHistory.customer.name || 'Anonymous Customer'}
            </h4>
            <div style={{ fontSize: '14px', color: '#666' }}>
              📱 {customerHistory.customer.phone}
            </div>
            {customerHistory.customer.email && (
              <div style={{ fontSize: '14px', color: '#666' }}>
                📧 {customerHistory.customer.email}
              </div>
            )}
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '20px' }}>
            <div style={{
              backgroundColor: '#e8f5e8',
              padding: '10px',
              borderRadius: '4px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '12px', color: '#666' }}>Total Visits</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#4caf50' }}>
                {customerHistory.total_visits}
              </div>
            </div>
            
            <div style={{
              backgroundColor: '#e3f2fd',
              padding: '10px',
              borderRadius: '4px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '12px', color: '#666' }}>Total Spent</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#2196f3' }}>
                {formatCurrency(customerHistory.total_spent)}
              </div>
            </div>
            
            <div style={{
              backgroundColor: '#fff3e0',
              padding: '10px',
              borderRadius: '4px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '12px', color: '#666' }}>Avg Order</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#ff9800' }}>
                {formatCurrency(customerHistory.average_order_value)}
              </div>
            </div>
            
            <div style={{
              backgroundColor: '#f3e5f5',
              padding: '10px',
              borderRadius: '4px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '12px', color: '#666' }}>Last Visit</div>
              <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#9c27b0' }}>
                {formatDate(customerHistory.last_visit_date)}
              </div>
            </div>
          </div>

          <div>
            <h5 style={{ marginBottom: '15px', color: '#333' }}>📋 Visit History</h5>
            {customerHistory.invoices.length > 0 ? (
              <div style={{ maxHeight: '400px', overflow: 'auto' }}>
                {customerHistory.invoices.map((invoice) => (
                  <div key={invoice.id} style={{ 
                    padding: '10px', 
                    marginBottom: '10px', 
                    backgroundColor: '#f5f5f5',
                    borderRadius: '4px',
                    border: '1px solid #ddd'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <strong>Invoice #{invoice.invoice_number}</strong>
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          {formatDate(invoice.created_at)}
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '14px', fontWeight: 'bold', color: '#4caf50' }}>
                          {formatCurrency(invoice.total_final_price)}
                        </div>
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          {invoice.payment_method}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
                No visit history found.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default CRM; 