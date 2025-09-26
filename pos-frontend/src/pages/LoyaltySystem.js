import React, { useState, useEffect } from 'react';
import api from '../api';

const LoyaltySystem = () => {
  const [customers, setCustomers] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [customerLoyalty, setCustomerLoyalty] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCustomerForm, setShowCustomerForm] = useState(false);
  const [showRedemptionForm, setShowRedemptionForm] = useState(false);
  
  // Form states
  const [customerForm, setCustomerForm] = useState({
    name: '',
    phone: '',
    email: '',
    address: ''
  });
  
  const [redemptionForm, setRedemptionForm] = useState({
    customer_phone: '',
    points_to_redeem: ''
  });

  useEffect(() => {
    fetchCustomers();
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

  const handleCreateCustomer = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await api.post('/customers/', customerForm);
      setCustomerForm({ name: '', phone: '', email: '', address: '' });
      setShowCustomerForm(false);
      fetchCustomers();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error creating customer');
    } finally {
      setLoading(false);
    }
  };

  const handleCustomerSelect = async (customer) => {
    try {
      setLoading(true);
      const response = await api.get(`/customers/${customer.id}/loyalty`);
      setCustomerLoyalty(response.data);
      setSelectedCustomer(customer);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error fetching customer loyalty info');
    } finally {
      setLoading(false);
    }
  };

  const handleRedeemPoints = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await api.post('/loyalty/redemption', {
        customer_phone: redemptionForm.customer_phone,
        points_to_redeem: parseInt(redemptionForm.points_to_redeem)
      });
      
      setRedemptionForm({ customer_phone: '', points_to_redeem: '' });
      setShowRedemptionForm(false);
      
      // Show success message
      alert(`Successfully redeemed ${response.data.points_redeemed} points for Rs. ${response.data.discount_amount} discount!`);
      
      // Refresh customer data if it's the selected customer
      if (selectedCustomer && selectedCustomer.phone === redemptionForm.customer_phone) {
        handleCustomerSelect(selectedCustomer);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error redeeming points');
    } finally {
      setLoading(false);
    }
  };

  const getTransactionTypeColor = (type) => {
    switch (type) {
      case 'EARNED': return '#4caf50';
      case 'REDEEMED': return '#f44336';
      case 'ADJUSTED': return '#ff9800';
      default: return '#757575';
    }
  };

  const getTransactionTypeIcon = (type) => {
    switch (type) {
      case 'EARNED': return '➕';
      case 'REDEEMED': return '➖';
      case 'ADJUSTED': return '⚙️';
      default: return '❓';
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <h3>🎯 Loading Loyalty System...</h3>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
        🎯 Loyalty System Management
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

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '30px' }}>
        <button
          onClick={() => setShowCustomerForm(true)}
          style={{
            padding: '10px 20px',
            backgroundColor: '#4caf50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          ➕ Add Customer
        </button>
        
        <button
          onClick={() => setShowRedemptionForm(true)}
          style={{
            padding: '10px 20px',
            backgroundColor: '#ff9800',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          🎁 Redeem Points
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
        {/* Customers List */}
        <div>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>👥 Customers</h3>
          
          {customers.length > 0 ? (
            <div style={{ 
              backgroundColor: '#f5f5f5', 
              padding: '15px', 
              borderRadius: '8px',
              border: '1px solid #ddd',
              maxHeight: '500px',
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
                      <strong style={{ fontSize: '16px' }}>{customer.name}</strong>
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
                        Rs. {customer.total_spent.toFixed(2)}
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
              <p style={{ color: '#666' }}>Add your first customer to start the loyalty program!</p>
            </div>
          )}
        </div>

        {/* Customer Loyalty Details */}
        <div>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>🎯 Customer Loyalty Details</h3>
          
          {customerLoyalty ? (
            <div style={{ 
              backgroundColor: '#f5f5f5', 
              padding: '20px', 
              borderRadius: '8px',
              border: '1px solid #ddd'
            }}>
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ marginBottom: '10px', color: '#333' }}>{customerLoyalty.customer.name}</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px' }}>
                  <div style={{
                    backgroundColor: '#e8f5e8',
                    padding: '15px',
                    borderRadius: '8px',
                    border: '1px solid #4caf50'
                  }}>
                    <h5 style={{ color: '#4caf50', margin: '0 0 10px 0' }}>🎯 Loyalty Points</h5>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4caf50' }}>
                      {customerLoyalty.loyalty_points}
                    </div>
                  </div>
                  
                  <div style={{
                    backgroundColor: '#e3f2fd',
                    padding: '15px',
                    borderRadius: '8px',
                    border: '1px solid #2196f3'
                  }}>
                    <h5 style={{ color: '#2196f3', margin: '0 0 10px 0' }}>💰 Total Spent</h5>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2196f3' }}>
                      Rs. {customerLoyalty.total_spent.toFixed(2)}
                    </div>
                  </div>
                  
                  <div style={{
                    backgroundColor: '#fff3e0',
                    padding: '15px',
                    borderRadius: '8px',
                    border: '1px solid #ff9800'
                  }}>
                    <h5 style={{ color: '#ff9800', margin: '0 0 10px 0' }}>📦 Total Orders</h5>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ff9800' }}>
                      {customerLoyalty.total_orders}
                    </div>
                  </div>
                  
                  <div style={{
                    backgroundColor: '#f3e5f5',
                    padding: '15px',
                    borderRadius: '8px',
                    border: '1px solid #9c27b0'
                  }}>
                    <h5 style={{ color: '#9c27b0', margin: '0 0 10px 0' }}>📱 Phone</h5>
                    <div style={{ fontSize: '16px', fontWeight: 'bold', color: '#9c27b0' }}>
                      {customerLoyalty.customer.phone}
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Transactions */}
              <div>
                <h5 style={{ marginBottom: '15px', color: '#333' }}>📋 Recent Transactions</h5>
                {customerLoyalty.recent_transactions.length > 0 ? (
                  <div style={{ maxHeight: '300px', overflow: 'auto' }}>
                    {customerLoyalty.recent_transactions.map((transaction) => (
                      <div key={transaction.id} style={{ 
                        padding: '10px', 
                        marginBottom: '10px', 
                        backgroundColor: 'white',
                        borderRadius: '4px',
                        border: '1px solid #ddd'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                              <span style={{ fontSize: '16px' }}>
                                {getTransactionTypeIcon(transaction.transaction_type)}
                              </span>
                              <strong>{transaction.transaction_type}</strong>
                            </div>
                            <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
                              {transaction.description}
                            </div>
                            <div style={{ fontSize: '12px', color: '#999' }}>
                              {new Date(transaction.created_at).toLocaleString()}
                            </div>
                          </div>
                          <div style={{ 
                            backgroundColor: getTransactionTypeColor(transaction.transaction_type), 
                            color: 'white', 
                            padding: '5px 10px',
                            borderRadius: '4px',
                            fontSize: '14px',
                            fontWeight: 'bold'
                          }}>
                            {transaction.points > 0 ? '+' : ''}{transaction.points} pts
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
                    No transactions found for this customer.
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div style={{ 
              textAlign: 'center', 
              padding: '40px', 
              backgroundColor: '#f5f5f5',
              borderRadius: '8px',
              border: '1px solid #ddd'
            }}>
              <h4 style={{ color: '#666', marginBottom: '10px' }}>Select a Customer</h4>
              <p style={{ color: '#666' }}>Choose a customer from the list to view their loyalty details.</p>
            </div>
          )}
        </div>
      </div>

      {/* Add Customer Form */}
      {showCustomerForm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '8px',
            width: '90%',
            maxWidth: '500px'
          }}>
            <h3 style={{ marginBottom: '20px', textAlign: 'center' }}>➕ Add New Customer</h3>
            
            <form onSubmit={handleCreateCustomer}>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Name: *
                </label>
                <input
                  type="text"
                  value={customerForm.name}
                  onChange={(e) => setCustomerForm({...customerForm, name: e.target.value})}
                  required
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '16px'
                  }}
                  placeholder="Enter customer name"
                />
              </div>
              
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Phone Number: *
                </label>
                <input
                  type="tel"
                  value={customerForm.phone}
                  onChange={(e) => setCustomerForm({...customerForm, phone: e.target.value})}
                  required
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '16px'
                  }}
                  placeholder="Enter phone number"
                />
              </div>
              
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Email (Optional):
                </label>
                <input
                  type="email"
                  value={customerForm.email}
                  onChange={(e) => setCustomerForm({...customerForm, email: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '16px'
                  }}
                  placeholder="Enter email address"
                />
              </div>
              
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Address (Optional):
                </label>
                <textarea
                  value={customerForm.address}
                  onChange={(e) => setCustomerForm({...customerForm, address: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '16px',
                    minHeight: '80px'
                  }}
                  placeholder="Enter address"
                />
              </div>
              
              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    flex: 1,
                    padding: '12px',
                    backgroundColor: loading ? '#ccc' : '#4caf50',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: loading ? 'not-allowed' : 'pointer'
                  }}
                >
                  {loading ? 'Creating...' : 'Create Customer'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCustomerForm(false)}
                  style={{
                    flex: 1,
                    padding: '12px',
                    backgroundColor: '#f44336',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Redeem Points Form */}
      {showRedemptionForm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '8px',
            width: '90%',
            maxWidth: '500px'
          }}>
            <h3 style={{ marginBottom: '20px', textAlign: 'center' }}>🎁 Redeem Loyalty Points</h3>
            
            <form onSubmit={handleRedeemPoints}>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Customer Phone Number: *
                </label>
                <input
                  type="tel"
                  value={redemptionForm.customer_phone}
                  onChange={(e) => setRedemptionForm({...redemptionForm, customer_phone: e.target.value})}
                  required
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '16px'
                  }}
                  placeholder="Enter customer phone number"
                />
              </div>
              
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Points to Redeem: *
                </label>
                <input
                  type="number"
                  value={redemptionForm.points_to_redeem}
                  onChange={(e) => setRedemptionForm({...redemptionForm, points_to_redeem: e.target.value})}
                  required
                  min="1"
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '16px'
                  }}
                  placeholder="Enter points to redeem"
                />
                <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                  💡 1 point = Rs. 1 discount
                </div>
              </div>
              
              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    flex: 1,
                    padding: '12px',
                    backgroundColor: loading ? '#ccc' : '#ff9800',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: loading ? 'not-allowed' : 'pointer'
                  }}
                >
                  {loading ? 'Redeeming...' : 'Redeem Points'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowRedemptionForm(false)}
                  style={{
                    flex: 1,
                    padding: '12px',
                    backgroundColor: '#f44336',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default LoyaltySystem; 