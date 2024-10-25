#!/bin/bash

# Server details
SERVER_IP="44.210.175.78"
PEM_FILE="synthetic.pem"
REPO_URL="https://github.com/bikramadhikari001/synthenic.git"

echo "Starting deployment process..."

# Check if PEM file exists
if [ ! -f "$PEM_FILE" ]; then
    echo "Error: PEM file ($PEM_FILE) not found!"
    exit 1
fi

# Ensure PEM file has correct permissions
chmod 400 $PEM_FILE

# Copy docker-compose.prod.yml to server
echo "Copying production docker-compose file..."
scp -i $PEM_FILE docker-compose.prod.yml ubuntu@$SERVER_IP:~/docker-compose.prod.yml

# SSH into server and deploy
echo "Connecting to server and deploying..."
ssh -i $PEM_FILE ubuntu@$SERVER_IP << 'EOF'
    set -e  # Exit on any error

    echo "Updating system packages..."
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose git nginx

    # Configure nginx
    echo "Configuring nginx..."
    sudo tee /etc/nginx/sites-available/synthenic << 'EON'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
    }
}
EON

    # Enable nginx site
    sudo ln -sf /etc/nginx/sites-available/synthenic /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    echo "Testing nginx configuration..."
    sudo nginx -t
    
    # Restart nginx
    echo "Restarting nginx..."
    sudo systemctl restart nginx

    # Start Docker service
    echo "Ensuring Docker is running..."
    sudo systemctl start docker
    sudo systemctl enable docker

    # Setup project directory
    echo "Setting up project directory..."
    if [ ! -d "~/synthenic" ]; then
        echo "Cloning repository..."
        git clone $REPO_URL ~/synthenic
    else
        echo "Updating existing repository..."
        cd ~/synthenic
        git fetch origin
        git reset --hard origin/main
    fi

    # Navigate to project directory
    cd ~/synthenic

    # Copy production docker-compose file
    cp ~/docker-compose.prod.yml ./docker-compose.prod.yml

    # Stop and remove existing containers
    echo "Cleaning up existing containers..."
    sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
    sudo docker system prune -f

    # Build and start containers with production configuration
    echo "Building and starting containers..."
    sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
    sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

    # Wait for application to start
    echo "Waiting for application to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8080 > /dev/null; then
            echo "Application is running!"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "Application failed to start. Checking logs..."
            sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs
            exit 1
        fi
        echo -n "."
        sleep 1
    done

    # Show container status
    echo "Container status:"
    sudo docker ps

    # Test the application through nginx
    echo "Testing application through nginx..."
    curl -I http://localhost:80

    # Cleanup production compose file
    rm ~/docker-compose.prod.yml
EOF

if [ $? -eq 0 ]; then
    echo "Deployment completed successfully!"
else
    echo "Deployment failed! Check the logs above for errors."
    exit 1
fi
