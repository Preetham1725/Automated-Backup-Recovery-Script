# Automated Backup & Recovery Script

## Overview

This Python tool automates backups of files, directories, and databases (MySQL/PostgreSQL) and provides easy recovery/restoration. Supports compression (tar.gz/tar.bz2), logging, email notifications, and optional cloud storage.

## Features

- Backup files and directories as tar.gz
- Database dump and compress (MySQL/Postgres)
- Easy restore of latest backup
- Email notification on completion
- Logging of all operations
- Configuration via YAML file

## Setup

1. Clone repository  
   `git clone https://github.com/Preetham1725/backup-suite.git`
2. Install dependencies  
   `pip install -r requirements.txt`
3. Update `backup_config.yaml` as per your requirements

## Usage

- Run backup:  
  `python backup_manager.py`
- Restore backup:  
  `python backup_manager.py --restore`
- Specify config file:  
  `python backup_manager.py -c custom_config.yaml`
- Check logs:  
  See `backup.log` after operation.

## Example Output

```
2025-09-04 12:36:23 - INFO - Backup successful: ./backups/data_20250904_123623.tar.gz
2025-09-04 12:36:24 - INFO - Backup completed.
2025-09-04 12:36:29 - INFO - Restored backup to: ./restored
```


## Skills Demonstrated

- Python scripting (file operations, subprocess, archiving)
- YAML configuration
- Logging and notification
- Database backup automation
- Error handling and reporting

## Me

**Preetham L**
- Position: DA II @ Amazon
- Location: Bangalore, India
- GitHub: [@Preetham1725](https://github.com/Preetham1725)
- LinkedIn: [preetham-l-820bb8170](https://linkedin.com/in/preetham-l-820bb8170)

## Acknowledgments

- Built for IT support engineers and system administrators

## Contribution

PRs welcome for cloud integration, new backup modes, and advanced notification features.


