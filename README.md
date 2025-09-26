# Garments POS System

A comprehensive Point of Sale (POS) system for garments retail businesses.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database (Railway/Supabase)

### Setup with External Database

#### Option 1: Railway (Recommended)
1. Go to [railway.app](https://railway.app)
2. Create a new project
3. Add a PostgreSQL database
4. Copy the database URL

#### Option 2: Supabase
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings > Database
4. Copy the connection string

### Environment Variables
Set these environment variables in your deployment platform:

```bash
DATABASE_URL=postgresql://username:password@host:port/database
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Deploy to Render
1. Fork this repository
2. Connect to Render
3. Set the environment variables
4. Deploy

## 🔐 Default Users

After setup, these users will be available:

- **Admin**: `admin` / `admin123`
- **Cashier**: `cashier` / `cashier123`
- **Inventory Manager**: `inventory` / `inventory123`

## 📚 Features

- **User Management**: Role-based access control
- **Inventory Management**: Track products and stock
- **Sales Processing**: Complete checkout workflow
- **Customer Management**: CRM with loyalty system
- **Reporting**: Sales analytics and reports
- **WhatsApp Integration**: Send invoices via WhatsApp
- **PDF Generation**: Generate invoices and receipts

## 🛠️ Development

### Local Setup
```bash
# Clone repository
git clone <repository-url>
cd garments-pos-system

# Install dependencies
pip install -r requirements.txt

# Set up database
python setup_database.py

# Run development server
uvicorn main:app --reload
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 📖 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License. # Test deployment trigger
