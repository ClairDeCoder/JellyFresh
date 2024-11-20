#!/bin/bash

# Define paths
INSTALL_DIR="/opt/jellyfresh"
SERVICE_FILE="/etc/systemd/system/jellyfresh.service"
LOG_DIR="/var/log/jellyfresh"
JELLYFRESH_USER="jellyfresh"

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
    echo "Requires root permissions, please use 'sudo' when running the uninstaller."
    exit 1
fi

echo "Sorry to see you go! Are you sure you want to continue uninstalling JellyFresh? [Y/n]"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "Let's clean this up..."

    # Stop and disable service
    echo "Disabling & removing JellyFresh service.."
    systemctl stop jellyfresh.service
    systemctl disable jellyfresh.service
    systemctl daemon-reload

    # Remove files and directories
    echo "Cleaning up files & folders.. one sec"
    rm $SERVICE_FILE
    rm -r $LOG_DIR

    # Remove user
    echo "Removing JellyFresh user.. almost there"
    userdel $JELLYFRESH_USER

    # Execute removal of dir after script is done running (preventing conflicts)
    nohup sh -c "sleep 5; rm -rf \"$INSTALL_DIR\"" &> /dev/null &

    echo "Thanks for giving it a go!"
    echo ""
    echo "!!!!! Don't forget to clean up your spotlight folders !!!!!"
    echo "Uninstall complete - JellyFresh has been removed from your system."

else
    exit 0
fi