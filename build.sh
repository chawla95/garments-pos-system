#!/usr/bin/env bash
# Build script for Render deployment

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Creating database..."
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"

echo "Setting up admin user..."
python create_admin.py

echo "Setting up test data..."
python setup_test_data.py

echo "Build completed successfully!" 