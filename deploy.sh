#!/bin/bash

# Update system and install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx

# Create application directory
sudo mkdir -p /var/www/synthenic
sudo chown -R ubuntu:ubuntu /var/www/synthenic

# Create and activate virtual environment
python3 -m venv /var/www/synthenic/venv
source /var/www/synthenic/venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Configure Nginx
sudo tee /etc/nginx/sites-available/synthenic << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Enable the Nginx site
sudo ln -s /etc/nginx/sites-available/synthenic /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

# Create systemd service file
sudo tee /etc/systemd/system/synthenic.service << EOF
[Unit]
Description=Synthenic Flask Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/synthenic
Environment="PATH=/var/www/synthenic/venv/bin"
ExecStart=/var/www/synthenic/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start and enable the service
sudo systemctl daemon-reload
sudo systemctl start synthenic
sudo systemctl enable synthenic

echo "Deployment completed!"
