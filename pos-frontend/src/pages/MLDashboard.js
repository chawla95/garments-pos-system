import React, { useState, useEffect } from 'react';
import api from '../api';

const MLDashboard = () => {
  const [stockAlerts, setStockAlerts] = useState(null);
  const [reorderSuggestions, setReorderSuggestions] = useState(null);
  const [inventoryAnalysis, setInventoryAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchMLData();
  }, []);

  const fetchMLData = async () => {
    try {
      setLoading(true);
      setError('');

      // Fetch all ML data in parallel
      const [alertsRes, suggestionsRes, analysisRes] = await Promise.all([
        api.get('/ml/stock-alerts'),
        api.get('/ml/reorder-suggestions'),
        api.get('/ml/inventory-analysis')
      ]);

      setStockAlerts(alertsRes.data);
      setReorderSuggestions(suggestionsRes.data);
      setInventoryAnalysis(analysisRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error fetching ML data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'DEADSTOCK': return '#f44336';
      case 'SLOW_MOVING': return '#ff9800';
      case 'OUT_OF_STOCK': return '#e91e63';
      case 'NORMAL': return '#4caf50';
      default: return '#757575';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'DEADSTOCK': return '💀';
      case 'SLOW_MOVING': return '🐌';
      case 'OUT_OF_STOCK': return '❌';
      case 'NORMAL': return '✅';
      default: return '❓';
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <h3>🤖 Loading ML Analysis...</h3>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '50px', color: '#f44336' }}>
        <h3>❌ Error</h3>
        <p>{error}</p>
        <button 
          onClick={fetchMLData}
          style={{
            padding: '10px 20px',
            backgroundColor: '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          🔄 Retry
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
        🤖 ML Inventory Intelligence
      </h2>

      {/* Summary Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
        gap: '20px', 
        marginBottom: '30px' 
      }}>
        <div style={{
          backgroundColor: '#ffebee',
          padding: '20px',
          borderRadius: '8px',
          border: '1px solid #f44336'
        }}>
          <h3 style={{ color: '#f44336', margin: '0 0 10px 0' }}>
            💀 Deadstock Items
          </h3>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f44336' }}>
            {stockAlerts?.deadstock?.count || 0}
          </div>
          <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#666' }}>
            Items unsold for > 60 days
          </p>
        </div>

        <div style={{
          backgroundColor: '#fff3e0',
          padding: '20px',
          borderRadius: '8px',
          border: '1px solid #ff9800'
        }}>
          <h3 style={{ color: '#ff9800', margin: '0 0 10px 0' }}>
            🐌 Slow Moving Items
          </h3>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ff9800' }}>
            {stockAlerts?.slow_moving?.count || 0}
          </div>
          <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#666' }}>
            Items unsold for > 30 days
          </p>
        </div>

        <div style={{
          backgroundColor: '#fce4ec',
          padding: '20px',
          borderRadius: '8px',
          border: '1px solid #e91e63'
        }}>
          <h3 style={{ color: '#e91e63', margin: '0 0 10px 0' }}>
            ❌ Out of Stock
          </h3>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#e91e63' }}>
            {stockAlerts?.out_of_stock?.count || 0}
          </div>
          <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#666' }}>
            Items with zero inventory
          </p>
        </div>

        <div style={{
          backgroundColor: '#e8f5e8',
          padding: '20px',
          borderRadius: '8px',
          border: '1px solid #4caf50'
        }}>
          <h3 style={{ color: '#4caf50', margin: '0 0 10px 0' }}>
            📦 Reorder Suggestions
          </h3>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#4caf50' }}>
            {reorderSuggestions?.total_suggestions || 0}
          </div>
          <p style={{ margin: '5px 0 0 0', fontSize: '14px', color: '#666' }}>
            Items needing restock
          </p>
        </div>
      </div>

      {/* Stock Alerts */}
      <div style={{ marginBottom: '30px' }}>
        <h3 style={{ marginBottom: '20px', color: '#333' }}>🚨 Stock Alerts</h3>
        
        {/* Deadstock Items */}
        {stockAlerts?.deadstock?.items?.length > 0 && (
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ color: '#f44336', marginBottom: '10px' }}>💀 Deadstock Items</h4>
            <div style={{ 
              backgroundColor: '#ffebee', 
              padding: '15px', 
              borderRadius: '8px',
              border: '1px solid #f44336'
            }}>
              {stockAlerts.deadstock.items.map((item, index) => (
                <div key={index} style={{ 
                  padding: '10px', 
                  marginBottom: '10px', 
                  backgroundColor: 'white',
                  borderRadius: '4px',
                  border: '1px solid #f44336'
                }}>
                  <strong>{item.product_name}</strong>
                  <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
                    Current Stock: {item.current_inventory} | 
                    Days Since Last Sale: {item.days_since_last_sale || 'Never'} |
                    Total Sales: {item.total_sales}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Slow Moving Items */}
        {stockAlerts?.slow_moving?.items?.length > 0 && (
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ color: '#ff9800', marginBottom: '10px' }}>🐌 Slow Moving Items</h4>
            <div style={{ 
              backgroundColor: '#fff3e0', 
              padding: '15px', 
              borderRadius: '8px',
              border: '1px solid #ff9800'
            }}>
              {stockAlerts.slow_moving.items.map((item, index) => (
                <div key={index} style={{ 
                  padding: '10px', 
                  marginBottom: '10px', 
                  backgroundColor: 'white',
                  borderRadius: '4px',
                  border: '1px solid #ff9800'
                }}>
                  <strong>{item.product_name}</strong>
                  <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
                    Current Stock: {item.current_inventory} | 
                    Days Since Last Sale: {item.days_since_last_sale || 'Never'} |
                    Avg Daily Sales: {item.avg_daily_sales}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Out of Stock Items */}
        {stockAlerts?.out_of_stock?.items?.length > 0 && (
          <div style={{ marginBottom: '20px' }}>
            <h4 style={{ color: '#e91e63', marginBottom: '10px' }}>❌ Out of Stock Items</h4>
            <div style={{ 
              backgroundColor: '#fce4ec', 
              padding: '15px', 
              borderRadius: '8px',
              border: '1px solid #e91e63'
            }}>
              {stockAlerts.out_of_stock.items.map((item, index) => (
                <div key={index} style={{ 
                  padding: '10px', 
                  marginBottom: '10px', 
                  backgroundColor: 'white',
                  borderRadius: '4px',
                  border: '1px solid #e91e63'
                }}>
                  <strong>{item.product_name}</strong>
                  <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
                    Current Stock: {item.current_inventory} | 
                    Total Sales: {item.total_sales} |
                    Avg Daily Sales: {item.avg_daily_sales}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {(!stockAlerts?.deadstock?.items?.length && 
          !stockAlerts?.slow_moving?.items?.length && 
          !stockAlerts?.out_of_stock?.items?.length) && (
          <div style={{ 
            textAlign: 'center', 
            padding: '40px', 
            backgroundColor: '#e8f5e8',
            borderRadius: '8px',
            border: '1px solid #4caf50'
          }}>
            <h4 style={{ color: '#4caf50', marginBottom: '10px' }}>✅ All Good!</h4>
            <p style={{ color: '#666' }}>No stock alerts at this time.</p>
          </div>
        )}
      </div>

      {/* Reorder Suggestions */}
      {reorderSuggestions?.suggestions?.length > 0 && (
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>📦 Reorder Suggestions</h3>
          <div style={{ 
            backgroundColor: '#e8f5e8', 
            padding: '15px', 
            borderRadius: '8px',
            border: '1px solid #4caf50'
          }}>
            {reorderSuggestions.suggestions.map((suggestion, index) => (
              <div key={index} style={{ 
                padding: '15px', 
                marginBottom: '15px', 
                backgroundColor: 'white',
                borderRadius: '8px',
                border: '1px solid #4caf50'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong style={{ fontSize: '16px' }}>{suggestion.product_name}</strong>
                    <div style={{ fontSize: '14px', color: '#666', marginTop: '5px' }}>
                      Current Stock: {suggestion.current_inventory} | 
                      Suggested Order: {suggestion.reorder_quantity} | 
                      Avg Forecast Demand: {suggestion.avg_forecast_demand}/day
                    </div>
                  </div>
                  <div style={{ 
                    backgroundColor: '#4caf50', 
                    color: 'white', 
                    padding: '8px 16px',
                    borderRadius: '4px',
                    fontSize: '14px'
                  }}>
                    📋 Reorder
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ML Insights */}
      <div style={{ marginBottom: '30px' }}>
        <h3 style={{ marginBottom: '20px', color: '#333' }}>🧠 ML Insights</h3>
        <div style={{ 
          backgroundColor: '#f5f5f5', 
          padding: '20px', 
          borderRadius: '8px',
          border: '1px solid #ddd'
        }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
            <div>
              <h4 style={{ marginBottom: '10px', color: '#333' }}>📊 Analysis Summary</h4>
              <p style={{ margin: '5px 0', fontSize: '14px' }}>
                <strong>Total Products Analyzed:</strong> {inventoryAnalysis?.total_products || 0}
              </p>
              <p style={{ margin: '5px 0', fontSize: '14px' }}>
                <strong>Models Trained:</strong> {inventoryAnalysis?.products_analyzed?.filter(p => p.model_trained).length || 0}
              </p>
              <p style={{ margin: '5px 0', fontSize: '14px' }}>
                <strong>Forecasting Available:</strong> {inventoryAnalysis?.products_analyzed?.filter(p => p.forecast_30d?.length > 0).length || 0}
              </p>
            </div>
            
            <div>
              <h4 style={{ marginBottom: '10px', color: '#333' }}>🎯 Recommendations</h4>
              <p style={{ margin: '5px 0', fontSize: '14px' }}>
                • Monitor deadstock items for clearance opportunities
              </p>
              <p style={{ margin: '5px 0', fontSize: '14px' }}>
                • Consider promotions for slow-moving items
              </p>
              <p style={{ margin: '5px 0', fontSize: '14px' }}>
                • Reorder suggested quantities to maintain optimal stock levels
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Refresh Button */}
      <div style={{ textAlign: 'center' }}>
        <button 
          onClick={fetchMLData}
          style={{
            padding: '12px 24px',
            backgroundColor: '#2196F3',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          🔄 Refresh ML Analysis
        </button>
      </div>
    </div>
  );
};

export default MLDashboard; 