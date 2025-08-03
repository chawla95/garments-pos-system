#!/usr/bin/env node

const axios = require('axios');

const API_BASE = 'http://127.0.0.1:8000';

async function testAuth() {
  try {
    console.log('🔐 Testing Authentication...\n');
    
    // Test login
    console.log('1. Testing login...');
    const loginResponse = await axios.post(`${API_BASE}/auth/login`, {
      username: 'admin',
      password: 'admin123'
    });
    
    const token = loginResponse.data.access_token;
    console.log('✅ Login successful');
    console.log(`Token: ${token.substring(0, 50)}...\n`);
    
    // Test RBAC endpoints
    console.log('2. Testing RBAC endpoints...');
    const headers = { Authorization: `Bearer ${token}` };
    
    const rbacResponse = await axios.get(`${API_BASE}/rbac/roles/summary`, { headers });
    console.log('✅ RBAC roles summary:', rbacResponse.data.length, 'roles found');
    
    const usersResponse = await axios.get(`${API_BASE}/auth/users`, { headers });
    console.log('✅ Users endpoint:', usersResponse.data.length, 'users found');
    
    const permissionsResponse = await axios.get(`${API_BASE}/rbac/permissions`, { headers });
    console.log('✅ Permissions endpoint:', permissionsResponse.data.length, 'permissions found');
    
    console.log('\n🎉 All authentication tests passed!');
    console.log('\n📝 To fix the frontend:');
    console.log('1. Clear your browser cache (Ctrl+F5 or Cmd+Shift+R)');
    console.log('2. Log out and log back in');
    console.log('3. The RBAC page should now work correctly');
    
  } catch (error) {
    console.error('❌ Test failed:', error.response?.data || error.message);
  }
}

testAuth(); 