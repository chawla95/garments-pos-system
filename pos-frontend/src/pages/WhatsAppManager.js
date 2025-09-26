import React, { useState, useEffect } from 'react';
import api from '../api';

const WhatsAppManager = () => {
  const [templates, setTemplates] = useState([]);
  const [logs, setLogs] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('templates');
  
  // Template form state
  const [templateForm, setTemplateForm] = useState({
    name: '',
    template_type: 'CUSTOM',
    message_template: '',
    variables: '',
    is_active: true
  });
  
  // Message form state
  const [messageForm, setMessageForm] = useState({
    phone_number: '',
    message: '',
    customer_id: null
  });
  
  // Broadcast form state
  const [broadcastForm, setBroadcastForm] = useState({
    template_id: '',
    message: '',
    customer_ids: [],
    include_pdf: false
  });

  useEffect(() => {
    fetchTemplates();
    fetchLogs();
    fetchCustomers();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await api.get('/whatsapp/templates/');
      setTemplates(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error fetching templates');
    } finally {
      setLoading(false);
    }
  };

  const fetchLogs = async () => {
    try {
      const response = await api.get('/whatsapp/logs/');
      setLogs(response.data);
    } catch (err) {
      console.error('Error fetching logs:', err);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/customers/');
      setCustomers(response.data);
    } catch (err) {
      console.error('Error fetching customers:', err);
    }
  };

  const handleTemplateSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError('');
      
      if (templateForm.id) {
        // Update existing template
        await api.put(`/whatsapp/templates/${templateForm.id}`, templateForm);
      } else {
        // Create new template
        await api.post('/whatsapp/templates/', templateForm);
      }
      
      setTemplateForm({
        name: '',
        template_type: 'CUSTOM',
        message_template: '',
        variables: '',
        is_active: true
      });
      
      fetchTemplates();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error saving template');
    } finally {
      setLoading(false);
    }
  };

  const handleMessageSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError('');
      
      await api.post('/whatsapp/send-message', {
        phone_number: messageForm.phone_number,
        message: messageForm.message,
        customer_id: messageForm.customer_id
      });
      
      setMessageForm({
        phone_number: '',
        message: '',
        customer_id: null
      });
      
      fetchLogs();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error sending message');
    } finally {
      setLoading(false);
    }
  };

  const handleBroadcastSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError('');
      
      await api.post('/whatsapp/broadcast', broadcastForm);
      
      setBroadcastForm({
        template_id: '',
        message: '',
        customer_ids: [],
        include_pdf: false
      });
      
      fetchLogs();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error sending broadcast');
    } finally {
      setLoading(false);
    }
  };

  const deleteTemplate = async (templateId) => {
    if (!window.confirm('Are you sure you want to delete this template?')) {
      return;
    }
    
    try {
      setLoading(true);
      setError('');
      
      await api.delete(`/whatsapp/templates/${templateId}`);
      fetchTemplates();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error deleting template');
    } finally {
      setLoading(false);
    }
  };

  const editTemplate = (template) => {
    setTemplateForm({
      id: template.id,
      name: template.name,
      template_type: template.template_type,
      message_template: template.message_template,
      variables: template.variables || '',
      is_active: template.is_active
    });
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'SENT':
        return '#4caf50';
      case 'DELIVERED':
        return '#2196f3';
      case 'FAILED':
        return '#f44336';
      case 'PENDING':
        return '#ff9800';
      default:
        return '#666';
    }
  };

  if (loading && templates.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <h3>📱 Loading WhatsApp Manager...</h3>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '30px', color: '#333' }}>
        📱 WhatsApp Messaging Manager
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
          className={`btn ${activeTab === 'templates' ? 'btn-success' : ''}`}
          onClick={() => setActiveTab('templates')}
        >
          📝 Templates
        </button>
        <button
          className={`btn ${activeTab === 'send' ? 'btn-success' : ''}`}
          onClick={() => setActiveTab('send')}
        >
          💬 Send Message
        </button>
        <button
          className={`btn ${activeTab === 'broadcast' ? 'btn-success' : ''}`}
          onClick={() => setActiveTab('broadcast')}
        >
          📢 Broadcast
        </button>
        <button
          className={`btn ${activeTab === 'logs' ? 'btn-success' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          📋 Message Logs
        </button>
      </div>

      {/* Templates Tab */}
      {activeTab === 'templates' && (
        <div>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>📝 Message Templates</h3>
          
          {/* Template Form */}
          <div style={{ 
            backgroundColor: '#f5f5f5', 
            padding: '20px', 
            borderRadius: '8px',
            border: '1px solid #ddd',
            marginBottom: '20px'
          }}>
            <h4 style={{ marginBottom: '15px', color: '#333' }}>
              {templateForm.id ? 'Edit Template' : 'Create New Template'}
            </h4>
            
            <form onSubmit={handleTemplateSubmit}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '15px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    Template Name:
                  </label>
                  <input
                    type="text"
                    value={templateForm.name}
                    onChange={(e) => setTemplateForm({...templateForm, name: e.target.value})}
                    required
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    Template Type:
                  </label>
                  <select
                    value={templateForm.template_type}
                    onChange={(e) => setTemplateForm({...templateForm, template_type: e.target.value})}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  >
                    <option value="CUSTOM">Custom Message</option>
                    <option value="INVOICE">Invoice Summary</option>
                    <option value="THANK_YOU">Thank You</option>
                    <option value="BROADCAST">Broadcast</option>
                  </select>
                </div>
              </div>
              
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Message Template:
                </label>
                <textarea
                  value={templateForm.message_template}
                  onChange={(e) => setTemplateForm({...templateForm, message_template: e.target.value})}
                  required
                  rows={4}
                  placeholder="Enter your message template. Use {customer_name}, {total_spent}, etc. for variables."
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    resize: 'vertical'
                  }}
                />
              </div>
              
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Available Variables (JSON):
                </label>
                <input
                  type="text"
                  value={templateForm.variables}
                  onChange={(e) => setTemplateForm({...templateForm, variables: e.target.value})}
                  placeholder='{"customer_name": "string", "total_spent": "number"}'
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                />
              </div>
              
              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    padding: '10px 20px',
                    backgroundColor: '#4caf50',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: loading ? 'not-allowed' : 'pointer'
                  }}
                >
                  {loading ? 'Saving...' : (templateForm.id ? 'Update Template' : 'Create Template')}
                </button>
                
                {templateForm.id && (
                  <button
                    type="button"
                    onClick={() => setTemplateForm({
                      name: '',
                      template_type: 'CUSTOM',
                      message_template: '',
                      variables: '',
                      is_active: true
                    })}
                    style={{
                      padding: '10px 20px',
                      backgroundColor: '#ff9800',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    Cancel Edit
                  </button>
                )}
              </div>
            </form>
          </div>
          
          {/* Templates List */}
          <div style={{ 
            backgroundColor: '#f5f5f5', 
            padding: '15px', 
            borderRadius: '8px',
            border: '1px solid #ddd'
          }}>
            <h4 style={{ marginBottom: '15px', color: '#333' }}>Existing Templates</h4>
            
            {templates.length > 0 ? (
              <div style={{ display: 'grid', gap: '10px' }}>
                {templates.map((template) => (
                  <div key={template.id} style={{ 
                    padding: '15px', 
                    backgroundColor: 'white',
                    borderRadius: '8px',
                    border: '1px solid #ddd'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div style={{ flex: 1 }}>
                        <h5 style={{ margin: '0 0 10px 0', color: '#333' }}>
                          {template.name}
                          <span style={{ 
                            marginLeft: '10px',
                            padding: '2px 8px',
                            backgroundColor: template.is_active ? '#4caf50' : '#f44336',
                            color: 'white',
                            borderRadius: '12px',
                            fontSize: '12px'
                          }}>
                            {template.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </h5>
                        <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
                          Type: {template.template_type}
                        </div>
                        <div style={{ 
                          backgroundColor: '#f8f9fa',
                          padding: '10px',
                          borderRadius: '4px',
                          fontSize: '14px',
                          whiteSpace: 'pre-wrap'
                        }}>
                          {template.message_template}
                        </div>
                      </div>
                      
                      <div style={{ display: 'flex', gap: '5px' }}>
                        <button
                          onClick={() => editTemplate(template)}
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
                          Edit
                        </button>
                        <button
                          onClick={() => deleteTemplate(template.id)}
                          style={{
                            padding: '5px 10px',
                            backgroundColor: '#f44336',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '12px'
                          }}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
                No templates found. Create your first template above.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Send Message Tab */}
      {activeTab === 'send' && (
        <div>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>💬 Send WhatsApp Message</h3>
          
          <div style={{ 
            backgroundColor: '#f5f5f5', 
            padding: '20px', 
            borderRadius: '8px',
            border: '1px solid #ddd'
          }}>
            <form onSubmit={handleMessageSubmit}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '15px' }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    Phone Number:
                  </label>
                  <input
                    type="text"
                    value={messageForm.phone_number}
                    onChange={(e) => setMessageForm({...messageForm, phone_number: e.target.value})}
                    placeholder="Enter phone number (e.g., 9876543210)"
                    required
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                    Customer (Optional):
                  </label>
                  <select
                    value={messageForm.customer_id || ''}
                    onChange={(e) => setMessageForm({...messageForm, customer_id: e.target.value ? parseInt(e.target.value) : null})}
                    style={{
                      width: '100%',
                      padding: '8px',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  >
                    <option value="">Select Customer</option>
                    {customers.map((customer) => (
                      <option key={customer.id} value={customer.id}>
                        {customer.name || 'Anonymous'} - {customer.phone}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Message:
                </label>
                <textarea
                  value={messageForm.message}
                  onChange={(e) => setMessageForm({...messageForm, message: e.target.value})}
                  required
                  rows={4}
                  placeholder="Enter your WhatsApp message..."
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    resize: 'vertical'
                  }}
                />
              </div>
              
              <button
                type="submit"
                disabled={loading}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#4caf50',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Sending...' : 'Send Message'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Broadcast Tab */}
      {activeTab === 'broadcast' && (
        <div>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>📢 Send Broadcast Message</h3>
          
          <div style={{ 
            backgroundColor: '#f5f5f5', 
            padding: '20px', 
            borderRadius: '8px',
            border: '1px solid #ddd'
          }}>
            <form onSubmit={handleBroadcastSubmit}>
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Template:
                </label>
                <select
                  value={broadcastForm.template_id}
                  onChange={(e) => setBroadcastForm({...broadcastForm, template_id: parseInt(e.target.value)})}
                  required
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px'
                  }}
                >
                  <option value="">Select Template</option>
                  {templates.filter(t => t.is_active).map((template) => (
                    <option key={template.id} value={template.id}>
                      {template.name} ({template.template_type})
                    </option>
                  ))}
                </select>
              </div>
              
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Message:
                </label>
                <textarea
                  value={broadcastForm.message}
                  onChange={(e) => setBroadcastForm({...broadcastForm, message: e.target.value})}
                  required
                  rows={4}
                  placeholder="Enter your broadcast message. Use {customer_name}, {total_spent}, etc. for variables."
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    resize: 'vertical'
                  }}
                />
              </div>
              
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <input
                    type="checkbox"
                    checked={broadcastForm.include_pdf}
                    onChange={(e) => setBroadcastForm({...broadcastForm, include_pdf: e.target.checked})}
                  />
                  Include PDF attachment (if available)
                </label>
              </div>
              
              <div style={{ marginBottom: '15px' }}>
                <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                  Target Customers:
                </label>
                <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
                  Leave empty to send to top 50 customers by spending
                </div>
                <select
                  multiple
                  value={broadcastForm.customer_ids}
                  onChange={(e) => {
                    const selected = Array.from(e.target.selectedOptions, option => parseInt(option.value));
                    setBroadcastForm({...broadcastForm, customer_ids: selected});
                  }}
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    minHeight: '100px'
                  }}
                >
                  {customers.map((customer) => (
                    <option key={customer.id} value={customer.id}>
                      {customer.name || 'Anonymous'} - {customer.phone} (₹{customer.total_spent})
                    </option>
                  ))}
                </select>
              </div>
              
              <button
                type="submit"
                disabled={loading}
                style={{
                  padding: '10px 20px',
                  backgroundColor: '#ff9800',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: loading ? 'not-allowed' : 'pointer'
                }}
              >
                {loading ? 'Sending Broadcast...' : 'Send Broadcast'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Logs Tab */}
      {activeTab === 'logs' && (
        <div>
          <h3 style={{ marginBottom: '20px', color: '#333' }}>📋 Message Logs</h3>
          
          <div style={{ 
            backgroundColor: '#f5f5f5', 
            padding: '15px', 
            borderRadius: '8px',
            border: '1px solid #ddd',
            maxHeight: '600px',
            overflow: 'auto'
          }}>
            {logs.length > 0 ? (
              <div style={{ display: 'grid', gap: '10px' }}>
                {logs.map((log) => (
                  <div key={log.id} style={{ 
                    padding: '15px', 
                    backgroundColor: 'white',
                    borderRadius: '8px',
                    border: '1px solid #ddd'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                          <span style={{ 
                            padding: '2px 8px',
                            backgroundColor: getStatusColor(log.status),
                            color: 'white',
                            borderRadius: '12px',
                            fontSize: '12px',
                            fontWeight: 'bold'
                          }}>
                            {log.status}
                          </span>
                          <span style={{ fontSize: '14px', color: '#666' }}>
                            {log.message_type}
                          </span>
                          <span style={{ fontSize: '14px', color: '#666' }}>
                            {log.phone_number}
                          </span>
                        </div>
                        
                        <div style={{ 
                          backgroundColor: '#f8f9fa',
                          padding: '10px',
                          borderRadius: '4px',
                          fontSize: '14px',
                          whiteSpace: 'pre-wrap',
                          marginBottom: '10px'
                        }}>
                          {log.message_content}
                        </div>
                        
                        <div style={{ fontSize: '12px', color: '#666' }}>
                          Sent: {formatDate(log.sent_at)}
                          {log.error_message && (
                            <div style={{ color: '#f44336', marginTop: '5px' }}>
                              Error: {log.error_message}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', color: '#666', padding: '20px' }}>
                No message logs found.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default WhatsAppManager; 