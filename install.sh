#!/bin/bash

# Installation script for JellyFresh

# Define paths
INSTALL_DIR="/opt/jellyfresh"
CONFIG_FILE="/opt/jellyfresh/new_releases_config.json"
SERVICE_FILE="/etc/systemd/system/jellyfresh.service"
LOG_DIR="/var/log/jellyfin_new_releases"
JELLYFRESH_USER="jellyfresh"
LAN_IP=$(hostname -I | awk '{print $1}')

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Requires root permissions, please use 'sudo' when running the installer."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
sudo apt update -y > /dev/null
sudo apt install -y python3 python3-pip python3-venv > /dev/null

# Create jellyfresh user if not exists, add it to adm group
if ! id -u $JELLYFRESH_USER > /dev/null 2>&1; then
    echo "Creating user $JELLYFRESH_USER..."
    useradd -r -s /usr/sbin/nologin $JELLYFRESH_USER
    sudo usermod -aG adm jellyfresh
else
    echo "User $JELLYFRESH_USER already exists."
fi

# Set up the installation directory
echo "Setting up the installation directory..."
mkdir -p $INSTALL_DIR
chmod 755 $INSTALL_DIR
cp -r . $INSTALL_DIR
chmod -R 755 $INSTALL_DIR
chown -R $JELLYFRESH_USER:$JELLYFRESH_USER $INSTALL_DIR

# Create a virtual environment
echo "Setting up virtual environment..."
if [ ! -d "/opt/jellyfresh/venv" ]; then
    python3 -m venv $INSTALL_DIR/venv
    echo "Virtual environment created successfully."
else
    echo "Virtual environment already exists."
fi

# Attempt to activate venv
if source /opt/jellyfresh/venv/bin/activate; then
    echo "Virtual environment activated."
else
    echo "Failed to activate virtual environment."
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r $INSTALL_DIR/requirements.txt

# Deactivate virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi

# Create default configuration file if it doesn't exist
echo "Creating configuration file..."
if [ ! -f $CONFIG_FILE ]; then
    cat > $CONFIG_FILE <<EOF
{
    "libraries": [],
    "automation": {
        "mode": "manual",
        "frequency": "weekly",
        "time": "02:00",
        "next_scan": null
    }
}
EOF
    chmod 644 $CONFIG_FILE
    chown $JELLYFRESH_USER:$JELLYFRESH_USER $CONFIG_FILE
    echo "Default configuration file created at $CONFIG_FILE."
else
    echo "Configuration file already exists at $CONFIG_FILE."
fi

# Set up log directory
echo "Setting up log directory..."
mkdir -p $LOG_DIR
chmod 755 $LOG_DIR
chown -R $JELLYFRESH_USER:$JELLYFRESH_USER $LOG_DIR

# Set up systemd service
echo "Setting up systemd service..."
cat > $SERVICE_FILE <<EOF
[Unit]
Description=JellyFresh Service
After=network.target

[Service]
Type=simple
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/main.py
WorkingDirectory=$INSTALL_DIR
Environment="CONFIG_FILE=$CONFIG_FILE"
Environment="LOG_DIR=$LOG_DIR"
Restart=always
User=$JELLYFRESH_USER
Group=$JELLYFRESH_USER

[Install]
WantedBy=multi-user.target
EOF

chmod 644 $SERVICE_FILE
systemctl daemon-reload
systemctl enable jellyfresh.service
systemctl start jellyfresh.service

# Completion
echo "Installation complete!"
echo "View logs with: journalctl -u jellyfresh -f"
echo ""
echo "!!!!!! Don't forget to setup your Jellyfin libraries first !!!!!!"
echo "!!!!!! Don't forget to create the folders for new releases !!!!!!"
echo "Setup Jellyfresh here > http://$LAN_IP:7007"
