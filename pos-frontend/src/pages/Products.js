import React, { useState, useEffect } from 'react';
import api from '../api';

const Products = () => {
  const [products, setProducts] = useState([]);
  const [brands, setBrands] = useState([]);
  const [productTypes, setProductTypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const [formData, setFormData] = useState({
    brand_id: '',
    type: '',
    size_type: 'ALPHA',
    gst_rate: 12.0
  });

  useEffect(() => {
    fetchProducts();
    fetchBrands();
    fetchProductTypes();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/');
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
      // Don't show error message to user for background refresh
      // Only log it for debugging
    }
  };

  const fetchBrands = async () => {
    try {
      const response = await api.get('/brands/');
      setBrands(response.data);
    } catch (error) {
      console.error('Error fetching brands:', error);
      // Don't show error message to user for background refresh
    }
  };

  const fetchProductTypes = async () => {
    try {
      const response = await api.get('/product-types');
      setProductTypes(response.data);
    } catch (error) {
      console.error('Error fetching product types:', error);
      // Don't show error message to user for background refresh
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await api.post('/products/', formData);
      setMessage('Product added successfully!');
      setFormData({
        brand_id: '',
        type: '',
        size_type: 'ALPHA',
        gst_rate: 12.0
      });
      // Try to refresh the products list, but don't show error if it fails
      try {
        await fetchProducts();
      } catch (refreshError) {
        console.warn('Failed to refresh products list, but product was added successfully:', refreshError);
        // Don't show this error to the user since the main operation succeeded
      }
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`);
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

  const getSelectedBrand = () => {
    return brands.find(b => b.id === parseInt(formData.brand_id));
  };

  return (
    <div>
      <h2>👕 Products Management</h2>
      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
          <button onClick={() => setMessage('')} style={{ float: 'right', background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}>×</button>
        </div>
      )}
      <div className="grid">
        <div className="form-container">
          <h3>Add New Product</h3>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            Product name will be auto-generated as: Brand-Type<br/>
            Design number, cost price, MRP, size, and color will be specified when adding inventory items.
          </p>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Brand: *</label>
              <select name="brand_id" value={formData.brand_id} onChange={handleChange} required>
                <option value="">Choose a brand</option>
                {brands.map((brand) => (
                  <option key={brand.id} value={brand.id}>{brand.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Product Type: *</label>
              <select name="type" value={formData.type} onChange={handleChange} required>
                <option value="">Choose product type</option>
                {productTypes.map((type) => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Size Type: *</label>
              <select name="size_type" value={formData.size_type} onChange={handleChange} required>
                <option value="ALPHA">Alpha (XS, S, M, L, XL, XXL, XXXL)</option>
                <option value="NUMERIC">Numeric (2, 4, 6, 8, ..., 50)</option>
                <option value="CUSTOM">Custom (User-defined sizes)</option>
              </select>
            </div>
            <div className="form-group">
              <label>GST Rate (%): *</label>
              <select name="gst_rate" value={formData.gst_rate} onChange={handleChange} required>
                <option value="5.0">5% (Basic necessities)</option>
                <option value="12.0">12% (Standard rate)</option>
                <option value="18.0">18% (Premium items)</option>
                <option value="28.0">28% (Luxury items)</option>
              </select>
            </div>
            {formData.brand_id && formData.type && (
              <div style={{ padding: '10px', backgroundColor: '#e8f5e8', borderRadius: '5px', marginBottom: '15px', border: '1px solid #28a745' }}>
                <strong>Auto-generated Product Name:</strong><br />
                <span style={{ color: '#28a745', fontSize: '16px' }}>{getSelectedBrand()?.name}-{formData.type}</span>
              </div>
            )}
            <button type="submit" className="btn btn-success" disabled={loading}>
              {loading ? 'Adding...' : 'Add Product'}
            </button>
          </form>
        </div>
        <div className="table-container">
          <h3>Current Products</h3>
          {loading ? (
            <p>Loading products...</p>
          ) : products.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Brand</th>
                  <th>Type</th>
                  <th>Size Type</th>
                  <th>GST Rate</th>
                </tr>
              </thead>
              <tbody>
                {products.map((product) => (
                  <tr key={product.id}>
                    <td>{product.id}</td>
                    <td><strong>{product.name}</strong></td>
                    <td>{brands.find(b => b.id === product.brand_id)?.name || 'N/A'}</td>
                    <td>{product.type}</td>
                    <td>{product.size_type}</td>
                    <td>{product.gst_rate}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p style={{ textAlign: 'center', color: '#666', fontStyle: 'italic' }}>No products added yet. Add your first product above.</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Products; 