// Debug script to check authentication status
console.log('=== Authentication Debug ===');

// Check if token exists
const token = localStorage.getItem('token');
console.log('Token exists:', !!token);
if (token) {
  console.log('Token length:', token.length);
  console.log('Token preview:', token.substring(0, 20) + '...');
}

// Check if user data exists
const user = localStorage.getItem('user');
console.log('User data exists:', !!user);
if (user) {
  try {
    const userObj = JSON.parse(user);
    console.log('User:', userObj);
  } catch (e) {
    console.log('Invalid user data in localStorage');
  }
}

// Check current URL
console.log('Current URL:', window.location.href);

// Check if we're on login page
console.log('On login page:', window.location.pathname === '/');

// Test API URL
const apiUrl = process.env.REACT_APP_API_URL || 'https://garments-pos-backend-92s1.onrender.com';
console.log('API URL:', apiUrl);

// Test backend connectivity
fetch(`${apiUrl}/health`, { method: 'GET' })
  .then(response => {
    console.log('Backend health check status:', response.status);
    return response.text();
  })
  .then(data => {
    console.log('Backend health response:', data);
  })
  .catch(error => {
    console.error('Backend health check failed:', error);
  });

console.log('=== Debug Complete ==='); 