#!/bin/bash

# GitHub Repository Setup Script
# Sets up a local git repository for GitHub Pages deployment

echo "=========================================="
echo "GitHub Pages Repository Setup"
echo "=========================================="
echo

# Get repository information
read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter your repository name (e.g., stock-analysis): " REPO_NAME

REPO_DIR="stock-reports-github"
REPO_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

echo
echo "Repository URL: $REPO_URL"
echo "Local directory: $REPO_DIR"
echo

# Check if directory already exists
if [ -d "$REPO_DIR" ]; then
    read -p "Directory $REPO_DIR already exists. Remove it? (y/n): " REMOVE
    if [ "$REMOVE" = "y" ]; then
        rm -rf "$REPO_DIR"
        echo "Removed existing directory."
    else
        echo "Using existing directory."
    fi
fi

# Create directory if it doesn't exist
mkdir -p "$REPO_DIR"
cd "$REPO_DIR" || exit 1

# Check if it's already a git repo
if [ -d ".git" ]; then
    echo "Git repository already initialized."
else
    echo "Initializing git repository..."
    git init
    git branch -M main
fi

# Create .gitignore
echo "Creating .gitignore..."
cat > .gitignore << EOF
# Ignore these files
*.log
.DS_Store
Thumbs.db
EOF

# Create README
echo "Creating README.md..."
cat > README.md << EOF
# Stock Investment Analysis Reports

AI-powered stock analysis using multi-agent system with local Ollama models.

## Latest Reports

- [View Dashboard](https://\${GITHUB_USERNAME}.github.io/\${REPO_NAME}/)

## Features

- 4 specialized AI agents analyzing stocks
- News sentiment analysis
- Statistical predictions using time series
- Fundamental analysis
- Investment recommendations

## Disclaimer

This is for educational purposes only. Not financial advice.

---

Last updated: $(date '+%Y-%m-%d')
EOF

# Add placeholder index.html if none exists
if [ ! -f "index.html" ]; then
    echo "Creating placeholder index.html..."
    cat > index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Stock Analysis</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            text-align: center;
        }
        h1 { color: #333; }
        p { color: #666; line-height: 1.6; }
    </style>
</head>
<body>
    <h1>📊 Stock Investment Analysis</h1>
    <p>Reports will appear here after the first analysis run.</p>
    <p>Check back soon!</p>
</body>
</html>
EOF
fi

# Set remote
echo "Setting up remote repository..."
git remote remove origin 2>/dev/null  # Remove if exists
git remote add origin "$REPO_URL"

# Initial commit
echo "Creating initial commit..."
git add .
git commit -m "Initial commit - Setup GitHub Pages" || echo "Nothing to commit"

echo
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo
echo "Next steps:"
echo
echo "1. Create the repository on GitHub:"
echo "   → Go to https://github.com/new"
echo "   → Name it: $REPO_NAME"
echo "   → Make it public"
echo "   → DO NOT initialize with README"
echo
echo "2. Push your code:"
echo "   → cd $REPO_DIR"
echo "   → git push -u origin main"
echo
echo "3. Enable GitHub Pages:"
echo "   → Go to repository Settings > Pages"
echo "   → Source: Deploy from branch"
echo "   → Branch: main, folder: / (root)"
echo "   → Save"
echo
echo "4. Your site will be available at:"
echo "   https://$GITHUB_USERNAME.github.io/$REPO_NAME/"
echo
echo "After running your analysis, use deploy_to_github.sh to push updates."
echo
