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
ssh -i $PEM_FILE ubuntu@$SERVER_IP << 'EOF'
    # Update system packages
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose git nginx

    # Configure nginx
    sudo tee /etc/nginx/sites-available/synthenic << 'EON'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://synthenic_web_1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EON

    # Enable nginx site
    sudo ln -sf /etc/nginx/sites-available/synthenic /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo systemctl restart nginx

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
        git fetch origin
        git reset --hard origin/main
    fi

    # Navigate to project directory
    cd ~/synthenic

    # Create Docker network if it doesn't exist
    sudo docker network create synthenic_network || true

    # Stop and remove existing containers and networks
    sudo docker-compose down
    sudo docker system prune -f

    # Build and start containers with custom network
    sudo docker-compose build --no-cache
    sudo docker-compose up -d

    # Connect nginx to the Docker network
    sudo docker network connect synthenic_network $(sudo docker ps -qf "name=nginx")

    # Show container status
    sudo docker ps

    # Check if the application is accessible
    echo "Checking if the application is accessible..."
    sleep 5  # Wait for the application to start
    curl -I http://localhost:80
EOF

echo "Deployment completed!"
