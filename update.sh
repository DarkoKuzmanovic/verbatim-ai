#!/bin/bash

# Production Server Update Script
# This script automates the process of updating the production server.

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
APP_DIR="/var/www/app.quz.ma/verbatim-ai"
LOG_FILE="/tmp/verbatim-ai.log"
HEALTH_CHECK_URL_LOCAL="http://localhost:8001/health"
HEALTH_CHECK_URL_PUBLIC="https://app.quz.ma/verbatim-ai/health"

# --- Script Logic ---

# Function to print colored output
print_status() {
  echo -e "\033[1;34m>>> $1\033[0m"
}

print_success() {
  echo -e "\033[1;32m✅ $1\033[0m"
}

print_warning() {
  echo -e "\033[1;33m⚠️  $1\033[0m"
}

print_error() {
  echo -e "\033[1;31m❌ $1\033[0m"
}

# 1. Navigate to the project directory
if [ -n "$APP_DIR" ]; then
  print_status "Changing directory to $APP_DIR"
  cd "$APP_DIR" || { print_error "Failed to change directory to $APP_DIR"; exit 1; }
fi

# 2. Save any local server changes
print_status "Stashing any local changes..."
git stash push -m "Auto-stash before update on $(date)"

# 3. Pull latest changes from GitHub
print_status "Pulling latest changes from origin/main..."
git pull origin main

# 4. Update dependencies if requirements.txt changed
print_status "Checking for dependency updates..."
if git diff --name-only HEAD~1 HEAD | grep -q "requirements.txt"; then
  print_status "requirements.txt changed. Updating dependencies..."
  # Assuming virtual environment is in 'venv' and activated
  if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    print_success "Dependencies updated."
  else
    print_warning "Virtual environment 'venv' not found. Skipping dependency update."
  fi
else
  print_status "No dependency changes detected."
fi

# 5. Check if .env needs updating
print_status "Checking for environment variable updates..."
if [ -f ".env.example" ] && [ -f ".env" ]; then
  # This command finds lines in .env.example that are not in .env
  NEW_VARS=$(comm -13 <(grep -v '^#' .env | grep -v '^$' | cut -d'=' -f1 | sort) <(grep -v '^#' .env.example | grep -v '^$' | cut -d'=' -f1 | sort))
  if [ -n "$NEW_VARS" ]; then
    print_warning "New environment variables detected in .env.example:"
    echo "$NEW_VARS"
    print_warning "Please update your .env file manually if needed."
  else
    print_success "No new environment variables detected."
  fi
else
  print_warning ".env or .env.example not found. Skipping environment check."
fi

# 6. Restart the application
print_status "Restarting the application with PM2..."
if command -v pm2 &> /dev/null; then
  pm2 restart verbatim-ai --update-env
  print_success "Application restarted via PM2."
else
  print_warning "PM2 not found. Using fallback method..."
  pkill -9 -f "uvicorn.*main:app" || print_warning "No running uvicorn process found to kill."
  nohup bash start.sh > "$LOG_FILE" 2>&1 &
  print_success "Application restart initiated."
fi

# 7. Verify it's working
print_status "Waiting for the application to start..."
sleep 5

print_status "Performing health check on $HEALTH_CHECK_URL_LOCAL..."
if curl -s -f "$HEALTH_CHECK_URL_LOCAL" > /dev/null; then
  print_success "Local health check passed."
else
  print_error "Local health check failed. Check the logs: tail -f $LOG_FILE"
  # Optionally, you could exit here if the local check fails
  # exit 1
fi

print_status "Performing health check on $HEALTH_CHECK_URL_PUBLIC..."
if curl -s -f "$HEALTH_CHECK_URL_PUBLIC" > /dev/null; then
  print_success "Public health check passed."
else
  print_error "Public health check failed. Check Nginx configuration and logs."
fi

print_success "Production server update complete!"