#!/usr/bin/env python3

import os
import subprocess
import sys
import logging
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_env_vars():
    """Load environment variables for configuration."""
    source_dir = os.getenv('SOURCE_DIR')
    dest_dir = os.getenv('DEST_DIR')
    compress = os.getenv('COMPRESS', 'false').lower() == 'true'
    email_to = os.getenv('EMAIL_TO')
    email_from = os.getenv('EMAIL_FROM')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    return source_dir, dest_dir, compress, email_to, email_from, smtp_server, smtp_port, smtp_user, smtp_pass

def perform_backup(source_dir, dest_dir, compress):
    """Perform incremental backup using rsync and optional compression."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(dest_dir, f'backup_{timestamp}')
    
    logging.info(f"Starting backup from {source_dir} to {backup_path}")
    
    # Use rsync for incremental sync
    try:
        subprocess.run(['rsync', '-avz', '--delete', source_dir + '/', backup_path + '/'], check=True)
        logging.info("Rsync completed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Rsync failed: {e}")
        raise
    
    if compress:
        archive_file = f"{backup_path}.tar.gz"
        logging.info(f"Compressing backup to {archive_file}")
        try:
            subprocess.run(['tar', '-czf', archive_file, '-C', dest_dir, os.path.basename(backup_path)], check=True)
            subprocess.run(['rm', '-rf', backup_path], check=True)  # Clean up uncompressed dir
            logging.info("Compression completed.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Compression failed: {e}")
            raise

def send_email_notification(email_to, email_from, smtp_server, smtp_port, smtp_user, smtp_pass, error_msg):
    """Send email notification on failure."""
    if not all([email_to, email_from, smtp_server]):
        logging.warning("Email configuration incomplete; skipping notification.")
        return
    
    msg = MIMEText(f"Backup failed at {datetime.now()}: {error_msg}")
    msg['Subject'] = 'Backup Service Failure Alert'
    msg['From'] = email_from
    msg['To'] = email_to
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(email_from, email_to, msg.as_string())
        logging.info("Error notification email sent.")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

if __name__ == "__main__":
    try:
        source_dir, dest_dir, compress, email_to, email_from, smtp_server, smtp_port, smtp_user, smtp_pass = load_env_vars()
        os.makedirs(dest_dir, exist_ok=True)
        perform_backup(source_dir, dest_dir, compress)
        logging.info("Backup completed successfully.")
        sys.exit(0)
    except Exception as e:
        error_msg = str(e)
        logging.error(f"Backup failed: {error_msg}")
        send_email_notification(email_to, email_from, smtp_server, smtp_port, smtp_user, smtp_pass, error_msg)
        sys.exit(1)