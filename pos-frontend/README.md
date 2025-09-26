# Garments POS Frontend

A React-based frontend for the Garments POS System with inventory-level barcode tracking.

## 🚀 Quick Start

### Prerequisites
- Node.js (v14 or higher)
- Backend server running on `http://localhost:8000`

### Installation
```bash
npm install
```

### Start Development Server
```bash
npm start
```

The app will open at `http://localhost:3000`

## 📱 Features

### 🏷️ **Dealers Management**
- Add new dealers with GSTIN and contact info
- View all dealers in a table format
- **NEW**: Link multiple brands to each dealer
- **NEW**: View which brands are linked to each dealer

### 🏷️ **Brands Management**
- Add new brands
- View all brands
- **NEW**: Link multiple dealers to each brand
- **NEW**: View which dealers are linked to each brand

### 👕 **Products Management**
- Add products with brand selection
- Product details: name, design number, size, color, type, cost price, MRP
- View all products with brand information

### 📦 **Inventory Management**
- **Add Inventory**: Link products to unique barcodes with quantities
- **Subtract Inventory**: Reduce stock by scanning barcodes
- **Search by Barcode**: Find inventory items by barcode
- **View All Inventory**: See all inventory items in a table

## 🔧 Key Features

### ✅ **Brand-Dealer Relationships**
- **Many-to-Many Relationship**: Each brand can have multiple dealers, each dealer can have multiple brands
- **Link Management**: Easily link/unlink dealers and brands through the UI
- **Bidirectional Viewing**: View dealers for a brand or brands for a dealer
- **Smart Filtering**: Only show unlinked dealers/brands in dropdowns

### ✅ **Barcode Management**
- Each inventory item has a unique barcode
- Generate random barcodes for testing
- Search inventory by barcode
- Subtract stock by barcode

### ✅ **Real-time Updates**
- Forms automatically refresh data after operations
- Success/error messages for all operations
- Loading states for better UX

### ✅ **Responsive Design**
- Works on desktop and mobile
- Clean, modern UI
- Tab-based navigation

## 🧪 Testing the System

1. **Start the Backend** (in a separate terminal):
   ```bash
   cd ../garments_pos
   uvicorn main:app --reload
   ```

2. **Start the Frontend**:
   ```bash
   npm start
   ```

3. **Test the Workflow**:
   - Add dealers (Dealers tab)
   - Add brands (Brands tab)
   - Link dealers to brands (Brands tab → Link Dealers)
   - Link brands to dealers (Dealers tab → Link Brands)
   - Add products (Products tab)
   - Add inventory items (Inventory tab)
   - Test barcode search and subtraction

## 🎯 Sample Workflow

1. **Add Dealers**: 
   - "Premium Fashion Supplier" with GSTIN "GST987654321"
   - "Sports Gear Ltd" with GSTIN "GST111222333"

2. **Add Brands**: 
   - "Nike"
   - "Adidas"

3. **Link Relationships**:
   - Link both dealers to "Adidas" brand
   - Link "Premium Fashion Supplier" to "Nike" brand

4. **Add Products**: "Nike T-Shirt" with size "M", color "Blue"

5. **Add Inventory**: Link product to barcode "1234567890123" with quantity 10

6. **Test Operations**: Search barcode, subtract inventory, view relationships

## 🔗 API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000` with the following endpoints:

### Core Endpoints
- `GET/POST /dealers/` - Dealer management
- `GET/POST /brands/` - Brand management  
- `GET/POST /products/` - Product management
- `GET/POST /inventory/` - Inventory management
- `PUT /inventory/subtract` - Subtract inventory
- `GET /inventory/barcode/{barcode}` - Search by barcode

### **NEW**: Brand-Dealer Relationship Endpoints
- `POST /brands/{brand_id}/dealers/{dealer_id}` - Link dealer to brand
- `DELETE /brands/{brand_id}/dealers/{dealer_id}` - Unlink dealer from brand
- `GET /brands/{brand_id}/dealers` - Get dealers for a brand
- `GET /dealers/{dealer_id}/brands` - Get brands for a dealer

## 🛠️ Technical Stack

- **Frontend**: React 18
- **HTTP Client**: Axios
- **Styling**: CSS3 with responsive design
- **State Management**: React Hooks (useState, useEffect)

## 📁 Project Structure

```
pos-frontend/
├── src/
│   ├── pages/
│   │   ├── Dealers.js      # Dealers management with brand linking
│   │   ├── Brands.js       # Brands management with dealer linking
│   │   ├── Products.js     # Products management
│   │   └── Inventory.js    # Inventory management
│   ├── api.js              # API configuration
│   ├── App.js              # Main app component
│   └── App.css             # Styles
├── public/
├── test_brand_dealer_linking.js  # Test script for relationships
└── package.json
```

## 🎨 UI Features

- **Modern Design**: Clean, professional interface
- **Color-coded Actions**: Green for add, red for subtract
- **Responsive Tables**: Scrollable on mobile
- **Form Validation**: Required fields and proper input types
- **Loading States**: Visual feedback during API calls
- **Success/Error Messages**: Clear feedback for all operations
- **Tab-based Navigation**: Easy switching between functions
- **Smart Dropdowns**: Only show available options for linking

## 🔄 Future Enhancements

- Barcode scanner integration
- Real-time inventory updates
- Advanced search and filtering
- Export functionality
- User authentication
- Checkout system
- Sales analytics dashboard
- Product images and descriptions
- Bulk import/export functionality
