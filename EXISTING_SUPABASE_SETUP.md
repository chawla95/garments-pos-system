# Configuring Your Existing Supabase Project

Since you already have a Supabase project, let's configure it for your Garments POS System.

## Step 1: Get Your Connection String

1. **Go to your Supabase project dashboard**
2. **Navigate to Settings → Database**
3. **Find the "Connection string" section**
4. **Copy the "URI" connection string** (it looks like):
   ```
   postgresql://postgres:[password]@[host]:5432/postgres
   ```

## Step 2: Run the Setup Script

Run the automated setup script to configure your database:

```bash
python setup_supabase.py
```

This script will:
- ✅ Test your database connection
- ✅ Create all necessary tables
- ✅ Set up an admin user
- ✅ Generate environment variables file

## Step 3: Verify Database Tables

After running the setup script, you should see these tables in your Supabase dashboard:

### Core Tables
- `users` - User accounts and authentication
- `products` - Product catalog
- `inventory_items` - Stock management
- `invoices` - Sales transactions
- `customers` - Customer information

### Supporting Tables
- `dealers` - Supplier information
- `brands` - Brand information
- `returns` - Return transactions
- `cash_registers` - Cash register sessions
- `whatsapp_logs` - WhatsApp message logs
- `loyalty_transactions` - Customer loyalty points
- `cash_expenses` - Cash register expenses

## Step 4: Environment Variables for Render

Copy these variables to your Render dashboard:

### Required Variables
```
DATABASE_URL=your_supabase_connection_string
SECRET_KEY=your-super-secret-key-change-this-in-production
```

### Optional Variables (with defaults)
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

## Step 5: Deploy to Render

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Configure for existing Supabase"
   git push origin main
   ```

2. **Deploy using the script**:
   ```bash
   ./deploy_to_render.sh
   ```

3. **Or manually deploy**:
   - Go to [render.com](https://render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Set the environment variables above

## Step 6: Test Your Deployment

After deployment, test these endpoints:

### Health Check
```bash
curl https://your-app-name.onrender.com/health
```

### API Documentation
Visit: `https://your-app-name.onrender.com/docs`

### Login Test
- **Username**: `admin`
- **Password**: `admin123`

## Database Schema Overview

Your Supabase project will contain these main tables:

### Users & Authentication
```sql
users (
  id, username, email, full_name, role, 
  is_active, created_at, updated_at
)
```

### Product Management
```sql
products (
  id, name, description, category, 
  brand_id, dealer_id, created_at
)

inventory_items (
  id, product_id, barcode, size, 
  color, quantity, cost_price, 
  selling_price, created_at
)
```

### Sales & Transactions
```sql
invoices (
  id, invoice_number, customer_id, 
  total_amount, gst_amount, 
  payment_method, created_at
)

invoice_items (
  id, invoice_id, inventory_item_id, 
  quantity, unit_price, total_price
)
```

### Customer Management
```sql
customers (
  id, name, phone, email, address, 
  loyalty_points, created_at
)
```

## Troubleshooting

### Common Issues

1. **Connection Failed**:
   - Verify your connection string is correct
   - Check if your Supabase project is active
   - Ensure the database password is correct

2. **Tables Not Created**:
   - Run `python setup_supabase.py` again
   - Check the logs for any errors
   - Verify the DATABASE_URL is set correctly

3. **Authentication Issues**:
   - Check if the admin user was created
   - Verify the SECRET_KEY is set
   - Try logging in with admin/admin123

### Testing Commands

```bash
# Test database connection
python -c "from database import engine; print('DB OK')"

# Test admin user creation
python -c "from database import SessionLocal; from models import User; db = SessionLocal(); user = db.query(User).filter(User.username == 'admin').first(); print('Admin exists:', user is not None)"

# Test API health
curl https://your-app-name.onrender.com/health
```

## Security Considerations

1. **Change Default Password**: Change admin password after first login
2. **Secure SECRET_KEY**: Use a strong, random secret key
3. **Database Access**: Limit database access to your application only
4. **Environment Variables**: Never commit sensitive data to your repository

## Monitoring

### Supabase Dashboard
- **Database**: Monitor table sizes and query performance
- **Logs**: Check for any database errors
- **Usage**: Monitor your free tier limits

### Render Dashboard
- **Logs**: Check application logs for errors
- **Metrics**: Monitor response times and errors
- **Deployments**: Track deployment status

## Next Steps

After successful deployment:

1. **Test all features**: Create products, make sales, etc.
2. **Configure shop details**: Update shop name, address, etc.
3. **Set up WhatsApp**: Configure WhatsApp Business API (optional)
4. **Monitor usage**: Keep an eye on Supabase and Render usage
5. **Scale up**: Upgrade plans when needed

## Support

If you encounter issues:

1. **Check Supabase logs**: Go to your Supabase dashboard → Logs
2. **Check Render logs**: Go to your Render service → Logs
3. **Test locally**: Run the setup script locally to debug
4. **Review environment variables**: Ensure all required variables are set

Your existing Supabase project is now ready to power your Garments POS System! 🎉 