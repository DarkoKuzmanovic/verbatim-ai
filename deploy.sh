#!/bin/bash

# Default BASE_PATH
BASE_PATH=""

# Read BASE_PATH from .env file if it exists
if [ -f .env ]; then
    # Extract BASE_PATH, removing potential quotes
    BASE_PATH=$(grep -E '^BASE_PATH=' .env | cut -d '=' -f2- | sed 's/"//g')
fi

# Determine Nginx location and proxy path
if [ -z "$BASE_PATH" ]; then
  LOCATION="/"
  PROXY_PASS_PATH="/"
else
  LOCATION="$BASE_PATH/"
  PROXY_PASS_PATH="$BASE_PATH/"
fi

# Generate the Nginx configuration file using a heredoc
cat > generated_nginx.conf <<EOL
# Generated Nginx Configuration
#
# Include this in your server block in your main nginx.conf
# e.g., include /path/to/your/project/generated_nginx.conf;

location ${LOCATION} {
    proxy_pass http://localhost:8000${PROXY_PASS_PATH};
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;

    # Required for long AI processing times
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
    proxy_read_timeout 300s;
}
EOL

echo "✅ Nginx configuration generated in 'generated_nginx.conf'."
echo ""
echo "---"
echo "Next Steps:"
echo "1. Install dependencies: pip install -r requirements.txt"
echo "2. Run the server: python start.py"
echo "---"