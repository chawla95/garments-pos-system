import React, { useState, useEffect } from 'react';
import api from '../api';
import './ConfigManager.css';

const ConfigManager = () => {
  const [activeTab, setActiveTab] = useState('whatsapp');
  const [whatsappConfig, setWhatsappConfig] = useState({});
  const [shopConfig, setShopConfig] = useState({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // WhatsApp form state
  const [whatsappForm, setWhatsappForm] = useState({
    api_key: '',
    api_secret: '',
    phone_number_id: '',
    business_account_id: ''
  });

  // Shop form state
  const [shopForm, setShopForm] = useState({
    shop_name: '',
    shop_address: '',
    shop_phone: '',
    shop_email: '',
    shop_gstin: ''
  });

  useEffect(() => {
    loadConfigurations();
  }, []);

  const loadConfigurations = async () => {
    setLoading(true);
    try {
      // Load WhatsApp config
      const whatsappResponse = await api.get('/config/whatsapp');
      setWhatsappConfig(whatsappResponse.data);

      // Load shop config
      const shopResponse = await api.get('/config/shop');
      setShopConfig(shopResponse.data);
      setShopForm(shopResponse.data);
    } catch (error) {
      console.error('Error loading configurations:', error);
      setMessage('Error loading configurations');
    } finally {
      setLoading(false);
    }
  };

  const handleWhatsappSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.post('/config/whatsapp', whatsappForm);
      setMessage('WhatsApp configuration updated successfully');
      loadConfigurations();
    } catch (error) {
      console.error('Error updating WhatsApp config:', error);
      setMessage('Error updating WhatsApp configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleShopSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await api.post('/config/shop', shopForm);
      setMessage('Shop configuration updated successfully');
      loadConfigurations();
    } catch (error) {
      console.error('Error updating shop config:', error);
      setMessage('Error updating shop configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleWhatsappInputChange = (e) => {
    setWhatsappForm({
      ...whatsappForm,
      [e.target.name]: e.target.value
    });
  };

  const handleShopInputChange = (e) => {
    setShopForm({
      ...shopForm,
      [e.target.name]: e.target.value
    });
  };

  if (loading) {
    return <div className="loading">Loading Configuration Manager...</div>;
  }

  return (
    <div className="config-manager">
      <div className="config-header">
        <h2>⚙️ System Configuration</h2>
      </div>

      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      <div className="config-tabs">
        <button
          className={`tab ${activeTab === 'whatsapp' ? 'active' : ''}`}
          onClick={() => setActiveTab('whatsapp')}
        >
          📱 WhatsApp Configuration
        </button>
        <button
          className={`tab ${activeTab === 'shop' ? 'active' : ''}`}
          onClick={() => setActiveTab('shop')}
        >
          🏪 Shop Configuration
        </button>
      </div>

      <div className="config-content">
        {activeTab === 'whatsapp' && (
          <div className="whatsapp-config">
            <div className="config-status">
              <h3>WhatsApp Business API Status</h3>
              <div className="status-grid">
                <div className={`status-item ${whatsappConfig.configured ? 'success' : 'error'}`}>
                  <span>Configuration Status:</span>
                  <strong>{whatsappConfig.configured ? '✅ Configured' : '❌ Not Configured'}</strong>
                </div>
                <div className={`status-item ${whatsappConfig.enabled ? 'success' : 'error'}`}>
                  <span>WhatsApp Enabled:</span>
                  <strong>{whatsappConfig.enabled ? '✅ Enabled' : '❌ Disabled'}</strong>
                </div>
                <div className={`status-item ${whatsappConfig.has_api_key ? 'success' : 'error'}`}>
                  <span>API Key:</span>
                  <strong>{whatsappConfig.has_api_key ? '✅ Set' : '❌ Missing'}</strong>
                </div>
                <div className={`status-item ${whatsappConfig.has_api_secret ? 'success' : 'error'}`}>
                  <span>API Secret:</span>
                  <strong>{whatsappConfig.has_api_secret ? '✅ Set' : '❌ Missing'}</strong>
                </div>
                <div className={`status-item ${whatsappConfig.has_phone_number_id ? 'success' : 'error'}`}>
                  <span>Phone Number ID:</span>
                  <strong>{whatsappConfig.has_phone_number_id ? '✅ Set' : '❌ Missing'}</strong>
                </div>
                <div className={`status-item ${whatsappConfig.has_business_account_id ? 'success' : 'error'}`}>
                  <span>Business Account ID:</span>
                  <strong>{whatsappConfig.has_business_account_id ? '✅ Set' : '❌ Missing'}</strong>
                </div>
              </div>
            </div>

            <div className="config-form">
              <h3>Configure WhatsApp Business API</h3>
              <p className="help-text">
                To enable WhatsApp messaging, you need to set up a WhatsApp Business API account with Interakt.
                <br />
                <strong>Steps to get your credentials:</strong>
                <br />
                1. Sign up at <a href="https://interakt.ai" target="_blank" rel="noopener noreferrer">interakt.ai</a>
                <br />
                2. Create a WhatsApp Business API account
                <br />
                3. Get your API credentials from the dashboard
                <br />
                4. Enter them below
              </p>

              <form onSubmit={handleWhatsappSubmit}>
                <div className="form-group">
                  <label htmlFor="api_key">API Key *</label>
                  <input
                    type="password"
                    id="api_key"
                    name="api_key"
                    value={whatsappForm.api_key}
                    onChange={handleWhatsappInputChange}
                    placeholder="Enter your Interakt API Key"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="api_secret">API Secret *</label>
                  <input
                    type="password"
                    id="api_secret"
                    name="api_secret"
                    value={whatsappForm.api_secret}
                    onChange={handleWhatsappInputChange}
                    placeholder="Enter your Interakt API Secret"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="phone_number_id">Phone Number ID *</label>
                  <input
                    type="text"
                    id="phone_number_id"
                    name="phone_number_id"
                    value={whatsappForm.phone_number_id}
                    onChange={handleWhatsappInputChange}
                    placeholder="Enter your WhatsApp Phone Number ID"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="business_account_id">Business Account ID *</label>
                  <input
                    type="text"
                    id="business_account_id"
                    name="business_account_id"
                    value={whatsappForm.business_account_id}
                    onChange={handleWhatsappInputChange}
                    placeholder="Enter your Business Account ID"
                    required
                  />
                </div>

                <button type="submit" className="save-btn" disabled={loading}>
                  {loading ? 'Saving...' : 'Save WhatsApp Configuration'}
                </button>
              </form>
            </div>
          </div>
        )}

        {activeTab === 'shop' && (
          <div className="shop-config">
            <div className="config-form">
              <h3>Shop Information</h3>
              <p className="help-text">
                Update your shop details that will appear on invoices and receipts.
              </p>

              <form onSubmit={handleShopSubmit}>
                <div className="form-group">
                  <label htmlFor="shop_name">Shop Name *</label>
                  <input
                    type="text"
                    id="shop_name"
                    name="shop_name"
                    value={shopForm.shop_name}
                    onChange={handleShopInputChange}
                    placeholder="Enter your shop name"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="shop_address">Shop Address *</label>
                  <textarea
                    id="shop_address"
                    name="shop_address"
                    value={shopForm.shop_address}
                    onChange={handleShopInputChange}
                    placeholder="Enter your complete shop address"
                    required
                    rows="3"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="shop_phone">Shop Phone *</label>
                  <input
                    type="tel"
                    id="shop_phone"
                    name="shop_phone"
                    value={shopForm.shop_phone}
                    onChange={handleShopInputChange}
                    placeholder="Enter your shop phone number"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="shop_email">Shop Email</label>
                  <input
                    type="email"
                    id="shop_email"
                    name="shop_email"
                    value={shopForm.shop_email}
                    onChange={handleShopInputChange}
                    placeholder="Enter your shop email"
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="shop_gstin">GSTIN *</label>
                  <input
                    type="text"
                    id="shop_gstin"
                    name="shop_gstin"
                    value={shopForm.shop_gstin}
                    onChange={handleShopInputChange}
                    placeholder="Enter your GSTIN (e.g., 22AAAAA0000A1Z5)"
                    required
                  />
                </div>

                <button type="submit" className="save-btn" disabled={loading}>
                  {loading ? 'Saving...' : 'Save Shop Configuration'}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConfigManager; 