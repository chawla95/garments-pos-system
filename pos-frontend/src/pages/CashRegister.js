import React, { useState, useEffect } from 'react';
import api from '../api';

const CashRegister = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showOpenForm, setShowOpenForm] = useState(false);
  const [showExpenseForm, setShowExpenseForm] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState([]);
  
  // Form states
  const [openForm, setOpenForm] = useState({
    opening_balance: '',
    notes: ''
  });
  
  const [expenseForm, setExpenseForm] = useState({
    category: '',
    description: '',
    amount: ''
  });

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/cash-register/status');
      setStatus(response.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setStatus(null); // No register opened
      } else {
        setError(err.response?.data?.detail || 'Error fetching cash register status');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleOpenRegister = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await api.post('/cash-register/open', {
        opening_balance: parseFloat(openForm.opening_balance),
        notes: openForm.notes
      });
      setOpenForm({ opening_balance: '', notes: '' });
      setShowOpenForm(false);
      fetchStatus();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error opening cash register');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseRegister = async () => {
    try {
      setLoading(true);
      await api.post('/cash-register/close');
      fetchStatus();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error closing cash register');
    } finally {
      setLoading(false);
    }
  };

  const handleAddExpense = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await api.post('/cash-register/expenses', {
        category: expenseForm.category,
        description: expenseForm.description,
        amount: parseFloat(expenseForm.amount)
      });
      setExpenseForm({ category: '', description: '', amount: '' });
      setShowExpenseForm(false);
      fetchStatus();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error adding expense');
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const response = await api.get('/cash-register/history');
      setHistory(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error fetching history');
    } finally {
      setLoading(false);
    }
  };

  const exportDailyLog = async (date) => {
    try {
      const response = await api.get(`/cash-register/export/${date}`);
      const dataStr = JSON.stringify(response.data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `cash_register_${date}.json`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error exporting daily log');
    }
  };

  const expenseCategories = [
    "Courier", "Packaging", "Lunch", "Transport", "Utilities", 
    "Maintenance", "Supplies", "Other"
  ];

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <h3>💰 Loading Cash Register...</h3>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
        💰 Cash Register Management
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

      {/* Cash Register Status */}
      {status ? (
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>📊 Today's Cash Register Status</h3>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '20px', 
            marginBottom: '20px' 
          }}>
            <div style={{
              backgroundColor: '#e8f5e8',
              padding: '20px',
              borderRadius: '8px',
              border: '1px solid #4caf50'
            }}>
              <h4 style={{ color: '#4caf50', margin: '0 0 10px 0' }}>💰 Opening Balance</h4>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4caf50' }}>
                Rs. {status.opening_balance.toFixed(2)}
              </div>
            </div>

            <div style={{
              backgroundColor: '#e3f2fd',
              padding: '20px',
              borderRadius: '8px',
              border: '1px solid #2196f3'
            }}>
              <h4 style={{ color: '#2196f3', margin: '0 0 10px 0' }}>📈 Total Sales</h4>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#2196f3' }}>
                Rs. {status.total_sales.toFixed(2)}
              </div>
            </div>

            <div style={{
              backgroundColor: '#fff3e0',
              padding: '20px',
              borderRadius: '8px',
              border: '1px solid #ff9800'
            }}>
              <h4 style={{ color: '#ff9800', margin: '0 0 10px 0' }}>🔄 Total Returns</h4>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ff9800' }}>
                Rs. {status.total_returns.toFixed(2)}
              </div>
            </div>

            <div style={{
              backgroundColor: '#ffebee',
              padding: '20px',
              borderRadius: '8px',
              border: '1px solid #f44336'
            }}>
              <h4 style={{ color: '#f44336', margin: '0 0 10px 0' }}>💸 Total Expenses</h4>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f44336' }}>
                Rs. {status.total_expenses.toFixed(2)}
              </div>
            </div>

            <div style={{
              backgroundColor: '#f3e5f5',
              padding: '20px',
              borderRadius: '8px',
              border: '1px solid #9c27b0'
            }}>
              <h4 style={{ color: '#9c27b0', margin: '0 0 10px 0' }}>💵 Net Cash</h4>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#9c27b0' }}>
                Rs. {status.net_cash.toFixed(2)}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
            <button
              onClick={() => setShowExpenseForm(true)}
              style={{
                padding: '10px 20px',
                backgroundColor: '#ff9800',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              ➕ Add Expense
            </button>
            
            <button
              onClick={handleCloseRegister}
              style={{
                padding: '10px 20px',
                backgroundColor: '#f44336',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              🔒 Close Register
            </button>
            
            <button
              onClick={() => {
                setShowHistory(true);
                fetchHistory();
              }}
              style={{
                padding: '10px 20px',
                backgroundColor: '#2196f3',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              📋 View History
            </button>
          </div>

          {/* Expenses List */}
          {status.expenses && status.expenses.length > 0 && (
            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ marginBottom: '10px', color: '#333' }}>📝 Today's Expenses</h4>
              <div style={{ 
                backgroundColor: '#f5f5f5', 
                padding: '15px', 
                borderRadius: '8px',
                border: '1px solid #ddd'
              }}>
                {status.expenses.map((expense, index) => (
                  <div key={index} style={{ 
                    padding: '10px', 
                    marginBottom: '10px', 
                    backgroundColor: 'white',
                    borderRadius: '4px',
                    border: '1px solid #ddd'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <strong>{expense.category}</strong>
                        <div style={{ fontSize: '14px', color: '#666' }}>
                          {expense.description}
                        </div>
                      </div>
                      <div style={{ 
                        backgroundColor: '#f44336', 
                        color: 'white', 
                        padding: '5px 10px',
                        borderRadius: '4px',
                        fontSize: '14px'
                      }}>
                        Rs. {expense.amount.toFixed(2)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <h3 style={{ color: '#666', marginBottom: '20px' }}>💰 No Cash Register Opened Today</h3>
          <button
            onClick={() => setShowOpenForm(true)}
            style={{
              padding: '15px 30px',
              backgroundColor: '#4caf50',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '16px'
            }}
          >
            🔓 Open Cash Register
          </button>
        </div>
      )}

      {/* Open Register Form */}
      {showOpenForm && (
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
            <h3 style={{ marginBottom: '20px', textAlign: 'center' }}>🔓 Open Cash Register</h3>
            
            <form onSubmit={handleOpenRegister}>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Opening Balance (Rs.):
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={openForm.opening_balance}
                  onChange={(e) => setOpenForm({...openForm, opening_balance: e.target.value})}
                  required
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '16px'
                  }}
                  placeholder="Enter opening balance"
                />
              </div>
              
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Notes (Optional):
                </label>
                <textarea
                  value={openForm.notes}
                  onChange={(e) => setOpenForm({...openForm, notes: e.target.value})}
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '16px',
                    minHeight: '80px'
                  }}
                  placeholder="Any notes for today's register"
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
                  {loading ? 'Opening...' : 'Open Register'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowOpenForm(false)}
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

      {/* Add Expense Form */}
      {showExpenseForm && (
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
            <h3 style={{ marginBottom: '20px', textAlign: 'center' }}>💸 Add Expense</h3>
            
            <form onSubmit={handleAddExpense}>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Category:
                </label>
                <select
                  value={expenseForm.category}
                  onChange={(e) => setExpenseForm({...expenseForm, category: e.target.value})}
                  required
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '16px'
                  }}
                >
                  <option value="">Select Category</option>
                  {expenseCategories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
              
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Description:
                </label>
                <input
                  type="text"
                  value={expenseForm.description}
                  onChange={(e) => setExpenseForm({...expenseForm, description: e.target.value})}
                  required
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '16px'
                  }}
                  placeholder="Enter expense description"
                />
              </div>
              
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Amount (Rs.):
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={expenseForm.amount}
                  onChange={(e) => setExpenseForm({...expenseForm, amount: e.target.value})}
                  required
                  style={{
                    width: '100%',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    fontSize: '16px'
                  }}
                  placeholder="Enter amount"
                />
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
                  {loading ? 'Adding...' : 'Add Expense'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowExpenseForm(false)}
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

      {/* History Modal */}
      {showHistory && (
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
            maxWidth: '800px',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <h3 style={{ marginBottom: '20px', textAlign: 'center' }}>📋 Cash Register History</h3>
            
            {history.length > 0 ? (
              <div>
                {history.map((register, index) => (
                  <div key={index} style={{ 
                    padding: '15px', 
                    marginBottom: '15px', 
                    backgroundColor: '#f5f5f5',
                    borderRadius: '8px',
                    border: '1px solid #ddd'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <h4 style={{ margin: 0 }}>
                        {new Date(register.date).toLocaleDateString()}
                      </h4>
                      <button
                        onClick={() => exportDailyLog(new Date(register.date).toISOString().split('T')[0])}
                        style={{
                          padding: '5px 10px',
                          backgroundColor: '#2196f3',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px'
                        }}
                      >
                        📥 Export
                      </button>
                    </div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px' }}>
                      <div>
                        <strong>Opening:</strong> Rs. {register.opening_balance.toFixed(2)}
                      </div>
                      <div>
                        <strong>Sales:</strong> Rs. {register.total_sales.toFixed(2)}
                      </div>
                      <div>
                        <strong>Returns:</strong> Rs. {register.total_returns.toFixed(2)}
                      </div>
                      <div>
                        <strong>Expenses:</strong> Rs. {register.total_expenses.toFixed(2)}
                      </div>
                      <div>
                        <strong>Closing:</strong> Rs. {register.closing_balance.toFixed(2)}
                      </div>
                    </div>
                    
                    {register.notes && (
                      <div style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
                        <strong>Notes:</strong> {register.notes}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', color: '#666' }}>
                No cash register history found.
              </div>
            )}
            
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <button
                onClick={() => setShowHistory(false)}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#f44336',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer'
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CashRegister; 