#!/bin/bash

# Deployment script for systemd-backup-project
# Usage: sudo ./deploy/deploy.sh

set -e  # Exit on error

PROJECT_ROOT=$(pwd)
INSTALL_DIR=/opt/backup-service
SYSTEMD_DIR=/etc/systemd/system

# Create install directory if it doesn't exist
mkdir -p $INSTALL_DIR

# Copy Python script
cp $PROJECT_ROOT/src/backup_service.py $INSTALL_DIR/
chmod +x $INSTALL_DIR/backup_service.py
chown root:root $INSTALL_DIR/backup_service.py

# Copy systemd units
cp $PROJECT_ROOT/systemd/backup.service $SYSTEMD_DIR/
cp $PROJECT_ROOT/systemd/backup.timer $SYSTEMD_DIR/
cp $PROJECT_ROOT/systemd/backup.socket $SYSTEMD_DIR/

# environment file
cp $PROJECT_ROOT/systemd/backup.env $SYSTEMD_DIR/backup.env
chmod 600 $SYSTEMD_DIR/backup.env

# Create dedicated user/group if not exists (for security)
if ! id -u backupuser > /dev/null 2>&1; then
    useradd -r -s /bin/false backupuser
fi
if ! getent group backupgroup > /dev/null 2>&1; then
    groupadd backupgroup
fi

# Reload systemd and enable services
systemctl daemon-reload
systemctl enable backup.timer
systemctl start backup.timer
systemctl enable backup.socket
systemctl start backup.socket