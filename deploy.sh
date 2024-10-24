#!/bin/bash

# Server details
SERVER_IP="44.210.175.78"
PEM_FILE="synthetic.pem"
REPO_URL="git@github.com:bikramadhikari001/synthenic.git"

echo "Starting deployment process..."

# Ensure PEM file has correct permissions
chmod 400 $PEM_FILE

# SSH into server and deploy
echo "Connecting to server and deploying..."
ssh -i $PEM_FILE ubuntu@$SERVER_IP << EOF
    # Update system packages
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose git

    # Start Docker service
    sudo systemctl start docker
    sudo systemctl enable docker

    # Setup project directory
    if [ ! -d "~/synthenic" ]; then
        # First time setup - Clone the repository
        git clone $REPO_URL ~/synthenic
    else
        # Repository exists - Pull latest changes
        cd ~/synthenic
        git pull origin main
    fi

    # Navigate to project directory
    cd ~/synthenic

    # Build and start containers
    sudo docker-compose down
    sudo docker-compose build --no-cache
    sudo docker-compose up -d

    # Show container status
    sudo docker ps
EOF

echo "Deployment completed!"
