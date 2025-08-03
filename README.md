# 🏪 Garments POS System

A comprehensive Point of Sale (POS) system designed specifically for garments retail stores. Built with FastAPI backend and React frontend.

## ✨ Features

### 🛍️ **Core POS Features**
- **Inventory Management**: Track products, brands, dealers, and stock levels
- **Barcode System**: Unique barcode for each inventory item
- **Checkout System**: Complete sales with GST calculation (Indian standards)
- **Returns Management**: Handle product returns with full tracking
- **Invoice Generation**: PDF invoices with barcodes

### 📊 **Analytics & Reporting**
- **Dashboard**: Real-time sales analytics and insights
- **GST Reports**: Detailed tax breakdown and reporting
- **Inventory Aging**: Track slow-moving and deadstock items
- **Top Products**: Best-selling items analysis

### 👥 **User Management**
- **Role-Based Access Control (RBAC)**: Admin, Cashier, Inventory Manager, Manager, Viewer
- **User Authentication**: JWT-based secure authentication
- **Permission Management**: Granular access control

### 💰 **Financial Management**
- **Cash Register**: Daily opening/closing balance tracking
- **Expense Tracking**: Manual expense entries
- **Loyalty System**: Customer points earning and redemption
- **CRM**: Customer relationship management

### 📱 **Communication**
- **WhatsApp Integration**: Send invoices and notifications via WhatsApp
- **Customer Management**: Phone number-based customer linking
- **Broadcast Campaigns**: Send messages to customer groups

### 🤖 **AI/ML Features**
- **Demand Forecasting**: Predict product demand using ML
- **Reorder Suggestions**: Automated inventory replenishment
- **Stock Alerts**: Low stock and overstock notifications
- **Inventory Analytics**: Data-driven insights

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 16+
- npm or yarn

### Backend Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd garments_pos

# Install Python dependencies
pip install -r requirements.txt

# Create database and setup
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
python create_admin.py
python setup_test_data.py

# Start backend server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup
```bash
# Navigate to frontend directory
cd pos-frontend

# Install dependencies
npm install

# Start development server
npm start
```

### Default Login
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Administrator

## 📁 Project Structure

```
garments_pos/
├── main.py                 # FastAPI application
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── database.py            # Database configuration
├── auth.py                # Authentication logic
├── config.py              # Configuration settings
├── rbac_service.py        # Role-based access control
├── whatsapp_service.py    # WhatsApp integration
├── ml_forecasting.py      # ML/AI features
├── create_admin.py        # Admin user creation
├── setup_test_data.py     # Test data setup
├── requirements.txt       # Python dependencies
└── pos-frontend/         # React frontend
    ├── src/
    │   ├── pages/        # React components
    │   ├── api.js        # API configuration
    │   └── App.js        # Main app component
    ├── package.json      # Node.js dependencies
    └── public/           # Static files
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```bash
# Database
DATABASE_URL=sqlite:///./pos_system.db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# WhatsApp Business API (Optional)
INTERAKT_API_KEY=your_interakt_api_key
INTERAKT_API_SECRET=your_interakt_api_secret
INTERAKT_PHONE_NUMBER_ID=your_phone_number_id
INTERAKT_BUSINESS_ACCOUNT_ID=your_business_account_id
```

### Shop Configuration
Update shop details in `config.py`:
- Shop name and address
- GSTIN number
- Contact information

## 🛠️ API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Features Overview

### Inventory Management
- **Products**: Brand-Type naming convention
- **Brands**: Multi-dealer support
- **Inventory Items**: Unique barcodes, size, color tracking
- **Stock Alerts**: Low stock notifications

### Sales & Billing
- **Checkout**: Multi-item sales with GST calculation
- **Discounts**: Percentage and fixed amount discounts
- **Returns**: Full and partial returns with receipt generation
- **Invoices**: PDF generation with barcodes

### User Roles
- **Admin**: Full system access
- **Cashier**: Sales and returns
- **Inventory Manager**: Stock management
- **Manager**: General management
- **Viewer**: Read-only access

### Analytics
- **Sales Dashboard**: Daily, weekly, monthly reports
- **GST Summary**: Tax collection and breakdown
- **Top Products**: Best-selling items
- **Inventory Aging**: Slow-moving stock analysis

## 🚀 Deployment

### Local Production
```bash
# Install PM2
npm install -g pm2

# Start backend
cd garments_pos
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name "pos-backend"

# Start frontend
cd pos-frontend
npm run build
pm2 start "serve -s build -l 3000" --name "pos-frontend"

# Save PM2 configuration
pm2 save
pm2 startup
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Cloud Deployment
- **Railway**: Easy deployment with GitHub integration
- **Render**: Free tier available
- **DigitalOcean**: Scalable VPS deployment
- **AWS**: Enterprise-grade cloud deployment

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Role-Based Access**: Granular permission system
- **Input Validation**: Pydantic schema validation
- **SQL Injection Protection**: SQLAlchemy ORM
- **CORS Configuration**: Cross-origin request handling

## 📱 WhatsApp Integration

### Setup
1. Sign up at [interakt.ai](https://interakt.ai)
2. Create WhatsApp Business API account
3. Get API credentials
4. Configure in POS system via "⚙️ Config" page

### Features
- Send invoice summaries
- Thank-you messages with loyalty points
- Broadcast campaigns
- Message templates
- Delivery status tracking

## 🤖 ML/AI Features

### Demand Forecasting
- Predict product demand using historical data
- Suggest reorder quantities and dates
- Flag slow-moving inventory

### Inventory Analytics
- Stock level optimization
- Deadstock identification
- Seasonal trend analysis

## 📈 Performance

- **Backend**: FastAPI with async support
- **Database**: SQLAlchemy with connection pooling
- **Frontend**: React with optimized rendering
- **PDF Generation**: ReportLab for fast invoice creation

## 🐛 Troubleshooting

### Common Issues
1. **Database Errors**: Delete `pos_system.db` and recreate
2. **Authentication Issues**: Clear browser cache and re-login
3. **WhatsApp Errors**: Check API credentials in config
4. **Port Conflicts**: Change ports in configuration

### Logs
- Backend logs: Check uvicorn output
- Frontend logs: Browser developer console
- Database logs: SQLite database file

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation at `/docs`
- Review the troubleshooting section

---

**Built with ❤️ for the retail industry** 