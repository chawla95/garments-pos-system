import React, { useState, useEffect } from 'react';
import api from '../api';

const Dashboard = () => {
  const [salesData, setSalesData] = useState(null);
  const [topProducts, setTopProducts] = useState([]);
  const [inventoryAging, setInventoryAging] = useState([]);
  const [gstSummary, setGstSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [agingDays, setAgingDays] = useState(30);

  useEffect(() => {
    fetchDashboardData();
  }, [agingDays]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [salesRes, productsRes, agingRes, gstRes] = await Promise.all([
        api.get('/dashboard/sales'),
        api.get('/dashboard/top-products'),
        api.get(`/dashboard/inventory-aging?days=${agingDays}`),
        api.get('/dashboard/gst-summary')
      ]);

      setSalesData(salesRes.data);
      setTopProducts(productsRes.data);
      setInventoryAging(agingRes.data);
      setGstSummary(gstRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return `Rs. ${parseFloat(amount || 0).toFixed(2)}`;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <h3>Loading Dashboard...</h3>
      </div>
    );
  }

  return (
    <div>
      <h2>📊 Sales Dashboard</h2>
      
      {/* Sales Summary Cards */}
      {salesData && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
          <div style={{ backgroundColor: '#e3f2fd', padding: '20px', borderRadius: '8px', border: '1px solid #2196f3' }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#1976d2' }}>📅 Daily Sales</h3>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1976d2' }}>
              {formatCurrency(salesData.daily.sales)}
            </div>
            <div style={{ color: '#666', fontSize: '14px' }}>
              {salesData.daily.invoices} invoices • GST: {formatCurrency(salesData.daily.gst)}
            </div>
          </div>

          <div style={{ backgroundColor: '#f3e5f5', padding: '20px', borderRadius: '8px', border: '1px solid #9c27b0' }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#7b1fa2' }}>📈 Weekly Sales</h3>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#7b1fa2' }}>
              {formatCurrency(salesData.weekly.sales)}
            </div>
            <div style={{ color: '#666', fontSize: '14px' }}>
              {salesData.weekly.invoices} invoices • GST: {formatCurrency(salesData.weekly.gst)}
            </div>
          </div>

          <div style={{ backgroundColor: '#e8f5e8', padding: '20px', borderRadius: '8px', border: '1px solid #4caf50' }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#388e3c' }}>📊 Monthly Sales</h3>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#388e3c' }}>
              {formatCurrency(salesData.monthly.sales)}
            </div>
            <div style={{ color: '#666', fontSize: '14px' }}>
              {salesData.monthly.invoices} invoices • GST: {formatCurrency(salesData.monthly.gst)}
            </div>
          </div>
        </div>
      )}

      {/* Sales Trend Chart */}
      {salesData && salesData.trend && (
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', marginBottom: '30px', border: '1px solid #ddd' }}>
          <h3>📈 Sales Trend (Last 7 Days)</h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f5f5f5' }}>
                  <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Date</th>
                  <th style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>Sales</th>
                  <th style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>GST</th>
                  <th style={{ padding: '10px', textAlign: 'center', border: '1px solid #ddd' }}>Invoices</th>
                </tr>
              </thead>
              <tbody>
                {salesData.trend.map((day, index) => (
                  <tr key={index} style={{ backgroundColor: index % 2 === 0 ? '#fafafa' : 'white' }}>
                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>{formatDate(day.date)}</td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd', fontWeight: 'bold' }}>
                      {formatCurrency(day.sales)}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                      {formatCurrency(day.gst)}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'center', border: '1px solid #ddd' }}>
                      {day.invoices}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* GST Summary */}
      {gstSummary && (
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', marginBottom: '30px', border: '1px solid #ddd' }}>
          <h3>💰 GST Collection Summary</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
            <div>
              <h4 style={{ color: '#1976d2', margin: '0 0 10px 0' }}>Daily GST</h4>
              <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{formatCurrency(gstSummary.daily.total)}</div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                CGST: {formatCurrency(gstSummary.daily.cgst)} • SGST: {formatCurrency(gstSummary.daily.sgst)}
              </div>
            </div>
            <div>
              <h4 style={{ color: '#7b1fa2', margin: '0 0 10px 0' }}>Weekly GST</h4>
              <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{formatCurrency(gstSummary.weekly.total)}</div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                CGST: {formatCurrency(gstSummary.weekly.cgst)} • SGST: {formatCurrency(gstSummary.weekly.sgst)}
              </div>
            </div>
            <div>
              <h4 style={{ color: '#388e3c', margin: '0 0 10px 0' }}>Monthly GST</h4>
              <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{formatCurrency(gstSummary.monthly.total)}</div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                CGST: {formatCurrency(gstSummary.monthly.cgst)} • SGST: {formatCurrency(gstSummary.monthly.sgst)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Top Products */}
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', marginBottom: '30px', border: '1px solid #ddd' }}>
        <h3>🏆 Top 10 Selling Products</h3>
        {topProducts.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f5f5f5' }}>
                  <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Rank</th>
                  <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Product</th>
                  <th style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>Quantity Sold</th>
                  <th style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>Revenue</th>
                  <th style={{ padding: '10px', textAlign: 'center', border: '1px solid #ddd' }}>Times Sold</th>
                </tr>
              </thead>
              <tbody>
                {topProducts.map((product, index) => (
                  <tr key={product.product_id} style={{ backgroundColor: index % 2 === 0 ? '#fafafa' : 'white' }}>
                    <td style={{ padding: '10px', border: '1px solid #ddd', fontWeight: 'bold' }}>
                      #{index + 1}
                    </td>
                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                      {product.product_name}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd', fontWeight: 'bold' }}>
                      {product.total_quantity}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                      {formatCurrency(product.total_revenue)}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'center', border: '1px solid #ddd' }}>
                      {product.times_sold}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ textAlign: 'center', color: '#666', fontStyle: 'italic' }}>
            No sales data available yet.
          </p>
        )}
      </div>

      {/* Inventory Aging */}
      <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #ddd' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h3>📦 Inventory Aging</h3>
          <div>
            <label style={{ marginRight: '10px' }}>Not sold in past:</label>
            <select 
              value={agingDays} 
              onChange={(e) => setAgingDays(parseInt(e.target.value))}
              style={{ padding: '5px', borderRadius: '4px', border: '1px solid #ddd' }}
            >
              <option value={7}>7 days</option>
              <option value={15}>15 days</option>
              <option value={30}>30 days</option>
              <option value={60}>60 days</option>
              <option value={90}>90 days</option>
            </select>
          </div>
        </div>
        
        {inventoryAging.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f5f5f5' }}>
                  <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Product</th>
                  <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Design No.</th>
                  <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Size</th>
                  <th style={{ padding: '10px', textAlign: 'left', border: '1px solid #ddd' }}>Color</th>
                  <th style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>MRP</th>
                  <th style={{ padding: '10px', textAlign: 'center', border: '1px solid #ddd' }}>Quantity</th>
                  <th style={{ padding: '10px', textAlign: 'center', border: '1px solid #ddd' }}>Days Old</th>
                </tr>
              </thead>
              <tbody>
                {inventoryAging.map((item, index) => (
                  <tr key={item.id} style={{ backgroundColor: index % 2 === 0 ? '#fafafa' : 'white' }}>
                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                      {item.product_name}
                    </td>
                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                      {item.design_number}
                    </td>
                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                      {item.size}
                    </td>
                    <td style={{ padding: '10px', border: '1px solid #ddd' }}>
                      {item.color}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'right', border: '1px solid #ddd' }}>
                      {formatCurrency(item.mrp)}
                    </td>
                    <td style={{ padding: '10px', textAlign: 'center', border: '1px solid #ddd' }}>
                      {item.quantity}
                    </td>
                    <td style={{ 
                      padding: '10px', 
                      textAlign: 'center', 
                      border: '1px solid #ddd',
                      color: item.days_old > 60 ? '#d32f2f' : item.days_old > 30 ? '#f57c00' : '#388e3c',
                      fontWeight: 'bold'
                    }}>
                      {item.days_old} days
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p style={{ textAlign: 'center', color: '#666', fontStyle: 'italic' }}>
            No aging inventory found for the selected period.
          </p>
        )}
      </div>
    </div>
  );
};

export default Dashboard; 