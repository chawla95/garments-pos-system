#!/bin/bash

echo "🚀 Fresh Vercel Deployment for Garments POS Frontend"
echo "=================================================="

# Navigate to frontend directory (if not already there)
cd "$(dirname "$0")"

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
echo "This will create a new project. Follow the prompts:"
echo "1. Choose 'Y' to set up and deploy"
echo "2. Select your scope/account"
echo "3. Choose 'N' to create a new project"
echo "4. Enter project name: pos-frontend"
echo "5. Choose 'Y' to override settings"

# Force new deployment
npx vercel --prod

echo ""
echo "✅ Fresh deployment initiated!"
echo "🌐 Your frontend will be live at the URL provided above"
echo "🔗 Backend API: https://garments-pos-backend-92s1.onrender.com"
echo ""
echo "📝 Next steps:"
echo "1. Set environment variable: npx vercel env add REACT_APP_API_URL"
echo "2. Redeploy: npx vercel --prod" 