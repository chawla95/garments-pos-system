import axios from 'axios';

// Get API URL from environment or use default
const getApiUrl = () => {
  // Check for environment variable first
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // Check for Vercel environment variable
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}`;
  }
  
  // Default to the Azure backend
  return 'https://garments-pos-backend.azurewebsites.net';
};

const api = axios.create({
  baseURL: getApiUrl(),
  headers: {
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
  },
  timeout: 30000, // 30 second timeout for better reliability
});

// Debug: Log the API URL being used
console.log('API URL:', getApiUrl());
console.log('Current timestamp:', new Date().toISOString());

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling and token refresh
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only log network errors, don't show them as console errors
    if (error.code === 'ERR_NETWORK') {
      console.warn('Network Error (this may be expected for background requests):', error.message);
    } else {
      console.error('API Error:', error.response?.data || error.message);
    }
    
    // Handle 401 Unauthorized errors
    if (error.response?.status === 401) {
      console.warn('Token expired, clearing authentication');
      // Clear invalid token
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Redirect to login if not already on login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/';
      }
    }
    
    // Handle timeout errors
    if (error.code === 'ECONNABORTED') {
      console.warn('Request timeout - this may be due to slow backend response');
    }
    
    return Promise.reject(error);
  }
);

export default api; 