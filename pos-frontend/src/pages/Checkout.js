import React, { useState, useEffect, useCallback } from 'react';
import api from '../api';

const Checkout = () => {
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('scan');
  const [searchBarcode, setSearchBarcode] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [invoices, setInvoices] = useState([]);

  // Customer details
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [customerLoyalty, setCustomerLoyalty] = useState(null);

  // Discount and payment
  const [discountType, setDiscountType] = useState('PERCENT');
  const [discountValue, setDiscountValue] = useState(0);
  const [loyaltyPointsRedeemed, setLoyaltyPointsRedeemed] = useState(0);
  const [paymentMethod, setPaymentMethod] = useState('CASH');
  const [notes, setNotes] = useState('');

  // Calculations
  const [totalMrp, setTotalMrp] = useState(0);
  const [totalDiscount, setTotalDiscount] = useState(0);
  const [totalFinalPrice, setTotalFinalPrice] = useState(0);
  const [totalBaseAmount, setTotalBaseAmount] = useState(0);
  const [totalGstAmount, setTotalGstAmount] = useState(0);
  const [totalCgstAmount, setTotalCgstAmount] = useState(0);
  const [totalSgstAmount, setTotalSgstAmount] = useState(0);

  useEffect(() => {
    fetchInvoices();
  }, []);

  const lookupCustomer = async (phone) => {
    if (!phone.trim()) {
      setCustomerLoyalty(null);
      return;
    }

    try {
      const response = await api.get(`/customers/phone/${phone}`);
      setCustomerLoyalty(response.data);
      setCustomerName(response.data.name);
      setCustomerEmail(response.data.email || '');
    } catch (error) {
      setCustomerLoyalty(null);
      console.log('Customer not found or error:', error.response?.data?.detail);
    }
  };

  const calculateTotals = useCallback(() => {
    // Calculate total MRP (GST-inclusive)
    const newTotalMrp = cart.reduce((sum, item) => sum + (item.mrp * item.quantity), 0);
    setTotalMrp(newTotalMrp);

    // Calculate discount
    let newTotalDiscount = 0;
    if (discountType === 'PERCENT' && discountValue > 0) {
      newTotalDiscount = newTotalMrp * (discountValue / 100);
    } else if (discountType === 'FIXED' && discountValue > 0) {
      newTotalDiscount = Math.min(discountValue, newTotalMrp);
    }
    
    // Add loyalty discount
    const loyaltyDiscount = loyaltyPointsRedeemed; // 1 point = Rs. 1
    newTotalDiscount += loyaltyDiscount;
    
    setTotalDiscount(newTotalDiscount);

    // Calculate final price after discount
    const newTotalFinalPrice = newTotalMrp - newTotalDiscount;
    setTotalFinalPrice(newTotalFinalPrice);

    // Calculate base amount and GST (reverse calculation)
    const newTotalBaseAmount = newTotalFinalPrice / (1 + 12.0 / 100); // Assuming 12% GST
    const newTotalGstAmount = newTotalFinalPrice - newTotalBaseAmount;
    const newTotalCgstAmount = newTotalGstAmount / 2;
    const newTotalSgstAmount = newTotalGstAmount / 2;

    setTotalBaseAmount(newTotalBaseAmount);
    setTotalGstAmount(newTotalGstAmount);
    setTotalCgstAmount(newTotalCgstAmount);
    setTotalSgstAmount(newTotalSgstAmount);
  }, [cart, discountValue, discountType, loyaltyPointsRedeemed]);

  useEffect(() => {
    calculateTotals();
  }, [calculateTotals]);

  const fetchInvoices = async () => {
    try {
      const response = await api.get('/invoices/');
      console.log('Fetched invoices:', response.data);
      setInvoices(response.data);
    } catch (error) {
      console.error('Error fetching invoices:', error);
      // Don't show error to user, just log it
      
      // If it's an authentication error, the API interceptor will handle it
      if (error.response?.status === 401) {
        console.warn('Authentication failed, user will be redirected to login');
      }
    }
  };

  const searchByBarcode = async () => {
    if (!searchBarcode.trim()) {
      setMessage('Please enter a barcode to search');
      return;
    }

    try {
      setLoading(true);
      const response = await api.get(`/inventory/search/${searchBarcode}`);
      setSearchResult(response.data);
      setMessage('Item found!');
    } catch (error) {
      setSearchResult(null);
      setMessage(`Error: ${error.response?.data?.detail || 'Item not found'}`);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (item) => {
    const existingItem = cart.find(cartItem => cartItem.barcode === item.barcode);
    
    if (existingItem) {
      setCart(cart.map(cartItem => 
        cartItem.barcode === item.barcode 
          ? { ...cartItem, quantity: cartItem.quantity + 1 }
          : cartItem
      ));
    } else {
      setCart([...cart, { ...item, quantity: 1 }]);
    }
    
    setSearchResult(null);
    setSearchBarcode('');
    setMessage('Item added to cart!');
  };

  const removeFromCart = (barcode) => {
    setCart(cart.filter(item => item.barcode !== barcode));
    setMessage('Item removed from cart!');
  };

  const updateQuantity = (barcode, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(barcode);
      return;
    }
    
    setCart(cart.map(item => 
      item.barcode === barcode 
        ? { ...item, quantity: newQuantity }
        : item
    ));
  };

  const processCheckout = async () => {
    if (cart.length === 0) {
      setMessage('Please add items to cart before checkout');
      return;
    }

    try {
      setLoading(true);
      const checkoutData = {
        items: cart.map(item => ({
          barcode: item.barcode,
          quantity: item.quantity
        })),
        customer_name: customerName || null,
        customer_phone: customerPhone || null,
        customer_email: customerEmail || null,
        discount_type: discountValue > 0 ? discountType : null,
        discount_value: discountValue,
        loyalty_points_redeemed: loyaltyPointsRedeemed,
        payment_method: paymentMethod,
        notes: notes || null
      };

      const response = await api.post('/checkout/', checkoutData);
      
      setMessage(response.data.message);
      setCart([]);
      setCustomerName('');
      setCustomerPhone('');
      setCustomerEmail('');
      setDiscountValue(0);
      setPaymentMethod('CASH');
      setNotes('');
      setActiveTab('invoices');
      
      // Wait a moment then refresh invoices to ensure the new invoice is included
      setTimeout(() => {
        fetchInvoices();
      }, 1000);
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const clearCart = () => {
    setCart([]);
    setCustomerName('');
    setCustomerPhone('');
    setCustomerEmail('');
    setCustomerLoyalty(null);
    setLoyaltyPointsRedeemed(0);
    setDiscountValue(0);
    setPaymentMethod('CASH');
    setNotes('');
    setMessage('Cart cleared!');
  };

  const printInvoice = async (invoiceId) => {
    try {
      setLoading(true);
      const response = await api.get(`/invoices/${invoiceId}/pdf`, {
        responseType: 'blob'
      });
      
      // Create blob URL
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      
      // Open PDF in new window and trigger print
      const printWindow = window.open(url);
      printWindow.onload = () => {
        printWindow.print();
        // Close window after printing
        setTimeout(() => {
          printWindow.close();
          window.URL.revokeObjectURL(url);
        }, 1000);
      };
      
      setMessage(`Print dialog opened!`);
    } catch (error) {
      setMessage(`Error printing invoice: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const previewInvoice = async (invoiceId) => {
    try {
      setLoading(true);
      const response = await api.get(`/invoices/${invoiceId}/pdf`, {
        responseType: 'blob'
      });
      
      // Create blob URL
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      
      // Open PDF in new window for preview
      const previewWindow = window.open(url, '_blank');
      previewWindow.onload = () => {
        window.URL.revokeObjectURL(url);
      };
      
      setMessage(`Invoice preview opened!`);
    } catch (error) {
      setMessage(`Error previewing invoice: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };



  return (
    <div>
      <h2>🛒 Checkout System</h2>
      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
          <button onClick={() => setMessage('')} style={{ float: 'right', background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}>×</button>
        </div>
      )}
      
      <div style={{ marginBottom: '20px' }}>
        <button className={`btn ${activeTab === 'scan' ? 'btn-success' : ''}`} onClick={() => setActiveTab('scan')}>📱 Scan Items</button>
        <button className={`btn ${activeTab === 'cart' ? 'btn-success' : ''}`} onClick={() => setActiveTab('cart')}>🛒 Cart ({cart.length})</button>
        <button className={`btn ${activeTab === 'checkout' ? 'btn-success' : ''}`} onClick={() => setActiveTab('checkout')}>💳 Checkout</button>
        <button className={`btn ${activeTab === 'invoices' ? 'btn-success' : ''}`} onClick={() => setActiveTab('invoices')}>📄 Invoices</button>
      </div>

      {activeTab === 'scan' && (
        <div className="form-container">
          <h3>Scan/Add Items to Cart</h3>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            Scan barcodes or search by barcode to add items to cart.
          </p>
          
          <div className="form-group">
            <label>Barcode:</label>
            <div style={{ display: 'flex', gap: '10px' }}>
              <input 
                type="text" 
                value={searchBarcode} 
                onChange={(e) => setSearchBarcode(e.target.value)} 
                placeholder="Enter or scan barcode"
                style={{ flex: 1 }}
                onKeyPress={(e) => e.key === 'Enter' && searchByBarcode()}
              />
              <button onClick={searchByBarcode} className="btn btn-primary" disabled={loading}>
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>

          {searchResult && (
            <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#e8f5e8', borderRadius: '5px', border: '1px solid #28a745' }}>
              <h4>Item Found:</h4>
              <p><strong>Barcode:</strong> {searchResult.barcode}</p>
              <p><strong>Product:</strong> {searchResult.product?.name || 'Unknown'}</p>
              <p><strong>Design Number:</strong> {searchResult.design_number}</p>
              <p><strong>Size:</strong> {searchResult.size}</p>
              <p><strong>Color:</strong> {searchResult.color}</p>
              <p><strong>MRP (GST-inclusive):</strong> ₹{searchResult.mrp}</p>
              <p><strong>Available:</strong> {searchResult.quantity}</p>
              <button 
                onClick={() => addToCart(searchResult)} 
                className="btn btn-success"
                style={{ marginTop: '10px' }}
              >
                Add to Cart
              </button>
            </div>
          )}
        </div>
      )}

      {activeTab === 'cart' && (
        <div className="table-container">
          <h3>Shopping Cart</h3>
          {cart.length > 0 ? (
            <div>
              <table>
                <thead>
                  <tr>
                    <th>Barcode</th>
                    <th>Product</th>
                    <th>Design No.</th>
                    <th>Size</th>
                    <th>Color</th>
                    <th>MRP</th>
                    <th>Quantity</th>
                    <th>Total</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {cart.map((item) => (
                    <tr key={item.barcode}>
                      <td><strong>{item.barcode}</strong></td>
                      <td>{item.product?.name || 'Unknown'}</td>
                      <td>{item.design_number}</td>
                      <td>{item.size}</td>
                      <td>{item.color}</td>
                      <td>₹{item.mrp}</td>
                      <td>
                        <input 
                          type="number" 
                          value={item.quantity} 
                          onChange={(e) => updateQuantity(item.barcode, parseInt(e.target.value) || 0)}
                          min="1"
                          style={{ width: '60px', padding: '5px' }}
                        />
                      </td>
                      <td>₹{item.mrp * item.quantity}</td>
                      <td>
                        <button 
                          onClick={() => removeFromCart(item.barcode)} 
                          className="btn btn-danger"
                          style={{ padding: '5px 10px', fontSize: '12px' }}
                        >
                          Remove
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              <div style={{ marginTop: '20px', textAlign: 'right' }}>
                <button onClick={clearCart} className="btn btn-warning" style={{ marginRight: '10px' }}>
                  Clear Cart
                </button>
                <button onClick={() => setActiveTab('checkout')} className="btn btn-success">
                  Proceed to Checkout
                </button>
              </div>
            </div>
          ) : (
            <p style={{ textAlign: 'center', color: '#666', fontStyle: 'italic' }}>
              Cart is empty. Scan items to add to cart.
            </p>
          )}
        </div>
      )}

      {activeTab === 'checkout' && (
        <div className="grid">
          <div className="form-container">
            <h3>Customer Details</h3>
            <div className="form-group">
              <label>Customer Name:</label>
              <input 
                type="text" 
                value={customerName} 
                onChange={(e) => setCustomerName(e.target.value)} 
                placeholder="Enter customer name"
              />
            </div>
            <div className="form-group">
              <label>Phone Number:</label>
              <div style={{ display: 'flex', gap: '10px' }}>
                <input 
                  type="text" 
                  value={customerPhone} 
                  onChange={(e) => setCustomerPhone(e.target.value)} 
                  placeholder="Enter phone number"
                  style={{ flex: 1 }}
                  onBlur={() => lookupCustomer(customerPhone)}
                />
                <button 
                  type="button"
                  onClick={() => lookupCustomer(customerPhone)}
                  className="btn btn-primary"
                  style={{ padding: '8px 12px' }}
                >
                  🔍
                </button>
              </div>
              {customerLoyalty && (
                <div style={{ 
                  marginTop: '10px', 
                  padding: '10px', 
                  backgroundColor: '#e8f5e8', 
                  borderRadius: '4px', 
                  border: '1px solid #28a745',
                  fontSize: '14px'
                }}>
                  <strong>🎯 Customer Found:</strong> {customerLoyalty.name}
                  <br />
                  <strong>Points Available:</strong> {customerLoyalty.loyalty_points} pts
                  <br />
                  <strong>Total Spent:</strong> ₹{customerLoyalty.total_spent.toFixed(2)}
                </div>
              )}
            </div>
            <div className="form-group">
              <label>Email:</label>
              <input 
                type="email" 
                value={customerEmail} 
                onChange={(e) => setCustomerEmail(e.target.value)} 
                placeholder="Enter email address"
              />
            </div>
            
            <h3 style={{ marginTop: '30px' }}>Discount & Payment</h3>
            <div className="form-group">
              <label>Discount Type:</label>
              <select value={discountType} onChange={(e) => setDiscountType(e.target.value)}>
                <option value="PERCENT">Percentage (%)</option>
                <option value="FIXED">Fixed Amount (₹)</option>
              </select>
            </div>
            <div className="form-group">
              <label>Discount Value:</label>
              <input 
                type="number" 
                value={discountValue} 
                onChange={(e) => setDiscountValue(parseFloat(e.target.value) || 0)} 
                placeholder="0"
                min="0"
                step={discountType === 'PERCENT' ? '1' : '0.01'}
              />
            </div>
            {customerLoyalty && customerLoyalty.loyalty_points > 0 && (
              <div className="form-group">
                <label>Loyalty Points to Redeem:</label>
                <input 
                  type="number" 
                  value={loyaltyPointsRedeemed} 
                  onChange={(e) => setLoyaltyPointsRedeemed(parseInt(e.target.value) || 0)} 
                  placeholder="0"
                  min="0"
                  max={customerLoyalty.loyalty_points}
                />
                <div style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>
                  💡 Available: {customerLoyalty.loyalty_points} pts (1 point = ₹1 discount)
                </div>
              </div>
            )}
            <div className="form-group">
              <label>Payment Method:</label>
              <select value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)}>
                <option value="CASH">Cash</option>
                <option value="CARD">Card</option>
                <option value="UPI">UPI</option>
                <option value="BANK_TRANSFER">Bank Transfer</option>
              </select>
            </div>
            <div className="form-group">
              <label>Notes:</label>
              <textarea 
                value={notes} 
                onChange={(e) => setNotes(e.target.value)} 
                placeholder="Any additional notes"
                rows="3"
              />
            </div>
          </div>

          <div className="table-container">
            <h3>Order Summary</h3>
            {cart.length > 0 ? (
              <div>
                <table>
                  <thead>
                    <tr>
                      <th>Item</th>
                      <th>Size</th>
                      <th>Color</th>
                      <th>Qty</th>
                      <th>MRP</th>
                      <th>Total</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cart.map((item) => (
                      <tr key={item.barcode}>
                        <td>{item.product?.name || 'Unknown'}</td>
                        <td>{item.size}</td>
                        <td>{item.color}</td>
                        <td>{item.quantity}</td>
                        <td>₹{item.mrp}</td>
                        <td>₹{item.mrp * item.quantity}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>

                <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
                  <h4>Bill Summary (Indian Retail Billing):</h4>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                    <span>Total MRP (GST-inclusive):</span>
                    <span>₹{totalMrp.toFixed(2)}</span>
                  </div>
                  {totalDiscount > 0 && (
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px', color: '#dc3545' }}>
                      <span>Discount ({discountType === 'PERCENT' ? `${discountValue}%` : `₹${discountValue}`}):</span>
                      <span>-₹{totalDiscount.toFixed(2)}</span>
                    </div>
                  )}
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px', fontWeight: 'bold' }}>
                    <span>Final Price (GST-inclusive):</span>
                    <span>₹{totalFinalPrice.toFixed(2)}</span>
                  </div>
                  <hr style={{ margin: '10px 0' }} />
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                    <span>Base Amount (ex-GST):</span>
                    <span>₹{totalBaseAmount.toFixed(2)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                    <span>GST (12%):</span>
                    <span>₹{totalGstAmount.toFixed(2)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px', fontSize: '14px', color: '#666' }}>
                    <span>├─ CGST (6%):</span>
                    <span>₹{totalCgstAmount.toFixed(2)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px', fontSize: '14px', color: '#666' }}>
                    <span>└─ SGST (6%):</span>
                    <span>₹{totalSgstAmount.toFixed(2)}</span>
                  </div>
                  <hr style={{ margin: '10px 0' }} />
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 'bold', fontSize: '18px', color: '#28a745' }}>
                    <span>Grand Total:</span>
                    <span>₹{totalFinalPrice.toFixed(2)}</span>
                  </div>
                </div>

                <button 
                  onClick={processCheckout} 
                  className="btn btn-success" 
                  disabled={loading || cart.length === 0}
                  style={{ marginTop: '20px', width: '100%', padding: '15px', fontSize: '16px' }}
                >
                  {loading ? 'Processing...' : `Complete Checkout - ₹${totalFinalPrice.toFixed(2)}`}
                </button>
              </div>
            ) : (
              <p style={{ textAlign: 'center', color: '#666', fontStyle: 'italic' }}>
                No items in cart. Add items first.
              </p>
            )}
          </div>
        </div>
      )}

      {activeTab === 'invoices' && (
        <div className="table-container">
          <h3>Recent Invoices ({invoices.length} found)</h3>
          {invoices.length > 0 ? (
            <table>
                              <thead>
                  <tr>
                    <th>Invoice No.</th>
                    <th>Date</th>
                    <th>Customer</th>
                    <th>Items</th>
                    <th>Total MRP</th>
                    <th>Discount</th>
                    <th>Final Price</th>
                    <th>Payment</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                                <tbody>
                    {invoices.map((invoice) => (
                      <tr key={invoice.id}>
                        <td><strong>{invoice.invoice_number}</strong></td>
                        <td>{new Date(invoice.created_at).toLocaleDateString()}</td>
                        <td>{invoice.customer_name || 'Walk-in Customer'}</td>
                        <td>{invoice.items?.length || 0} items</td>
                        <td>₹{invoice.total_mrp?.toFixed(2) || '0.00'}</td>
                        <td>₹{invoice.total_discount?.toFixed(2) || '0.00'}</td>
                        <td>₹{invoice.total_final_price?.toFixed(2) || '0.00'}</td>
                        <td>{invoice.payment_method}</td>
                        <td>
                          <div style={{ display: 'flex', gap: '5px', flexWrap: 'wrap' }}>
                            <button 
                              onClick={() => printInvoice(invoice.id)}
                              className="btn btn-primary"
                              style={{ padding: '3px 8px', fontSize: '10px' }}
                            >
                              🖨️ Print
                            </button>
                            <button 
                              onClick={() => previewInvoice(invoice.id)}
                              className="btn btn-info"
                              style={{ padding: '3px 8px', fontSize: '10px' }}
                            >
                              👁️ Preview
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
              </tbody>
            </table>
          ) : (
            <p style={{ textAlign: 'center', color: '#666', fontStyle: 'italic' }}>
              No invoices found. Complete a checkout to see invoices here.
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default Checkout; 