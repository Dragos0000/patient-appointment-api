#!/usr/bin/env python3
import shutil
import os
import sys
from pathlib import Path

# Database paths
DB_PATH = "patient_appointments.db"
BACKUP_PATH = "patient_appointments_backup.db"

def backup_database():
    """Create a backup of the current database."""
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"Database backed up: {DB_PATH} -> {BACKUP_PATH}")
        return True
    else:
        print(f"Warning: Database not found: {DB_PATH}")
        return False

def restore_database():
    """Restore the database from backup."""
    if os.path.exists(BACKUP_PATH):
        shutil.copy2(BACKUP_PATH, DB_PATH)
        print(f"Database restored: {BACKUP_PATH} -> {DB_PATH}")
        return True
    else:
        print(f"Warning: Backup not found: {BACKUP_PATH}")
        return False

def cleanup_backup():
    """Remove the backup file."""
    if os.path.exists(BACKUP_PATH):
        os.remove(BACKUP_PATH)
        print(f"Backup cleaned up: {BACKUP_PATH}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python backup_restore_db.py [backup|restore|cleanup]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "backup":
        success = backup_database()
        sys.exit(0 if success else 1)
    elif action == "restore":
        success = restore_database()
        sys.exit(0 if success else 1)
    elif action == "cleanup":
        cleanup_backup()
        sys.exit(0)
    else:
        print(f"Unknown action: {action}")
        print("Usage: python backup_restore_db.py [backup|restore|cleanup]")
        sys.exit(1)
