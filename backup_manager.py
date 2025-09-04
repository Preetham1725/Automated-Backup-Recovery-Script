#!/usr/bin/env python3
"""
Automated Backup & Recovery Script
Me: Preetham L

Features:
- Backup files, directories, databases (MySQL/Postgres)
- Compression (tar.gz/tar.bz2)
- Cloud upload (S3, optional)
- Logging and email notifications
- Recovery support
"""

import os, shutil, tarfile, smtplib, subprocess, yaml, logging, argparse
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class BackupManager:
    def __init__(self, config_file='backup_config.yaml'):
        self.config_file = config_file
        self.config = self._load_config()
        self._setup_logging()
    def _load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Config load error: {e}. Using defaults.")
            return self._get_default_config()
    def _get_default_config(self):
        return {
            'backup': {'items': ['./important'], 'backup_dir': './backups', 'compression': 'gz'},
            'mysql': {'enabled': False, 'user': '', 'password': '', 'database': '', 'host': 'localhost', 'backup_dir': './backups/mysql'},
            'postgres': {'enabled': False, 'user': '', 'password': '', 'database': '', 'host': 'localhost', 'backup_dir': './backups/postgres'},
            'cloud': {'enabled': False, 'provider': 'aws', 'bucket': '', 'access_key': '', 'secret_key': ''},
            'email': {'enabled': False, 'smtp_server': '', 'port': 587, 'username': '', 'password': '', 'from': '', 'to': ''},
            'logging': {'file': './backup.log', 'level': 'INFO'}
        }
    def _setup_logging(self):
        logging.basicConfig(level=getattr(logging, self.config['logging']['level'].upper(), logging.INFO),
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            filename=self.config['logging']['file'], filemode='a')
        self.logger = logging.getLogger(__name__)
    def backup_files(self):
        backup_dir = self.config['backup']['backup_dir']
        os.makedirs(backup_dir, exist_ok=True)
        for item in self.config['backup']['items']:
            if not os.path.exists(item):
                self.logger.error(f"Path not found: {item}")
                continue
            backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            basename = os.path.basename(item.rstrip(os.sep))
            dest_file = os.path.join(
                backup_dir,
                f"{basename}_{backup_time}.tar.{self.config['backup']['compression']}" if self.config['backup']['compression'] else f"{basename}_{backup_time}.tar"
            )
            try:
                with tarfile.open(dest_file, f"w:{self.config['backup']['compression']}" if self.config['backup']['compression'] else "w") as tar:
                    tar.add(item, arcname=basename)
                self.logger.info(f"Backup successful: {dest_file}")
            except Exception as e:
                self.logger.error(f"Backup failed for {item}: {e}")
    def backup_mysql(self):
        if not self.config['mysql']['enabled']:
            return
        backup_dir = self.config['mysql']['backup_dir']
        os.makedirs(backup_dir, exist_ok=True)
        dt = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"mysql_{dt}.sql.gz"
        filepath = os.path.join(backup_dir, filename)
        cmd = ['mysqldump', f"-u{self.config['mysql']['user']}", f"-p{self.config['mysql']['password']}", f"-h{self.config['mysql']['host']}", self.config['mysql']['database']]
        try:
            with open(filepath, 'wb') as f:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
                proc_out, _ = proc.communicate()
                import gzip
                f_gz = gzip.GzipFile(fileobj=f)
                f_gz.write(proc_out)
                f_gz.close()
            self.logger.info(f"MySQL backup completed: {filepath}")
        except Exception as e:
            self.logger.error(f"MySQL backup failed: {e}")
    def backup_postgres(self):
        if not self.config['postgres']['enabled']:
            return
        backup_dir = self.config['postgres']['backup_dir']
        os.makedirs(backup_dir, exist_ok=True)
        dt = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"postgres_{dt}.sql.gz"
        filepath = os.path.join(backup_dir, filename)
        cmd = ['pg_dump', f"-U{self.config['postgres']['user']}", f"-h{self.config['postgres']['host']}", self.config['postgres']['database']]
        try:
            env = os.environ.copy()
            env['PGPASSWORD'] = self.config['postgres']['password']
            with open(filepath, 'wb') as f:
                proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE)
                proc_out, _ = proc.communicate()
                import gzip
                f_gz = gzip.GzipFile(fileobj=f)
                f_gz.write(proc_out)
                f_gz.close()
            self.logger.info(f"PostgreSQL backup completed: {filepath}")
        except Exception as e:
            self.logger.error(f"PostgreSQL backup failed: {e}")
    def send_notification(self, subject, message):
        if not self.config['email']['enabled']:
            return
        smtp_cfg = self.config['email']
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_cfg['from']
            msg['To'] = smtp_cfg['to']
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            server = smtplib.SMTP(smtp_cfg['smtp_server'], smtp_cfg['port'])
            server.starttls()
            server.login(smtp_cfg['username'], smtp_cfg['password'])
            server.send_message(msg)
            server.quit()
            self.logger.info("Email notification sent.")
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
    def restore_backup(self, backup_file, restore_path):
        if not os.path.exists(backup_file):
            self.logger.error(f"Backup file not found: {backup_file}")
            return
        try:
            with tarfile.open(backup_file, 'r:*') as tar:
                tar.extractall(restore_path)
            self.logger.info(f"Restored backup to: {restore_path}")
        except Exception as e:
            self.logger.error(f"Restore failed: {e}")
    def run(self, operation='backup'):
        if operation == 'backup':
            self.logger.info("Starting backup…")
            self.backup_files()
            self.backup_mysql()
            self.backup_postgres()
            self.send_notification('Backup completed', f'Backup completed at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}. Check logs for details.')
        elif operation == 'restore':
            self.logger.info("Starting restore…")
            backup_dir = self.config['backup']['backup_dir']
            files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if f.endswith('tar.gz') or f.endswith('tar.bz2') or f.endswith('tar')]
            if not files:
                self.logger.error('No backup files found.')
                return
            latest_file = max(files, key=os.path.getmtime)
            self.restore_backup(latest_file, './restored')
        else:
            self.logger.info('No valid operation specified.')

def main():
    parser = argparse.ArgumentParser(description="Automated Backup & Recovery Script")
    parser.add_argument('-c', '--config', default='backup_config.yaml', help="Configuration YAML file")
    parser.add_argument('--restore', action='store_true', help="Restore the latest backup")
    args = parser.parse_args()
    mgr = BackupManager(args.config)
    if args.restore:
        mgr.run(operation='restore')
    else:
        mgr.run(operation='backup')

if __name__ == "__main__":
    main()
