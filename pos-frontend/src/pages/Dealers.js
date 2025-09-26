import React, { useState, useEffect } from 'react';
import api from '../api';

const Dealers = () => {
  const [dealers, setDealers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  
  const [formData, setFormData] = useState({
    name: '',
    pan: '',
    gst: '',
    address: ''
  });

  useEffect(() => {
    fetchDealers();
  }, []);

  const fetchDealers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/dealers/');
      setDealers(response.data);
    } catch (error) {
      setMessage('Error fetching dealers: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await api.post('/dealers/', formData);
      setMessage('Dealer added successfully!');
      setFormData({ name: '', pan: '', gst: '', address: '' });
      fetchDealers();
    } catch (error) {
      setMessage('Error adding dealer: ' + error.message);
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

  return (
    <div>
      <h2>📋 Dealers Management</h2>
      
      {message && (
        <div className={`alert ${message.includes('Error') ? 'alert-error' : 'alert-success'}`}>
          {message}
        </div>
      )}

      <div className="grid">
        <div className="form-container">
          <h3>Add New Dealer</h3>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            Create a dealer first. Then you can link brands to this dealer.
          </p>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Dealer Name: *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                required
                placeholder="Enter dealer name"
              />
            </div>
            <div className="form-group">
              <label>PAN Number: *</label>
              <input
                type="text"
                name="pan"
                value={formData.pan}
                onChange={handleChange}
                required
                placeholder="ABCDE1234F"
                maxLength="10"
              />
            </div>
            <div className="form-group">
              <label>GST Number: *</label>
              <input
                type="text"
                name="gst"
                value={formData.gst}
                onChange={handleChange}
                required
                placeholder="GST123456789"
              />
            </div>
            <div className="form-group">
              <label>Address: (Optional)</label>
              <textarea
                name="address"
                value={formData.address}
                onChange={handleChange}
                placeholder="Enter dealer address"
                rows="3"
                style={{
                  width: '100%',
                  padding: '10px',
                  border: '1px solid #ddd',
                  borderRadius: '5px',
                  fontSize: '16px',
                  resize: 'vertical'
                }}
              />
            </div>
            
            <button type="submit" className="btn btn-success" disabled={loading}>
              {loading ? 'Adding...' : 'Add Dealer'}
            </button>
          </form>
        </div>

        <div className="table-container">
          <h3>Current Dealers</h3>
          {loading ? (
            <p>Loading dealers...</p>
          ) : dealers.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>PAN</th>
                  <th>GST</th>
                  <th>Address</th>
                </tr>
              </thead>
              <tbody>
                {dealers.map((dealer) => (
                  <tr key={dealer.id}>
                    <td>{dealer.id}</td>
                    <td><strong>{dealer.name}</strong></td>
                    <td>{dealer.pan}</td>
                    <td>{dealer.gst}</td>
                    <td>{dealer.address || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p style={{ textAlign: 'center', color: '#666', fontStyle: 'italic' }}>
              No dealers added yet. Add your first dealer above.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dealers; 