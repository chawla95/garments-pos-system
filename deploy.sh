#!/bin/bash

# Pre-Deployment Script
# Runs comprehensive tests before deployment to catch errors early

set -e  # Exit on any error

echo "🚀 Starting Pre-Deployment Process..."
echo "=================================="

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

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    print_error "Not in the correct directory. Please run this from the project root."
    exit 1
fi

print_status "Directory check passed"

# Check if required files exist
required_files=("requirements.txt" "render.yaml" "main.py" "database.py" "models.py" "schemas.py")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Required file missing: $file"
        exit 1
    fi
done

print_status "Required files check passed"

# Check environment variables
if [ -z "$DATABASE_URL" ]; then
    print_error "DATABASE_URL environment variable is not set"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    print_error "SECRET_KEY environment variable is not set"
    exit 1
fi

print_status "Environment variables check passed"

# Run pre-deployment tests
echo ""
echo "🧪 Running Pre-Deployment Tests..."
echo "=================================="

if python test_pre_deployment.py; then
    print_status "Pre-deployment tests passed"
else
    print_error "Pre-deployment tests failed"
    echo ""
    echo "🔧 Please fix the errors above before deploying"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_warning "You have uncommitted changes"
    echo "Current changes:"
    git status --short
    echo ""
    read -p "Do you want to commit these changes before deploying? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git add .
        git commit -m "Auto-commit before deployment"
        print_status "Changes committed"
    else
        print_warning "Proceeding with uncommitted changes"
    fi
fi

# Check if we're on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    print_warning "You're not on the main branch (currently on: $current_branch)"
    read -p "Do you want to switch to main branch? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout main
        print_status "Switched to main branch"
    fi
fi

# Pull latest changes
echo ""
echo "📥 Pulling latest changes..."
git pull origin main
print_status "Latest changes pulled"

# Run additional checks
echo ""
echo "🔍 Running Additional Checks..."
echo "================================"

# Check for Python syntax errors
if python -m py_compile main.py; then
    print_status "Python syntax check passed"
else
    print_error "Python syntax errors found"
    exit 1
fi

# Check for import errors
if python -c "import main; print('Import check passed')" 2>/dev/null; then
    print_status "Import check passed"
else
    print_error "Import errors found"
    exit 1
fi

# Test database connection
echo ""
echo "🗄️  Testing Database Connection..."
echo "=================================="

if python -c "
import os
from database import engine
with engine.connect() as conn:
    result = conn.execute('SELECT 1')
    print('Database connection successful')
"; then
    print_status "Database connection test passed"
else
    print_error "Database connection failed"
    exit 1
fi

# Check Render configuration
echo ""
echo "⚙️  Checking Render Configuration..."
echo "==================================="

if [ -f "render.yaml" ]; then
    if python -c "
import yaml
with open('render.yaml', 'r') as f:
    config = yaml.safe_load(f)
    if 'services' in config:
        print('Render configuration valid')
    else:
        raise Exception('Invalid render.yaml structure')
"; then
        print_status "Render configuration check passed"
    else
        print_error "Render configuration has issues"
        exit 1
    fi
else
    print_error "render.yaml file not found"
    exit 1
fi

# Final deployment readiness check
echo ""
echo "🎯 Final Deployment Readiness Check"
echo "==================================="

print_status "All pre-deployment checks passed!"
echo ""
echo "🚀 Ready to deploy!"
echo ""
echo "Next steps:"
echo "1. Push to main branch: git push origin main"
echo "2. Monitor deployment on Render dashboard"
echo "3. Check deployment logs for any issues"
echo ""
echo "Deployment will automatically trigger on Render when you push to main."

# Optional: Auto-push to trigger deployment
read -p "Do you want to push to main now to trigger deployment? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "📤 Pushing to main branch..."
    git push origin main
    print_status "Deployment triggered!"
    echo ""
    echo "🔗 Monitor your deployment at: https://dashboard.render.com"
else
    echo ""
    print_warning "Deployment not triggered. Push manually when ready."
fi

echo ""
echo "✅ Pre-deployment process completed successfully!" 