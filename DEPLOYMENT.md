# Garments POS System - Backend Deployment Guide

This guide will help you deploy the Garments POS System backend to Render.

## Prerequisites

1. **Supabase Database**: You need a Supabase PostgreSQL database set up
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **GitHub Repository**: Your code should be in a GitHub repository

## Step 1: Prepare Your Database

### Set up Supabase Database

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Get your database connection string from Settings > Database
3. The connection string should look like: `postgresql://postgres:[password]@[host]:5432/postgres`

## Step 2: Deploy to Render

### Option A: Using render.yaml (Recommended)

1. **Push your code to GitHub** with the `render.yaml` file
2. **Connect to Render**:
   - Go to [render.com](https://render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file

3. **Set Environment Variables**:
   - In the Render dashboard, go to your service
   - Navigate to "Environment" tab
   - Add these required variables:
     ```
     DATABASE_URL=your_supabase_postgresql_url
     SECRET_KEY=your_secret_key_here
     ```

### Option B: Manual Deployment

1. **Create Web Service**:
   - Go to Render dashboard
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure Build Settings**:
   - **Build Command**: `pip install -r requirements.txt && python startup_validation.py`
   - **Start Command**: `python setup_database.py && uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**:
   ```
   DATABASE_URL=your_supabase_postgresql_url
   SECRET_KEY=your_secret_key_here
   ENVIRONMENT=production
   DEBUG=false
   LOG_LEVEL=info
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   SHOP_NAME=Your Garments Store
   SHOP_ADDRESS=123 Main Street, City, State 12345
   SHOP_PHONE=+91-9876543210
   SHOP_EMAIL=info@yourstore.com
   SHOP_GSTIN=22AAAAA0000A1Z5
   DEFAULT_GST_RATE=12.0
   DEFAULT_CURRENCY=INR
   ```

## Step 3: Verify Deployment

1. **Check Health Endpoint**: Visit `https://your-app-name.onrender.com/health`
2. **Check API Documentation**: Visit `https://your-app-name.onrender.com/docs`

## Step 4: Initial Setup

After deployment, the system will automatically:
- Create database tables
- Create an admin user with credentials:
  - Username: `admin`
  - Password: `admin123`

**Important**: Change the admin password after first login!

## Environment Variables Reference

### Required Variables
- `DATABASE_URL`: Your Supabase PostgreSQL connection string
- `SECRET_KEY`: A secure secret key for JWT tokens

### Optional Variables
- `ENVIRONMENT`: Set to "production" for production deployment
- `DEBUG`: Set to "false" for production
- `LOG_LEVEL`: Logging level (info, debug, warning, error)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)
- `SHOP_NAME`: Your store name
- `SHOP_ADDRESS`: Your store address
- `SHOP_PHONE`: Your store phone number
- `SHOP_EMAIL`: Your store email
- `SHOP_GSTIN`: Your GSTIN number
- `DEFAULT_GST_RATE`: Default GST rate (default: 12.0)
- `DEFAULT_CURRENCY`: Default currency (default: INR)

## Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Verify your `DATABASE_URL` is correct
   - Check if your Supabase database is accessible
   - Ensure the database exists and is running

2. **Build Failed**:
   - Check the build logs in Render dashboard
   - Verify all dependencies are in `requirements.txt`
   - Ensure Python version is compatible

3. **Application Won't Start**:
   - Check the logs in Render dashboard
   - Verify all environment variables are set
   - Ensure the start command is correct

### Logs and Monitoring

- **Build Logs**: Available in Render dashboard during deployment
- **Runtime Logs**: Available in the "Logs" tab of your service
- **Health Check**: Use `/health` endpoint to monitor application status

## Security Considerations

1. **Change Default Passwords**: Change the admin password after first login
2. **Secure Environment Variables**: Never commit sensitive data to your repository
3. **Database Security**: Use strong passwords for your database
4. **HTTPS**: Render automatically provides HTTPS for your application

## API Endpoints

After deployment, your API will be available at:
- **Base URL**: `https://your-app-name.onrender.com`
- **API Documentation**: `https://your-app-name.onrender.com/docs`
- **Health Check**: `https://your-app-name.onrender.com/health`

## Support

If you encounter issues:
1. Check the Render logs
2. Verify your environment variables
3. Test your database connection
4. Review the startup validation output

For additional help, check the application logs or contact support. 