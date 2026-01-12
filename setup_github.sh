#!/bin/bash
# GitHub Setup Script for DataGuard

echo "🚀 DataGuard - GitHub Setup"
echo "================================"
echo ""

# Check if git user is configured
if ! git config user.name > /dev/null 2>&1; then
    echo "⚠️  Git user not configured. Let's set it up."
    echo ""
    read -p "Enter your GitHub username: " github_username
    read -p "Enter your email: " github_email
    
    git config --global user.name "$github_username"
    git config --global user.email "$github_email"
    
    echo ""
    echo "✅ Git configured!"
else
    echo "✅ Git already configured as: $(git config user.name)"
fi

echo ""
echo "================================"
echo "📋 Next Steps:"
echo "================================"
echo ""
echo "1. Create a GitHub repository:"
echo "   → Go to: https://github.com/new"
echo "   → Name: dataguard"
echo "   → Keep it Public (required for Render free tier)"
echo "   → Click 'Create repository'"
echo ""
echo "2. Then run these commands:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/dataguard.git"
echo "   git push -u origin main"
echo ""
echo "3. Deploy to Render:"
echo "   → Go to: https://render.com"
echo "   → Sign up with GitHub"
echo "   → New → Web Service"
echo "   → Connect your 'dataguard' repo"
echo "   → Click 'Create Web Service'"
echo ""
echo "4. See CHECKLIST.md for complete launch plan"
echo ""
echo "================================"
echo "🛡️  Your API is ready to launch!"
echo "================================"
