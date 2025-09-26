import React, { useState, useEffect } from 'react';
import api from '../api';

const Returns = () => {
  const [invoiceNumber, setInvoiceNumber] = useState('');
  const [invoiceData, setInvoiceData] = useState(null);
  const [returnItems, setReturnItems] = useState([]);
  const [returnMethod, setReturnMethod] = useState('CASH');
  const [returnReason, setReturnReason] = useState('');
  const [walletCredit, setWalletCredit] = useState(0);
  const [cashRefund, setCashRefund] = useState(0);
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [returns, setReturns] = useState([]);
  const [activeTab, setActiveTab] = useState('process');

  useEffect(() => {
    fetchReturns();
  }, []);

  const fetchReturns = async () => {
    try {
      const response = await api.get('/returns/');
      setReturns(response.data);
    } catch (error) {
      console.error('Error fetching returns:', error);
    }
  };

  const lookupInvoice = async () => {
    if (!invoiceNumber.trim()) {
      setMessage('Please enter an invoice number');
      return;
    }

    try {
      setLoading(true);
      const response = await api.get(`/returns/invoice/${invoiceNumber}`);
      setInvoiceData(response.data);
      
      if (!response.data.can_return) {
        setMessage('This invoice has already been returned');
        return;
      }
      
      setMessage('Invoice found! Select items to return.');
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleItemReturn = (itemId, returnQty) => {
    if (returnQty < 0) return;
    
    const item = invoiceData.items.find(i => i.id === itemId);
    if (returnQty > item.quantity) {
      setMessage(`Return quantity cannot exceed original quantity (${item.quantity})`);
      return;
    }

    setReturnItems(prev => {
      const existing = prev.find(i => i.invoice_item_id === itemId);
      if (existing) {
        return prev.map(i => 
          i.invoice_item_id === itemId 
            ? { ...i, return_quantity: returnQty }
            : i
        );
      } else {
        return [...prev, { invoice_item_id: itemId, return_quantity: returnQty }];
      }
    });
  };

  const calculateReturnAmount = () => {
    if (!invoiceData) return 0;
    
    return returnItems.reduce((total, returnItem) => {
      const originalItem = invoiceData.items.find(i => i.id === returnItem.invoice_item_id);
      if (originalItem) {
        const unitPrice = originalItem.final_price / originalItem.quantity;
        return total + (unitPrice * returnItem.return_quantity);
      }
      return total;
    }, 0);
  };

  const handleReturnMethodChange = (method) => {
    setReturnMethod(method);
    const amount = calculateReturnAmount();
    
    // Auto-calculate amounts based on return method
    if (method === 'CASH') {
      setCashRefund(amount);
      setWalletCredit(0);
    } else {
      setWalletCredit(amount);
      setCashRefund(0);
    }
  };

  const processReturn = async () => {
    if (returnItems.length === 0) {
      setMessage('Please select items to return');
      return;
    }

    // Auto-calculate return amount based on selected items
    const returnAmount = calculateReturnAmount();
    
    // Auto-set amounts based on return method
    if (returnMethod === 'CASH') {
      setCashRefund(returnAmount);
      setWalletCredit(0);
    } else {
      setWalletCredit(returnAmount);
      setCashRefund(0);
    }

    try {
      setLoading(true);
      const response = await api.post('/returns/', {
        invoice_number: invoiceNumber,
        items: returnItems,
        return_reason: returnReason,
        return_method: returnMethod,
        wallet_credit: walletCredit,
        cash_refund: cashRefund,
        notes: notes
      });

      setMessage(response.data.message);
      setInvoiceData(null);
      setReturnItems([]);
      setInvoiceNumber('');
      setReturnReason('');
      setNotes('');
      setWalletCredit(0);
      setCashRefund(0);
      setReturnMethod('CASH');
      
      // Refresh returns list
      fetchReturns();
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const printReturn = async (returnId) => {
    try {
      const response = await api.get(`/returns/${returnId}/pdf`, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const printWindow = window.open(url);
      printWindow.onload = () => {
        printWindow.print();
        setTimeout(() => {
          printWindow.close();
          window.URL.revokeObjectURL(url);
        }, 1000);
      };
    } catch (error) {
      setMessage(`Error printing return: ${error.response?.data?.detail || error.message}`);
    }
  };

  const formatCurrency = (amount) => {
    return `Rs. ${parseFloat(amount || 0).toFixed(2)}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div>
      <h2>🔄 Returns Management</h2>
      
      {/* Tab Navigation */}
      <div style={{ marginBottom: '20px' }}>
        <button
          className={`btn ${activeTab === 'process' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('process')}
          style={{ marginRight: '10px' }}
        >
          📝 Process Return
        </button>
        <button
          className={`btn ${activeTab === 'history' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => setActiveTab('history')}
        >
          📋 Return History
        </button>
      </div>

      {message && (
        <div className={`alert ${message.includes('Error') ? 'alert-danger' : 'alert-success'}`}>
          {message}
        </div>
      )}

      {activeTab === 'process' && (
        <div>
          {/* Invoice Lookup */}
          <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #ddd' }}>
            <h3>🔍 Invoice Lookup</h3>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '10px' }}>
              <input
                type="text"
                placeholder="Enter Invoice Number or Scan Barcode"
                value={invoiceNumber}
                onChange={(e) => setInvoiceNumber(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    lookupInvoice();
                  }
                }}
                style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                autoFocus
              />
              <button
                className="btn btn-primary"
                onClick={lookupInvoice}
                disabled={loading}
              >
                {loading ? 'Looking up...' : '🔍 Lookup'}
              </button>
            </div>
            <div style={{ fontSize: '12px', color: '#666', textAlign: 'center' }}>
              💡 Tip: You can scan the barcode from any invoice to quickly load it for returns
            </div>
          </div>

          {/* Invoice Details */}
          {invoiceData && (
            <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #ddd' }}>
              <h3>📄 Invoice Details</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '20px' }}>
                <div>
                  <strong>Invoice Number:</strong> {invoiceData.invoice.invoice_number}
                </div>
                <div>
                  <strong>Customer:</strong> {invoiceData.invoice.customer_name || 'Walk-in Customer'}
                </div>
                <div>
                  <strong>Date:</strong> {formatDate(invoiceData.invoice.created_at)}
                </div>
                <div>
                  <strong>Total Amount:</strong> {formatCurrency(invoiceData.invoice.total_final_price)}
                </div>
              </div>

              {/* Return Items Selection */}
              <h4>Select Items to Return:</h4>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f5f5f5' }}>
                      <th style={{ padding: '10px', border: '1px solid #ddd' }}>Product</th>
                      <th style={{ padding: '10px', border: '1px solid #ddd' }}>Design No.</th>
                      <th style={{ padding: '10px', border: '1px solid #ddd' }}>Size</th>
                      <th style={{ padding: '10px', border: '1px solid #ddd' }}>Color</th>
                      <th style={{ padding: '10px', border: '1px solid #ddd' }}>Original Qty</th>
                      <th style={{ padding: '10px', border: '1px solid #ddd' }}>Return Qty</th>
                      <th style={{ padding: '10px', border: '1px solid #ddd' }}>Unit Price</th>
                      <th style={{ padding: '10px', border: '1px solid #ddd' }}>Return Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {invoiceData.items.map((item) => {
                      const returnItem = returnItems.find(i => i.invoice_item_id === item.id);
                      const returnQty = returnItem ? returnItem.return_quantity : 0;
                      const unitPrice = item.final_price / item.quantity;
                      const returnAmount = unitPrice * returnQty;
                      
                      return (
                        <tr key={item.id}>
                          <td style={{ padding: '10px', border: '1px solid #ddd' }}>{item.product_name}</td>
                          <td style={{ padding: '10px', border: '1px solid #ddd' }}>{item.design_number}</td>
                          <td style={{ padding: '10px', border: '1px solid #ddd' }}>{item.size}</td>
                          <td style={{ padding: '10px', border: '1px solid #ddd' }}>{item.color}</td>
                          <td style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'center' }}>{item.quantity}</td>
                          <td style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'center' }}>
                            <input
                              type="number"
                              min="0"
                              max={item.quantity}
                              value={returnQty}
                              onChange={(e) => handleItemReturn(item.id, parseInt(e.target.value) || 0)}
                              style={{ width: '60px', padding: '4px', textAlign: 'center' }}
                            />
                          </td>
                          <td style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'right' }}>
                            {formatCurrency(unitPrice)}
                          </td>
                          <td style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'right', fontWeight: 'bold' }}>
                            {formatCurrency(returnAmount)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Return Details */}
          {returnItems.length > 0 && (
            <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', marginBottom: '20px', border: '1px solid #ddd' }}>
              <h3>🔄 Return Details</h3>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '20px' }}>
                <div>
                  <label>Return Reason:</label>
                  <textarea
                    value={returnReason}
                    onChange={(e) => setReturnReason(e.target.value)}
                    placeholder="Enter return reason..."
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd', minHeight: '60px' }}
                  />
                </div>
                
                <div>
                  <label>Return Method:</label>
                  <select
                    value={returnMethod}
                    onChange={(e) => handleReturnMethodChange(e.target.value)}
                    style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
                  >
                    <option value="CASH">Cash Refund</option>
                    <option value="WALLET">Wallet Credit</option>
                    <option value="STORE_CREDIT">Store Credit</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '20px' }}>
                {returnMethod === 'CASH' && (
                  <div>
                    <label>Cash Refund Amount:</label>
                    <div style={{ 
                      width: '100%', 
                      padding: '8px', 
                      borderRadius: '4px', 
                      border: '1px solid #ddd', 
                      backgroundColor: '#f8f9fa',
                      fontWeight: 'bold',
                      color: '#28a745'
                    }}>
                      {formatCurrency(cashRefund)}
                    </div>
                    <small style={{ color: '#666', fontStyle: 'italic' }}>
                      Automatically calculated based on original invoice amounts
                    </small>
                  </div>
                )}
                
                {(returnMethod === 'WALLET' || returnMethod === 'STORE_CREDIT') && (
                  <div>
                    <label>Credit Amount:</label>
                    <div style={{ 
                      width: '100%', 
                      padding: '8px', 
                      borderRadius: '4px', 
                      border: '1px solid #ddd', 
                      backgroundColor: '#f8f9fa',
                      fontWeight: 'bold',
                      color: '#007bff'
                    }}>
                      {formatCurrency(walletCredit)}
                    </div>
                    <small style={{ color: '#666', fontStyle: 'italic' }}>
                      Automatically calculated based on original invoice amounts
                    </small>
                  </div>
                )}
              </div>

              <div>
                <label>Notes:</label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Additional notes..."
                  style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #ddd', minHeight: '60px' }}
                />
              </div>

              <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
                <h4>Return Summary:</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
                  <div><strong>Total Return Amount:</strong> {formatCurrency(calculateReturnAmount())}</div>
                  <div><strong>Return Method:</strong> {returnMethod}</div>
                  <div><strong>Items to Return:</strong> {returnItems.filter(i => i.return_quantity > 0).length}</div>
                </div>
              </div>

              <button
                className="btn btn-success"
                onClick={processReturn}
                disabled={loading}
                style={{ marginTop: '20px' }}
              >
                {loading ? 'Processing...' : '✅ Process Return'}
              </button>
            </div>
          )}
        </div>
      )}

      {activeTab === 'history' && (
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #ddd' }}>
          <h3>📋 Return History</h3>
          
          {returns.length > 0 ? (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f5f5f5' }}>
                    <th style={{ padding: '10px', border: '1px solid #ddd' }}>Return No.</th>
                    <th style={{ padding: '10px', border: '1px solid #ddd' }}>Original Invoice</th>
                    <th style={{ padding: '10px', border: '1px solid #ddd' }}>Date</th>
                    <th style={{ padding: '10px', border: '1px solid #ddd' }}>Customer</th>
                    <th style={{ padding: '10px', border: '1px solid #ddd' }}>Return Amount</th>
                    <th style={{ padding: '10px', border: '1px solid #ddd' }}>Method</th>
                    <th style={{ padding: '10px', border: '1px solid #ddd' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {returns.map((returnRecord) => (
                    <tr key={returnRecord.id}>
                      <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                        <strong>{returnRecord.return_number}</strong>
                      </td>
                      <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                        {returnRecord.invoice_number}
                      </td>
                      <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                        {formatDate(returnRecord.created_at)}
                      </td>
                      <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                        {returnRecord.customer_name || 'Walk-in Customer'}
                      </td>
                      <td style={{ padding: '10px', border: '1px solid #ddd', textAlign: 'right' }}>
                        {formatCurrency(Math.abs(returnRecord.total_return_amount))}
                      </td>
                      <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                        {returnRecord.return_method}
                      </td>
                      <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                        <button
                          onClick={() => printReturn(returnRecord.id)}
                          className="btn btn-primary"
                          style={{ padding: '3px 8px', fontSize: '10px' }}
                        >
                          🖨️ Print
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p style={{ textAlign: 'center', color: '#666', fontStyle: 'italic' }}>
              No returns found.
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default Returns; 