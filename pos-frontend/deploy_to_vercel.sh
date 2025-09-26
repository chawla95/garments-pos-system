#!/bin/bash

echo "🚀 Creating Fresh Vercel Deployment for Garments POS Frontend..."

# Navigate to frontend directory
cd pos-frontend

# Clean up any existing build artifacts
echo "🧹 Cleaning up previous builds..."
rm -rf build
rm -rf .vercel
rm -rf node_modules
rm -f package-lock.json

# Install dependencies fresh
echo "📦 Installing dependencies..."
npm install

# Build the project
echo "🔨 Building the project..."
npm run build

# Check if build was successful
if [ ! -d "build" ]; then
    echo "❌ Build failed! Please check the build logs above."
    exit 1
fi

echo "✅ Build successful!"

# Deploy to Vercel with fresh configuration
echo "🚀 Deploying to Vercel..."
echo "This will create a new deployment. Follow the prompts if needed."

# Force new deployment
npx vercel --prod --force

echo "✅ Fresh deployment initiated!"
echo "🌐 Your frontend should be live at the URL provided above"
echo "🔗 Backend API: https://garments-pos-backend-92s1.onrender.com"
echo ""
echo "📝 If you need to set environment variables, run:"
echo "   npx vercel env add REACT_APP_API_URL" 