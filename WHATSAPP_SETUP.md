# WhatsApp Business API Setup Guide

## 🔧 How to Configure WhatsApp Messaging

The WhatsApp messaging feature requires a WhatsApp Business API account. Here's how to set it up:

### 📋 Prerequisites
1. A WhatsApp Business account
2. A phone number for your business
3. API access (we use Interakt.ai as the provider)

### 🚀 Step-by-Step Setup

#### 1. Sign up for Interakt.ai
- Go to [https://interakt.ai](https://interakt.ai)
- Create an account
- Complete the verification process

#### 2. Set up WhatsApp Business API
- In your Interakt dashboard, go to "WhatsApp Business API"
- Add your business phone number
- Complete the verification process with WhatsApp
- Get your API credentials

#### 3. Get Your API Credentials
From your Interakt dashboard, you'll need:
- **API Key**: Your Interakt API key
- **API Secret**: Your Interakt API secret
- **Phone Number ID**: Your WhatsApp phone number ID
- **Business Account ID**: Your business account ID

#### 4. Configure in the POS System

**Option A: Using the Web Interface (Recommended)**
1. Login to your POS system as admin
2. Click on "⚙️ Config" in the navigation
3. Go to "📱 WhatsApp Configuration" tab
4. Enter your API credentials
5. Click "Save WhatsApp Configuration"

**Option B: Using Environment Variables**
Create a `.env` file in the `garments_pos` directory:

```bash
# WhatsApp Business API Configuration
INTERAKT_API_KEY=your_interakt_api_key_here
INTERAKT_API_SECRET=your_interakt_api_secret_here
INTERAKT_PHONE_NUMBER_ID=your_phone_number_id_here
INTERAKT_BUSINESS_ACCOUNT_ID=your_business_account_id_here
```

#### 5. Test the Configuration
1. Go to the WhatsApp Manager in your POS system
2. Try sending a test message
3. Check the message logs for delivery status

### 🔍 Troubleshooting

#### "Error sending message" Issues:
1. **Check API Credentials**: Ensure all 4 credentials are correctly entered
2. **Verify Phone Number**: Make sure your WhatsApp phone number is verified
3. **Check Account Status**: Ensure your Interakt account is active
4. **Test API Connection**: Use the configuration page to verify status

#### Common Error Messages:
- `"API Error: 401"` - Invalid API credentials
- `"API Error: 403"` - Insufficient permissions
- `"API Error: 400"` - Invalid phone number format
- `"Network Error"` - Check internet connection

### 📞 Support
- **Interakt Support**: [https://interakt.ai/support](https://interakt.ai/support)
- **WhatsApp Business API Docs**: [https://developers.facebook.com/docs/whatsapp](https://developers.facebook.com/docs/whatsapp)

### 💡 Tips
1. **Start with Test Numbers**: Use test phone numbers first
2. **Monitor Message Logs**: Check delivery status in the WhatsApp Manager
3. **Template Messages**: Use pre-approved message templates for better delivery rates
4. **Rate Limits**: Be aware of WhatsApp's messaging rate limits

### 🔒 Security Notes
- Never share your API credentials
- Use environment variables in production
- Regularly rotate your API keys
- Monitor your API usage

---

**Need Help?** Check the configuration status in the "⚙️ Config" section of your POS system. 