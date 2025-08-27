#!/bin/bash
# Script to update GitHub repository description from README.md
# Usage: ./update-description.sh [github_token] [repo_owner] [repo_name]

set -e

# Check if arguments are provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 [github_token] [repo_owner] [repo_name]"
    echo "Or set environment variables: GITHUB_TOKEN, GITHUB_REPOSITORY"
    exit 1
fi

# Get repository information
if [ $# -eq 3 ]; then
    GITHUB_TOKEN=$1
    REPO_OWNER=$2
    REPO_NAME=$3
else
    # Try to get from environment
    if [ -z "$GITHUB_TOKEN" ] || [ -z "$GITHUB_REPOSITORY" ]; then
        echo "Error: Please provide GitHub token and repository information"
        exit 1
    fi
    REPO_OWNER=$(echo $GITHUB_REPOSITORY | cut -d'/' -f1)
    REPO_NAME=$(echo $GITHUB_REPOSITORY | cut -d'/' -f2)
fi

# Extract description from README.md
DESCRIPTION=$(sed -n '/^# Verbatim AI/,/^## /{ /^# Verbatim AI/d; /^## /d; p; }' README.md | head -1 | sed 's/^A //')

if [ -z "$DESCRIPTION" ]; then
    echo "Error: Could not extract description from README.md"
    exit 1
fi

echo "Updating repository description to: $DESCRIPTION"

# Update repository description using GitHub API
curl -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/$REPO_OWNER/$REPO_NAME \
  -d "{\"description\":\"$DESCRIPTION\"}"

echo "Repository description updated successfully!"