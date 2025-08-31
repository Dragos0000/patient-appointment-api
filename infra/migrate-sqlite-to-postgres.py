#!/usr/bin/env python3
import sqlite3
import asyncio
import asyncpg
import os
import sys
from datetime import datetime, date
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = project_root / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"Loaded environment variables from {env_file}")
    else:
        print("No .env file found, using system environment variables")
except ImportError:
    print("python-dotenv not available, using system environment variables")

async def migrate_data():
    """Migrate data from SQLite to PostgreSQL."""
    
    # Database connection parameters
    sqlite_db_path = project_root / "patient_appointments.db"
    postgres_config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', '5432')),
        'database': os.getenv('POSTGRES_DB', 'patient_appointments'),
        'user': os.getenv('POSTGRES_USER', 'patient_user'),
        'password': os.getenv('POSTGRES_PASSWORD', 'patient_password')
    }
    
    print(f"PostgreSQL connection: {postgres_config['user']}@{postgres_config['host']}:{postgres_config['port']}/{postgres_config['database']}")
    
    # Check if SQLite database exists
    if not sqlite_db_path.exists():
        print(f"SQLite database not found at {sqlite_db_path}")
        print("No data to migrate.")
        return
    
    print(f"Starting migration from {sqlite_db_path} to PostgreSQL...")
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_conn.row_factory = sqlite3.Row  # Enable column access by name
    
    try:
        # Connect to PostgreSQL
        pg_conn = await asyncpg.connect(**postgres_config)
        
        try:
            # Migrate patients
            print("Migrating patients...")
            cursor = sqlite_conn.execute("SELECT * FROM patients")
            patients = cursor.fetchall()
            
            for patient in patients:
                # Convert date string to date object if needed
                date_of_birth = patient['date_of_birth']
                if isinstance(date_of_birth, str):
                    try:
                        date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
                    except ValueError:
                        print(f"Warning: Could not parse date '{date_of_birth}' for patient {patient['nhs_number']}")
                        continue
                
                await pg_conn.execute(
                    """
                    INSERT INTO patients (nhs_number, name, date_of_birth, postcode)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (nhs_number) DO NOTHING
                    """,
                    patient['nhs_number'],
                    patient['name'],
                    date_of_birth,
                    patient['postcode']
                )
            
            print(f"Migrated {len(patients)} patients")
            
            # Migrate appointments
            print("Migrating appointments...")
            cursor = sqlite_conn.execute("SELECT * FROM appointments")
            appointments = cursor.fetchall()
            
            for appointment in appointments:
                # Convert time string to datetime if needed
                time_value = appointment['time']
                if isinstance(time_value, str):
                    try:
                        time_value = datetime.fromisoformat(time_value.replace('Z', '+00:00'))
                    except ValueError:
                        print(f"Warning: Could not parse time '{time_value}' for appointment {appointment['id']}")
                        continue
                
                await pg_conn.execute(
                    """
                    INSERT INTO appointments (id, patient, status, time, duration, clinician, department, postcode)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                    ON CONFLICT (id) DO NOTHING
                    """,
                    appointment['id'],
                    appointment['patient'],
                    appointment['status'],
                    time_value,
                    appointment['duration'],
                    appointment['clinician'],
                    appointment['department'],
                    appointment['postcode']
                )
            
            print(f"Migrated {len(appointments)} appointments")
            print("Migration completed successfully!")
            
        finally:
            await pg_conn.close()
            
    except Exception as e:
        print(f"Error during migration: {e}")
        raise
    finally:
        sqlite_conn.close()

if __name__ == "__main__":
    asyncio.run(migrate_data())
