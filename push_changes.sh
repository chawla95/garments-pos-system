#!/bin/bash

echo "🚀 Pushing changes from chat session to GitHub..."

echo "📁 Adding modified files..."
git add render.yaml

echo "💾 Committing changes..."
git commit -m "Fix build command to use python -m pip for Render deployment"

echo "📤 Pushing to GitHub..."
git push origin main

echo "✅ Changes pushed successfully!"
echo "🔗 Check your repository: https://github.com/chawla95/garments-pos-system" 