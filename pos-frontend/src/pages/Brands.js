import React, { useState, useEffect } from 'react';
import api from '../api';

const Brands = () => {
  const [brands, setBrands] = useState([]);
  const [dealers, setDealers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    dealer_ids: []
  });

  useEffect(() => {
    fetchBrands();
    fetchDealers();
  }, []);

  const fetchBrands = async () => {
    try {
      const response = await api.get('/brands/');
      setBrands(response.data);
    } catch (error) {
      console.error('Error fetching brands:', error);
    }
  };

  const fetchDealers = async () => {
    try {
      const response = await api.get('/dealers/');
      setDealers(response.data);
    } catch (error) {
      console.error('Error fetching dealers:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      // Create brand first
      const brandResponse = await api.post('/brands/', {
        name: formData.name
      });
      
      // Link dealers to brand
      if (formData.dealer_ids.length > 0) {
        const linkPromises = formData.dealer_ids.map(dealerId =>
          api.post(`/brands/${brandResponse.data.id}/dealers/${dealerId}`)
        );
        await Promise.all(linkPromises);
      }
      
      setMessage('Brand created and linked to dealers successfully!');
      setFormData({ name: '', dealer_ids: [] });
      fetchBrands();
    } catch (error) {
      console.error('Brand creation error:', error);
      if (error.response?.data?.detail) {
        setMessage(`Error: ${error.response.data.detail}`);
      } else if (error.message === 'Network Error') {
        setMessage('Error: Network error. Please check your connection and try again.');
      } else {
        setMessage(`Error: ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleDealerSelection = (e) => {
    const dealerId = parseInt(e.target.value);
    if (e.target.checked) {
      setFormData({
        ...formData,
        dealer_ids: [...formData.dealer_ids, dealerId]
      });
    } else {
      setFormData({
        ...formData,
        dealer_ids: formData.dealer_ids.filter(id => id !== dealerId)
      });
    }
  };

  return (
    <div>
      <h2>🏷️ Brands Management</h2>
      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
          <button onClick={() => setMessage('')} style={{ float: 'right', background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}>×</button>
        </div>
      )}
      <div className="grid">
        <div className="form-container">
          <h3>Add New Brand</h3>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            Create a brand and select which dealers will supply this brand.
          </p>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Brand Name: *</label>
              <input type="text" name="name" value={formData.name} onChange={handleChange} required placeholder="Enter brand name (e.g., Nike, Adidas)" />
            </div>
            <div className="form-group">
              <label>Select Dealers (Multi-select): *</label>
              {dealers.length > 0 ? (
                <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #ddd', borderRadius: '5px', padding: '10px', backgroundColor: '#f9f9f9' }}>
                  {dealers.map((dealer) => (
                    <div key={dealer.id} style={{ marginBottom: '8px' }}>
                      <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                        <input 
                          type="checkbox" 
                          value={dealer.id} 
                          checked={formData.dealer_ids.includes(dealer.id)} 
                          onChange={handleDealerSelection} 
                          style={{ marginRight: '8px' }} 
                        />
                        <span><strong>{dealer.name}</strong> - PAN: {dealer.pan}, GST: {dealer.gst}</span>
                      </label>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ padding: '15px', border: '1px solid #ddd', borderRadius: '5px', backgroundColor: '#f9f9f9', textAlign: 'center', color: '#666' }}>
                  <p style={{ margin: 0, fontStyle: 'italic' }}>No dealers available. Please add dealers first in the Dealers tab.</p>
                </div>
              )}
              {formData.dealer_ids.length > 0 && (
                <p style={{ marginTop: '8px', fontSize: '14px', color: '#28a745' }}>✅ Selected {formData.dealer_ids.length} dealer(s)</p>
              )}
            </div>
            <button type="submit" className="btn btn-success" disabled={loading || dealers.length === 0}>
              {loading ? 'Adding...' : 'Add Brand'}
            </button>
          </form>
        </div>
        <div className="table-container">
          <h3>Current Brands</h3>
          {loading ? (
            <p>Loading brands...</p>
          ) : brands.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                </tr>
              </thead>
              <tbody>
                {brands.map((brand) => (
                  <tr key={brand.id}>
                    <td>{brand.id}</td>
                    <td><strong>{brand.name}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p style={{ textAlign: 'center', color: '#666', fontStyle: 'italic' }}>No brands added yet. Add your first brand above.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Brands; 