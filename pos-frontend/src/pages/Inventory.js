import React, { useState, useEffect } from 'react';
import api from '../api';

const Inventory = () => {
  const [inventory, setInventory] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState('add');
  const [sizeScales, setSizeScales] = useState({});

  const [formData, setFormData] = useState({
    product_id: '',
    barcode: '', // Not used for input, but for internal state if needed
    quantity: 1, // Number of items to generate barcodes for
    design_number: '',
    size: '',
    color: '',
    cost_price: '',
    mrp: ''
  });

  // Manual barcode input state
  const [manualBarcodes, setManualBarcodes] = useState('');
  const [selectedProductForManual, setSelectedProductForManual] = useState('');
  const [manualDesignNumber, setManualDesignNumber] = useState('');
  const [manualSize, setManualSize] = useState('');
  const [manualColor, setManualColor] = useState('');
  const [manualCostPrice, setManualCostPrice] = useState('');
  const [manualMrp, setManualMrp] = useState('');

  // CSV upload state
  const [csvFile, setCsvFile] = useState(null);
  const [csvData, setCsvData] = useState([]);
  const [csvPreview, setCsvPreview] = useState([]);

  const [searchBarcode, setSearchBarcode] = useState('');
  const [searchResult, setSearchResult] = useState(null);
  const [subtractBarcode, setSubtractBarcode] = useState('');
  const [subtractQuantity, setSubtractQuantity] = useState(1);

  useEffect(() => {
    fetchInventory();
    fetchProducts();
    fetchSizeScales();
  }, []);

  const fetchInventory = async () => {
    try {
      const response = await api.get('/inventory/');
      setInventory(response.data);
    } catch (error) {
      console.error('Error fetching inventory:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/');
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
    }
  };

  const fetchSizeScales = async () => {
    try {
      const response = await api.get('/size-scales');
      setSizeScales(response.data);
    } catch (error) {
      console.error('Error fetching size scales:', error);
    }
  };

  const generateBarcode = () => {
    const timestamp = Date.now();
    const random = Math.floor(Math.random() * 1000);
    return `BC${timestamp}${random}`;
  };

  const getSelectedProduct = () => {
    return products.find(p => p.id === parseInt(formData.product_id));
  };

  const getSizeOptions = () => {
    const selectedProduct = getSelectedProduct();
    if (!selectedProduct) return [];
    
    const scale = selectedProduct.size_type;
    return sizeScales[scale] || [];
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.design_number || !formData.size || !formData.color || !formData.cost_price || !formData.mrp) {
      setMessage('Please fill in all required fields: design number, size, color, cost price, and MRP');
      return;
    }

    try {
      setLoading(true);
      const promises = [];
      for (let i = 0; i < formData.quantity; i++) {
        const uniqueBarcode = generateBarcode();
        promises.push(api.post('/inventory/', {
          product_id: parseInt(formData.product_id),
          barcode: uniqueBarcode,
          design_number: formData.design_number,
          size: formData.size,
          color: formData.color,
          cost_price: parseFloat(formData.cost_price),
          mrp: parseFloat(formData.mrp),
          quantity: 1 // Each item has quantity 1
        }));
      }
      await Promise.all(promises);
      setMessage(`Successfully added ${formData.quantity} items with unique barcodes!`);
      setFormData({ product_id: '', barcode: '', quantity: 1, design_number: '', size: '', color: '', cost_price: '', mrp: '' });
      fetchInventory();
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Manual barcode input handler
  const handleManualBarcodeSubmit = async (e) => {
    e.preventDefault();
    if (!selectedProductForManual || !manualBarcodes.trim() || !manualDesignNumber || !manualSize || !manualColor || !manualCostPrice || !manualMrp) {
      setMessage('Please fill in all required fields: product, barcodes, design number, size, color, cost price, and MRP');
      return;
    }

    try {
      setLoading(true);
      const barcodeList = manualBarcodes.split('\n').map(b => b.trim()).filter(b => b);
      
      const promises = barcodeList.map(barcode => 
        api.post('/inventory/', {
          product_id: parseInt(selectedProductForManual),
          barcode: barcode,
          design_number: manualDesignNumber,
          size: manualSize,
          color: manualColor,
          cost_price: parseFloat(manualCostPrice),
          mrp: parseFloat(manualMrp),
          quantity: 1
        })
      );
      
      await Promise.all(promises);
      setMessage(`Successfully added ${barcodeList.length} items with manual barcodes!`);
      setManualBarcodes('');
      setSelectedProductForManual('');
      setManualDesignNumber('');
      setManualSize('');
      setManualColor('');
      setManualCostPrice('');
      setManualMrp('');
      fetchInventory();
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  // CSV file handler
  const handleCsvFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type === 'text/csv') {
      setCsvFile(file);
      const reader = new FileReader();
      reader.onload = (event) => {
        const csvText = event.target.result;
        const lines = csvText.split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        const data = lines.slice(1).filter(line => line.trim()).map(line => {
          const values = line.split(',').map(v => v.trim());
          const row = {};
          headers.forEach((header, index) => {
            row[header] = values[index] || '';
          });
          return row;
        });
        setCsvData(data);
        setCsvPreview(data.slice(0, 5)); // Show first 5 rows
      };
      reader.readAsText(file);
    } else {
      setMessage('Please select a valid CSV file');
    }
  };

  // CSV upload handler
  const handleCsvUpload = async () => {
    if (!csvData.length) {
      setMessage('Please select a CSV file first');
      return;
    }

    try {
      setLoading(true);
      const promises = csvData.map(row => {
        const productId = parseInt(row.product_id);
        const barcode = row.barcode;
        const designNumber = row.design_number;
        const size = row.size;
        const color = row.color;
        const costPrice = parseFloat(row.cost_price);
        const mrp = parseFloat(row.mrp);
        
        if (!productId || !barcode || !designNumber || !size || !color || isNaN(costPrice) || isNaN(mrp)) {
          throw new Error(`Invalid data in CSV: product_id=${row.product_id}, barcode=${row.barcode}, design_number=${row.design_number}, size=${row.size}, color=${row.color}, cost_price=${row.cost_price}, mrp=${row.mrp}`);
        }

        return api.post('/inventory/', {
          product_id: productId,
          barcode: barcode,
          design_number: designNumber,
          size: size,
          color: color,
          cost_price: costPrice,
          mrp: mrp,
          quantity: 1
        });
      });

      await Promise.all(promises);
      setMessage(`Successfully uploaded ${csvData.length} items from CSV!`);
      setCsvFile(null);
      setCsvData([]);
      setCsvPreview([]);
      fetchInventory();
    } catch (error) {
      setMessage(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
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

  const handleSubtract = async () => {
    if (!subtractBarcode.trim()) {
      setMessage('Please enter a barcode');
      return;
    }

    try {
      setLoading(true);
      await api.post('/inventory/subtract', {
        barcode: subtractBarcode,
        quantity: parseInt(subtractQuantity)
      });
      setMessage(`Successfully subtracted ${subtractQuantity} from inventory`);
      setSubtractBarcode('');
      setSubtractQuantity(1);
      fetchInventory();
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

  const getProductName = (productId) => {
    const product = products.find(p => p.id === productId);
    return product ? product.name : 'Unknown Product';
  };

  return (
    <div>
      <h2>📦 Inventory Management</h2>
      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
          <button onClick={() => setMessage('')} style={{ float: 'right', background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}>×</button>
        </div>
      )}
      
      <div style={{ marginBottom: '20px' }}>
        <button className={`btn ${activeTab === 'add' ? 'btn-success' : ''}`} onClick={() => setActiveTab('add')}>➕ Auto Generate</button>
        <button className={`btn ${activeTab === 'manual' ? 'btn-success' : ''}`} onClick={() => setActiveTab('manual')}>✏️ Manual Input</button>
        <button className={`btn ${activeTab === 'csv' ? 'btn-success' : ''}`} onClick={() => setActiveTab('csv')}>📄 CSV Upload</button>
        <button className={`btn ${activeTab === 'search' ? 'btn-success' : ''}`} onClick={() => setActiveTab('search')}>🔍 Search by Barcode</button>
        <button className={`btn ${activeTab === 'subtract' ? 'btn-success' : ''}`} onClick={() => setActiveTab('subtract')}>➖ Subtract Stock</button>
        <button className={`btn ${activeTab === 'view' ? 'btn-success' : ''}`} onClick={() => setActiveTab('view')}>📋 View All Inventory</button>
      </div>

      {activeTab === 'add' && (
        <div className="form-container">
          <h3>Add Inventory Items (Auto-Generated Barcodes)</h3>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            <strong>Important:</strong> Each individual item gets its own unique barcode.
            If you add 10 jeans, you'll get 10 unique barcodes - one for each jean.
          </p>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>Product: *</label>
              <select name="product_id" value={formData.product_id} onChange={handleChange} required>
                <option value="">Choose a product</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name} - {product.design_number}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Design Number: *</label>
              <input type="text" name="design_number" value={formData.design_number} onChange={handleChange} required placeholder="Enter design number" />
            </div>
            <div className="form-group">
              <label>Size: *</label>
              <select name="size" value={formData.size} onChange={handleChange} required disabled={!formData.product_id}>
                <option value="">{formData.product_id ? 'Choose size' : 'Select product first'}</option>
                {getSizeOptions().map((size) => (
                  <option key={size} value={size}>{size}</option>
                ))}
              </select>
              {formData.product_id && getSizeOptions().length === 0 && (
                <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>No size options available for this product's size type</p>
              )}
            </div>
            <div className="form-group">
              <label>Color: *</label>
              <input type="text" name="color" value={formData.color} onChange={handleChange} required placeholder="Enter color" />
            </div>
            <div className="form-group">
              <label>Cost Price (Excluding GST): *</label>
              <input type="number" name="cost_price" value={formData.cost_price} onChange={handleChange} required placeholder="0.00" step="0.01" min="0" />
            </div>
            <div className="form-group">
              <label>MRP (Including GST): *</label>
              <input type="number" name="mrp" value={formData.mrp} onChange={handleChange} required placeholder="0.00" step="0.01" min="0" />
            </div>
            <div className="form-group">
              <label>Number of Items: *</label>
              <input 
                type="number" 
                name="quantity" 
                value={formData.quantity} 
                onChange={handleChange} 
                required 
                min="1" 
                max="100" 
                placeholder="How many items to add?" 
              />
              <small style={{ color: '#666' }}>Each item will get a unique barcode automatically</small>
            </div>
            <button type="submit" className="btn btn-success" disabled={loading}>
              {loading ? 'Adding...' : `Add ${formData.quantity} Item(s)`}
            </button>
          </form>
        </div>
      )}

      {activeTab === 'manual' && (
        <div className="form-container">
          <h3>Add Inventory Items (Manual Barcode Input)</h3>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            Enter barcodes manually, one per line. You can scan barcodes or type them in.
          </p>
          <form onSubmit={handleManualBarcodeSubmit}>
            <div className="form-group">
              <label>Product: *</label>
              <select 
                value={selectedProductForManual} 
                onChange={(e) => setSelectedProductForManual(e.target.value)} 
                required
              >
                <option value="">Choose a product</option>
                {products.map((product) => (
                  <option key={product.id} value={product.id}>
                    {product.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Design Number: *</label>
              <input 
                type="text" 
                value={manualDesignNumber} 
                onChange={(e) => setManualDesignNumber(e.target.value)} 
                required 
                placeholder="Enter design number" 
              />
            </div>
            <div className="form-group">
              <label>Size: *</label>
              <select 
                value={manualSize} 
                onChange={(e) => setManualSize(e.target.value)} 
                required
                disabled={!selectedProductForManual}
              >
                <option value="">{selectedProductForManual ? 'Choose size' : 'Select product first'}</option>
                {selectedProductForManual && sizeScales[products.find(p => p.id === parseInt(selectedProductForManual))?.size_type]?.map((size) => (
                  <option key={size} value={size}>{size}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Color: *</label>
              <input 
                type="text" 
                value={manualColor} 
                onChange={(e) => setManualColor(e.target.value)} 
                required 
                placeholder="Enter color" 
              />
            </div>
            <div className="form-group">
              <label>Cost Price (Excluding GST): *</label>
              <input 
                type="number" 
                value={manualCostPrice} 
                onChange={(e) => setManualCostPrice(e.target.value)} 
                required 
                placeholder="0.00" 
                step="0.01" 
                min="0" 
              />
            </div>
            <div className="form-group">
              <label>MRP (Including GST): *</label>
              <input 
                type="number" 
                value={manualMrp} 
                onChange={(e) => setManualMrp(e.target.value)} 
                required 
                placeholder="0.00" 
                step="0.01" 
                min="0" 
              />
            </div>
            <div className="form-group">
              <label>Barcodes (one per line): *</label>
              <textarea 
                value={manualBarcodes}
                onChange={(e) => setManualBarcodes(e.target.value)}
                placeholder="Enter barcodes here, one per line:&#10;BC123456789&#10;BC987654321&#10;BC555666777"
                rows="8"
                style={{ 
                  width: '100%', 
                  padding: '10px', 
                  border: '1px solid #ddd', 
                  borderRadius: '5px', 
                  fontSize: '16px', 
                  resize: 'vertical',
                  fontFamily: 'monospace'
                }}
                required
              />
              <small style={{ color: '#666' }}>
                Enter each barcode on a new line. You can scan barcodes or type them manually.
              </small>
            </div>
            <button type="submit" className="btn btn-success" disabled={loading}>
              {loading ? 'Adding...' : `Add ${manualBarcodes.split('\n').filter(b => b.trim()).length} Item(s)`}
            </button>
          </form>
        </div>
      )}

      {activeTab === 'csv' && (
        <div className="form-container">
          <h3>Add Inventory Items (CSV Upload)</h3>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            Upload a CSV file with columns: <strong>product_id, barcode, design_number, size, color, cost_price, mrp</strong><br/>
            Example CSV format:<br/>
            <code>product_id,barcode,design_number,size,color,cost_price,mrp<br/>
            1,BC123456789,DES001,M,Blue,500.00,750.00<br/>
            1,BC987654321,DES002,L,Red,550.00,825.00<br/>
            2,BC555666777,DES003,XL,Green,600.00,900.00</code>
          </p>
          
          <div className="form-group">
            <label>Select CSV File: *</label>
            <input 
              type="file" 
              accept=".csv" 
              onChange={handleCsvFileChange}
              style={{ 
                width: '100%', 
                padding: '10px', 
                border: '1px solid #ddd', 
                borderRadius: '5px', 
                fontSize: '16px' 
              }}
            />
          </div>

          {csvPreview.length > 0 && (
            <div style={{ marginTop: '20px' }}>
              <h4>CSV Preview (first 5 rows):</h4>
              <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
                <thead>
                  <tr style={{ backgroundColor: '#f5f5f5' }}>
                    {Object.keys(csvPreview[0] || {}).map(header => (
                      <th key={header} style={{ padding: '8px', border: '1px solid #ddd', textAlign: 'left' }}>
                        {header}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {csvPreview.map((row, index) => (
                    <tr key={index}>
                      {Object.values(row).map((value, cellIndex) => (
                        <td key={cellIndex} style={{ padding: '8px', border: '1px solid #ddd' }}>
                          {value}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
              <p style={{ marginTop: '10px', fontSize: '14px', color: '#666' }}>
                Total rows in CSV: {csvData.length}
              </p>
            </div>
          )}

          {csvData.length > 0 && (
            <button 
              onClick={handleCsvUpload} 
              className="btn btn-success" 
              disabled={loading}
              style={{ marginTop: '20px' }}
            >
              {loading ? 'Uploading...' : `Upload ${csvData.length} Items from CSV`}
            </button>
          )}
        </div>
      )}

      {activeTab === 'search' && (
        <div className="form-container">
          <h3>Search Inventory by Barcode</h3>
          <form onSubmit={(e) => { e.preventDefault(); handleSearch(); }}>
            <div className="form-group">
              <label>Barcode:</label>
              <input 
                type="text" 
                value={searchBarcode} 
                onChange={(e) => setSearchBarcode(e.target.value)} 
                required 
                placeholder="Enter barcode to search" 
              />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </form>
          
          {searchResult && (
            <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#e8f5e8', borderRadius: '5px', border: '1px solid #28a745' }}>
              <h4>Search Result:</h4>
              <p><strong>Barcode:</strong> {searchResult.barcode}</p>
              <p><strong>Product:</strong> {getProductName(searchResult.product_id)}</p>
              <p><strong>Design Number:</strong> {searchResult.design_number}</p>
              <p><strong>Size:</strong> {searchResult.size}</p>
              <p><strong>Color:</strong> {searchResult.color}</p>
              <p><strong>Cost Price:</strong> ₹{searchResult.cost_price}</p>
              <p><strong>MRP:</strong> ₹{searchResult.mrp}</p>
              <p><strong>Quantity:</strong> {searchResult.quantity}</p>
              <p><strong>Created:</strong> {new Date(searchResult.created_at).toLocaleDateString()}</p>
            </div>
          )}
        </div>
      )}

      {activeTab === 'subtract' && (
        <div className="form-container">
          <h3>Subtract Stock by Barcode</h3>
          <form onSubmit={(e) => { e.preventDefault(); handleSubtract(); }}>
            <div className="form-group">
              <label>Barcode:</label>
              <input 
                type="text" 
                value={subtractBarcode} 
                onChange={(e) => setSubtractBarcode(e.target.value)} 
                required 
                placeholder="Enter barcode" 
              />
            </div>
            <div className="form-group">
              <label>Quantity to Subtract:</label>
              <input 
                type="number" 
                value={subtractQuantity} 
                onChange={(e) => setSubtractQuantity(e.target.value)} 
                required 
                min="1" 
                placeholder="1" 
              />
            </div>
            <button type="submit" className="btn btn-warning" disabled={loading}>
              {loading ? 'Subtracting...' : 'Subtract Stock'}
            </button>
          </form>
        </div>
      )}

      {activeTab === 'view' && (
        <div className="table-container">
          <h3>Current Inventory</h3>
          {loading ? (
            <p>Loading inventory...</p>
          ) : inventory.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>Barcode</th>
                  <th>Product</th>
                  <th>Design No.</th>
                  <th>Size</th>
                  <th>Color</th>
                  <th>Cost Price</th>
                  <th>MRP</th>
                  <th>Quantity</th>
                  <th>Created</th>
                  <th>Updated</th>
                </tr>
              </thead>
              <tbody>
                {inventory.map((item) => (
                  <tr key={item.id}>
                    <td><strong>{item.barcode}</strong></td>
                    <td>{getProductName(item.product_id)}</td>
                    <td>{item.design_number}</td>
                    <td>{item.size}</td>
                    <td>{item.color}</td>
                    <td>₹{item.cost_price}</td>
                    <td>₹{item.mrp}</td>
                    <td>{item.quantity}</td>
                    <td>{new Date(item.created_at).toLocaleDateString()}</td>
                    <td>
                      {item.updated_at
                        ? new Date(item.updated_at).toLocaleDateString()
                        : '-'
                      }
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p style={{ textAlign: 'center', color: '#666', fontStyle: 'italic' }}>
              No inventory items found. Add some items first.
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default Inventory; 