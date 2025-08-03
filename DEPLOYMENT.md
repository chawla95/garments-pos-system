# 🚀 Deployment Guide

## 📋 Prerequisites

- **Git**: For version control
- **GitHub Account**: For repository hosting
- **Python 3.11+**: For backend
- **Node.js 16+**: For frontend
- **Docker** (optional): For containerized deployment

## 🎯 Deployment Options

### **Option 1: GitHub Repository Setup**

#### **Step 1: Create GitHub Repository**
1. Go to [GitHub.com](https://github.com)
2. Click "New repository"
3. Name: `garments-pos-system`
4. Description: "Complete POS system for garments retail"
5. Make it **Public** (for easier deployment)
6. Don't initialize with README (we already have one)

#### **Step 2: Push to GitHub**
```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/garments-pos-system.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### **Option 2: Local Production Setup**

#### **Step 1: Install PM2**
```bash
npm install -g pm2
```

#### **Step 2: Start Backend**
```bash
cd garments_pos
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name "pos-backend"
```

#### **Step 3: Build and Start Frontend**
```bash
cd pos-frontend
npm install
npm run build
pm2 start "serve -s build -l 3000" --name "pos-frontend"
```

#### **Step 4: Auto-start on Boot**
```bash
pm2 startup
pm2 save
```

### **Option 3: Docker Deployment**

#### **Step 1: Build and Run**
```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### **Step 2: Access Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### **Option 4: Cloud Deployment**

#### **A. Railway.app (Recommended for Beginners)**

**Steps:**
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `garments-pos-system` repository
5. Add environment variables:
   ```
   DATABASE_URL=sqlite:///./pos_system.db
   SECRET_KEY=your-secret-key-here
   ```
6. Deploy automatically

**Cost**: $5-20/month

#### **B. Render.com (Free Tier Available)**

**Steps:**
1. Go to [Render.com](https://render.com)
2. Sign up with GitHub
3. Click "New Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Deploy

**Cost**: Free tier available

#### **C. DigitalOcean App Platform**

**Steps:**
1. Go to [DigitalOcean](https://digitalocean.com)
2. Create account and add payment method
3. Go to "Apps" → "Create App"
4. Connect GitHub repository
5. Configure environment variables
6. Deploy

**Cost**: $5-25/month

#### **D. AWS EC2 (Advanced)**

**Steps:**
1. Launch Ubuntu EC2 instance
2. Install Docker and Docker Compose
3. Clone repository
4. Run `docker-compose up -d`
5. Configure security groups
6. Set up domain and SSL

**Cost**: $10-50/month

## 🔧 Environment Configuration

### **Production Environment Variables**
Create `.env` file:
```bash
# Database
DATABASE_URL=sqlite:///./pos_system.db

# JWT Security
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# WhatsApp (Optional)
INTERAKT_API_KEY=your_interakt_api_key
INTERAKT_API_SECRET=your_interakt_api_secret
INTERAKT_PHONE_NUMBER_ID=your_phone_number_id
INTERAKT_BUSINESS_ACCOUNT_ID=your_business_account_id

# Shop Details
SHOP_NAME=Your Garments Store
SHOP_ADDRESS=123 Main Street, City, State 12345
SHOP_PHONE=+91-9876543210
SHOP_EMAIL=info@yourstore.com
SHOP_GSTIN=22AAAAA0000A1Z5
```

### **Database Migration**
For production, consider migrating to PostgreSQL:

```bash
# Install PostgreSQL dependencies
pip install psycopg2-binary

# Update DATABASE_URL
DATABASE_URL=postgresql://user:password@localhost/pos_db
```

## 🔒 Security Checklist

### **Before Deployment**
- [ ] Change default admin password
- [ ] Update SECRET_KEY
- [ ] Configure HTTPS/SSL
- [ ] Set up firewall rules
- [ ] Enable CORS properly
- [ ] Configure rate limiting

### **After Deployment**
- [ ] Test all user roles
- [ ] Verify API endpoints
- [ ] Check database connections
- [ ] Test WhatsApp integration
- [ ] Monitor application logs

## 📊 Monitoring & Maintenance

### **Health Checks**
```bash
# Check backend health
curl http://localhost:8000/

# Check frontend
curl http://localhost:3000/

# Check database
python -c "from database import engine; print('DB OK')"
```

### **Logs**
```bash
# PM2 logs
pm2 logs

# Docker logs
docker-compose logs -f

# Application logs
tail -f backend.log
```

### **Backup**
```bash
# Database backup
cp pos_system.db backup_$(date +%Y%m%d).db

# Full backup
tar -czf pos_backup_$(date +%Y%m%d).tar.gz .
```

## 🚨 Troubleshooting

### **Common Issues**

#### **1. Port Already in Use**
```bash
# Find process using port
lsof -i :8000
lsof -i :3000

# Kill process
kill -9 <PID>
```

#### **2. Database Errors**
```bash
# Recreate database
rm pos_system.db
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
python create_admin.py
```

#### **3. Authentication Issues**
```bash
# Clear browser cache
# Or restart application
pm2 restart all
```

#### **4. Docker Issues**
```bash
# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 📈 Performance Optimization

### **Backend**
- Use Gunicorn with multiple workers
- Enable database connection pooling
- Implement caching (Redis)
- Optimize database queries

### **Frontend**
- Enable gzip compression
- Use CDN for static assets
- Implement lazy loading
- Optimize bundle size

## 🔄 Updates & Maintenance

### **Regular Updates**
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade
cd pos-frontend && npm update

# Restart services
pm2 restart all
# or
docker-compose restart
```

### **Database Migrations**
```bash
# Backup before migration
cp pos_system.db backup.db

# Run migration scripts
python migrate_database.py
```

## 📞 Support

### **Getting Help**
1. Check the logs for error messages
2. Review the troubleshooting section
3. Create an issue on GitHub
4. Check the API documentation at `/docs`

### **Useful Commands**
```bash
# Check system status
pm2 status
docker-compose ps

# View logs
pm2 logs
docker-compose logs

# Restart services
pm2 restart all
docker-compose restart

# Update application
git pull && pm2 restart all
```

---

**🎉 Your POS system is now ready for deployment!** 