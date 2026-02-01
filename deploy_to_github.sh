#!/bin/bash

# GitHub Pages Deployment Script
# This script pushes your HTML reports to GitHub Pages

echo "=========================================="
echo "Deploying to GitHub Pages"
echo "=========================================="
echo

# Configuration
REPO_DIR="stock-reports-github"
GIT_BRANCH="main"  # or "gh-pages" if you prefer

# Check if repo directory exists
if [ ! -d "$REPO_DIR" ]; then
    echo "Error: Repository directory '$REPO_DIR' not found!"
    echo "Please run setup_github.sh first to initialize the repository."
    exit 1
fi

# Navigate to repo directory
cd "$REPO_DIR" || exit 1

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "Error: Not a git repository!"
    echo "Please run setup_github.sh first."
    exit 1
fi

# Add all changes
echo "Adding files to git..."
git add .

# Check if there are changes to commit
if git diff-index --quiet HEAD --; then
    echo "No changes to commit. Everything is up to date!"
    exit 0
fi

# Commit with timestamp
COMMIT_MSG="Update stock analysis - $(date '+%Y-%m-%d %H:%M:%S')"
echo "Committing changes: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# Push to GitHub
echo "Pushing to GitHub..."
git push origin "$GIT_BRANCH"

if [ $? -eq 0 ]; then
    echo
    echo "=========================================="
    echo "✓ Successfully deployed to GitHub Pages!"
    echo "=========================================="
    echo
    echo "Your site should be available at:"
    echo "https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/"
    echo
    echo "Note: It may take a few minutes for changes to appear."
else
    echo
    echo "✗ Failed to push to GitHub"
    echo "Please check your git configuration and credentials."
    exit 1
fi
