# Supabase Database Setup for Render Deployment

This guide will help you set up a Supabase PostgreSQL database for your Garments POS System deployment on Render.

## Step 1: Create Supabase Project

1. **Go to Supabase**: Visit [supabase.com](https://supabase.com)
2. **Sign Up/Login**: Create an account or sign in
3. **Create New Project**:
   - Click "New Project"
   - Choose your organization
   - Enter project name: `garments-pos-system`
   - Enter database password (save this!)
   - Choose a region close to your users
   - Click "Create new project"

## Step 2: Get Database Connection String

1. **Go to Settings**: In your Supabase dashboard, click "Settings" (gear icon)
2. **Database**: Click "Database" in the sidebar
3. **Connection String**: Find the "Connection string" section
4. **Copy URI**: Copy the connection string that looks like:
   ```
   postgresql://postgres:[password]@[host]:5432/postgres
   ```

## Step 3: Configure Database Security

1. **Go to Settings > Database**
2. **Connection Pooling**: Enable connection pooling (optional but recommended)
3. **Row Level Security**: You can disable this for now (we'll handle security in the app)

## Step 4: Test Database Connection

You can test the connection using the Supabase SQL editor:

1. **Go to SQL Editor** in your Supabase dashboard
2. **Run this query** to test:
   ```sql
   SELECT version();
   ```

## Step 5: Environment Variables for Render

When deploying to Render, you'll need these environment variables:

### Required Variables
```
DATABASE_URL=postgresql://postgres:[your_password]@[your_host]:5432/postgres
SECRET_KEY=your-super-secret-key-change-this-in-production
```

### Optional Variables
```
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

## Step 6: Database Schema

The application will automatically create all necessary tables when it starts. The main tables include:

- `users` - User accounts and authentication
- `products` - Product catalog
- `inventory_items` - Stock management
- `invoices` - Sales transactions
- `customers` - Customer information
- `dealers` - Supplier information
- `brands` - Brand information
- `returns` - Return transactions
- `cash_registers` - Cash register sessions
- `whatsapp_logs` - WhatsApp message logs

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Check if your database password is correct
   - Verify the host URL is correct
   - Ensure your IP is not blocked

2. **Authentication Failed**:
   - Double-check your database password
   - Make sure you're using the correct connection string format

3. **Database Not Found**:
   - The database name should be `postgres` (default)
   - Check if your Supabase project is active

### Testing Connection

You can test your database connection locally:

```bash
# Install psql (PostgreSQL client)
# On macOS: brew install postgresql
# On Ubuntu: sudo apt-get install postgresql-client

# Test connection
psql "postgresql://postgres:[password]@[host]:5432/postgres"
```

## Security Best Practices

1. **Strong Passwords**: Use a strong password for your database
2. **Environment Variables**: Never commit database credentials to your code
3. **Connection Pooling**: Enable connection pooling in Supabase for better performance
4. **Backup**: Supabase provides automatic backups, but you can also set up manual backups

## Cost Information

- **Supabase Free Tier**: 
  - 500MB database
  - 2GB bandwidth
  - 50,000 monthly active users
  - Perfect for development and small production apps

- **Supabase Pro**: 
  - $25/month
  - 8GB database
  - 250GB bandwidth
  - 100,000 monthly active users

## Next Steps

After setting up Supabase:

1. **Deploy to Render**: Follow the main deployment guide
2. **Test the API**: Use the health endpoint to verify everything works
3. **Monitor Usage**: Check Supabase dashboard for database usage
4. **Scale Up**: Upgrade to Pro plan when needed

## Support

- **Supabase Docs**: [supabase.com/docs](https://supabase.com/docs)
- **Supabase Discord**: [discord.supabase.com](https://discord.supabase.com)
- **Render Support**: [render.com/docs](https://render.com/docs) 