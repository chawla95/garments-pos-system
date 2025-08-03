#!/bin/bash

# Garments POS System - Render Deployment Script
# This script helps you deploy your backend to Render

set -e

echo "🚀 Garments POS System - Render Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository. Please initialize git first."
    echo "Run: git init && git add . && git commit -m 'Initial commit'"
    exit 1
fi

# Check if we have the required files
required_files=("main.py" "requirements.txt" "render.yaml" "startup_validation.py" "setup_database.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Missing required file: $file"
        exit 1
    fi
done

print_status "All required files found"

# Check if we have a remote repository
if ! git remote get-url origin &> /dev/null; then
    print_warning "No remote repository configured."
    echo "Please add your GitHub repository as origin:"
    echo "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    echo ""
    echo "Or if you already have a repository:"
    echo "git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
    exit 1
fi

# Get the remote URL
remote_url=$(git remote get-url origin)
print_status "Remote repository: $remote_url"

# Check if we have uncommitted changes
if ! git diff-index --quiet HEAD --; then
    print_warning "You have uncommitted changes."
    echo "Please commit your changes before deploying:"
    echo "git add ."
    echo "git commit -m 'Update for deployment'"
    exit 1
fi

print_status "No uncommitted changes found"

# Push to GitHub
echo ""
echo "📤 Pushing to GitHub..."
if git push origin main; then
    print_status "Successfully pushed to GitHub"
else
    print_error "Failed to push to GitHub"
    exit 1
fi

echo ""
echo "🎉 Deployment files are ready!"
echo ""
echo "Next steps:"
echo "1. Go to https://render.com"
echo "2. Sign up/Login with your GitHub account"
echo "3. Click 'New' → 'Blueprint'"
echo "4. Connect your GitHub repository"
echo "5. Render will automatically detect the render.yaml file"
echo "6. Set your environment variables:"
echo "   - DATABASE_URL (your Supabase PostgreSQL URL)"
echo "   - SECRET_KEY (a secure secret key)"
echo "7. Deploy!"
echo ""
echo "Your API will be available at: https://your-app-name.onrender.com"
echo "API Documentation: https://your-app-name.onrender.com/docs"
echo "Health Check: https://your-app-name.onrender.com/health"
echo ""
print_status "Deployment script completed successfully!" 