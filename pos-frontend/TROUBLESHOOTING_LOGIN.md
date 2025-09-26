# Login Troubleshooting Guide

## 🔍 **Issue: "Not authenticated" Error on Products Page**

### **Root Cause Analysis:**
The error `{"error":{"code":"HTTP_ERROR","message":"Not authenticated","type":"HTTPException"}}` indicates that:
1. You're not logged in, OR
2. Your authentication token has expired, OR
3. The token is not being sent with requests

## 🚀 **Step-by-Step Troubleshooting:**

### **Step 1: Check if you're logged in**
1. Open your browser console (F12 → Console)
2. Run this command:
```javascript
console.log('Token:', localStorage.getItem('token'));
console.log('User:', localStorage.getItem('user'));
```

**Expected Result:** You should see a token and user data.

### **Step 2: Check API URL**
In the browser console, look for:
```
API URL: https://garments-pos-backend-92s1.onrender.com
```

### **Step 3: Test Login Process**
1. Go to: https://pos-frontend-final-k4io3yvya-abhisheks-projects-f92c4bb9.vercel.app
2. Try logging in with:
   - **Username:** admin
   - **Password:** admin123
3. Check if you get redirected after login
4. Check if token is stored in localStorage

### **Step 4: Check Network Requests**
1. Open Developer Tools (F12)
2. Go to **Network** tab
3. Try to access the Products page
4. Look for the request to `/products`
5. Check:
   - **Request Headers:** Should include `Authorization: Bearer [token]`
   - **Response Status:** Should be 200, not 401

### **Step 5: Clear Browser Data (if needed)**
If the above steps don't work:
1. Clear browser cache and cookies
2. Try logging in again
3. Check if the issue persists

## 🔧 **Quick Fixes:**

### **Fix 1: Force Re-login**
```javascript
// In browser console
localStorage.clear();
window.location.reload();
```

### **Fix 2: Check Token Format**
```javascript
// In browser console
const token = localStorage.getItem('token');
console.log('Token format:', token ? 'Bearer ' + token.substring(0, 20) + '...' : 'No token');
```

### **Fix 3: Test Backend Directly**
```bash
# Get a fresh token
curl -X POST "https://garments-pos-backend-92s1.onrender.com/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Test products endpoint with token
curl -X GET "https://garments-pos-backend-92s1.onrender.com/products" \
  -H "Authorization: Bearer [YOUR_TOKEN_HERE]"
```

## 🎯 **Common Issues & Solutions:**

### **Issue 1: Token Missing**
**Symptoms:** `localStorage.getItem('token')` returns null
**Solution:** Log in again

### **Issue 2: Token Expired**
**Symptoms:** 401 error with valid token
**Solution:** Log in again to get fresh token

### **Issue 3: Wrong API URL**
**Symptoms:** Network errors or wrong backend
**Solution:** Check environment variable `REACT_APP_API_URL`

### **Issue 4: CORS Issues**
**Symptoms:** CORS errors in console
**Solution:** Backend CORS is configured correctly, check network tab

## 📊 **Backend Status:**
- ✅ **Backend URL:** https://garments-pos-backend-92s1.onrender.com
- ✅ **Login Endpoint:** `/auth/login`
- ✅ **Products Endpoint:** `/products` (requires admin auth)
- ✅ **Authentication:** JWT Bearer token

## 🔍 **Debug Commands:**

### **Check Authentication Status:**
```javascript
// Run in browser console
console.log('=== Auth Debug ===');
console.log('Token exists:', !!localStorage.getItem('token'));
console.log('User exists:', !!localStorage.getItem('user'));
console.log('Current URL:', window.location.href);
console.log('API URL:', process.env.REACT_APP_API_URL || 'https://garments-pos-backend-92s1.onrender.com');
```

### **Test API Call:**
```javascript
// Run in browser console
const token = localStorage.getItem('token');
if (token) {
  fetch('https://garments-pos-backend-92s1.onrender.com/products', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  })
  .then(response => {
    console.log('Status:', response.status);
    return response.json();
  })
  .then(data => {
    console.log('Products:', data);
  })
  .catch(error => {
    console.error('Error:', error);
  });
} else {
  console.log('No token found');
}
```

## 🎉 **Expected Flow:**
1. Visit frontend URL
2. Login with admin/admin123
3. Get redirected to dashboard
4. Navigate to Products page
5. See products list (no authentication error)

---

**If you're still having issues, please share:**
1. What you see in the browser console
2. The network tab response for the products request
3. Whether you can successfully log in
4. Any error messages displayed 