#!/bin/bash

# Git setup script for deployment
echo "🚀 Setting up Git repository for deployment..."

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Add all files
echo "📝 Adding files to Git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Video-to-Audio API service

- Lightweight Flask API for video-to-audio conversion
- Optimized for Render.com free tier (512MB RAM)
- Automatic file cleanup and memory management
- Docker-based deployment with FFmpeg pre-installed
- Supports multiple video formats (MP4, AVI, MOV, etc.)
- RESTful API with upload and download endpoints"

# Set main branch
echo "🌿 Setting main branch..."
git branch -M main

echo ""
echo "✅ Git setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Copy the repository URL"
echo "3. Run: git remote add origin <your-repo-url>"
echo "4. Run: git push -u origin main"
echo "5. Connect the repository to Render.com"
echo ""
echo "🔗 Example:"
echo "   git remote add origin https://github.com/yourusername/video-to-audio-api.git"
echo "   git push -u origin main"
echo ""
echo "🌐 Then go to https://render.com and create a new Web Service"
