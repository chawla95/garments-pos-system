#!/bin/bash

echo "Adding deployment files to git..."
git add render.yaml build.sh pos-frontend/vercel.json

echo "Committing deployment files..."
git commit -m "Add deployment configuration for Vercel and Render"

echo "Pushing to GitHub..."
git push origin main

echo "Deployment files have been added to the repository!" 