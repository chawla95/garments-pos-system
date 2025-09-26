#!/bin/bash

echo "Setting up environment variables for Vercel..."

# Set the environment variable
echo "https://garments-pos-backend-92s1.onrender.com" | npx vercel env add REACT_APP_API_URL production

echo "Environment variable set successfully!"
echo "You may need to redeploy for the changes to take effect:"
echo "npx vercel --prod" 