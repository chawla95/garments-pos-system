# 🚀 Supabase Setup Guide for Garments POS System

This guide will walk you through setting up Supabase as your external database for the POS system.

## 📋 Prerequisites

- GitHub account
- Render account (for backend deployment)
- Basic understanding of environment variables

## 🎯 Step-by-Step Process

### **Step 1: Create Supabase Account**

1. **Go to [supabase.com](https://supabase.com)**
2. **Click "Start your project"**
3. **Sign up with GitHub** (recommended for easy integration)
4. **Complete the signup process**

### **Step 2: Create New Project**

1. **Click "New Project"** in your Supabase dashboard
2. **Select your organization** (or create one if needed)
3. **Enter project details:**
   - **Name**: `garments-pos-system`
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to your users
     - For India: `Northeast Asia (Singapore)`
     - For US: `US East (N. Virginia)`
     - For Europe: `West Europe (Amsterdam)`
4. **Click "Create new project"**
5. **Wait 2-3 minutes** for setup to complete

### **Step 3: Get Database Connection String**

1. **In your project dashboard, go to Settings → Database**
2. **Scroll down to "Connection string" section**
3. **Copy the "URI" connection string**
   - It looks like: `postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres`
   - Replace `[YOUR-PASSWORD]` with your actual database password

### **Step 4: Test Connection Locally (Optional)**

Run the setup helper script:

```bash
python setup_supabase.py
```

This will:
- Test your connection string
- Create database tables
- Set up initial data
- Generate environment variables

### **Step 5: Update Render Environment Variables**

1. **Go to your Render dashboard**
2. **Select your backend service** (`garments-pos-backend`)
3. **Click "Environment" tab**
4. **Add these environment variables:**

| Variable Name | Value | Description |
|---------------|-------|-------------|
| `DATABASE_URL` | `postgresql://postgres:[PASSWORD]@db.xxxxxxxxxxxxx.supabase.co:5432/postgres` | Your Supabase connection string |
| `SECRET_KEY` | `your-super-secret-key-here-change-this-in-production` | Random string for JWT tokens |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token expiration time |

5. **Click "Save Changes"**

### **Step 6: Redeploy Backend**

1. **Go to your Render service**
2. **Click "Manual Deploy" → "Deploy latest commit"**
3. **Wait for deployment to complete** (2-3 minutes)

### **Step 7: Verify Setup**

1. **Test health endpoint:**
   ```bash
   curl https://garments-pos-backend.onrender.com/health
   ```

2. **Test database connection:**
   ```bash
   curl https://garments-pos-backend.onrender.com/debug/users
   ```

3. **Test login with default credentials:**
   - Username: `admin`
   - Password: `admin123`

## 🔧 Troubleshooting

### **Common Issues**

#### **1. Connection Failed**
- **Check**: Database password is correct
- **Check**: Connection string format is valid
- **Check**: Supabase project is active

#### **2. Tables Not Created**
- **Solution**: The `setup_database.py` script runs on startup
- **Check**: Render logs for any errors

#### **3. Authentication Issues**
- **Check**: `SECRET_KEY` is set correctly
- **Check**: Environment variables are saved

#### **4. CORS Issues**
- **Check**: Frontend URL is in CORS allowlist
- **Solution**: Backend CORS is already configured

### **Useful Commands**

```bash
# Test database connection
curl https://garments-pos-backend.onrender.com/debug/users

# Test health
curl https://garments-pos-backend.onrender.com/health

# Check deployment status
curl https://garments-pos-backend.onrender.com/
```

## 📊 Supabase Dashboard Features

Once set up, you can use Supabase dashboard for:

- **Database Browser**: View and edit data directly
- **SQL Editor**: Run custom queries
- **API Documentation**: View auto-generated API docs
- **Authentication**: Manage users (optional)
- **Storage**: File storage (if needed later)

## 🔒 Security Best Practices

1. **Never commit database passwords** to Git
2. **Use environment variables** for all sensitive data
3. **Regularly rotate** your `SECRET_KEY`
4. **Monitor** your Supabase usage (free tier limits)
5. **Backup** your database regularly

## 📈 Free Tier Limits

Supabase free tier includes:
- **500MB database**
- **2GB bandwidth**
- **50,000 monthly active users**
- **Unlimited API requests**

This is sufficient for most small to medium POS systems.

## 🎉 Success Indicators

Your setup is successful when:
- ✅ Health endpoint returns `{"status": "healthy"}`
- ✅ Debug users endpoint returns user list
- ✅ Login works with admin/admin123
- ✅ Dealer creation works without errors
- ✅ Data persists across deployments

## 📞 Support

If you encounter issues:
1. Check Render deployment logs
2. Verify Supabase connection string
3. Test locally with `setup_supabase.py`
4. Check environment variables in Render

---

**🎯 You're all set! Your POS system now has a persistent, scalable database that won't reset on deployments.** 