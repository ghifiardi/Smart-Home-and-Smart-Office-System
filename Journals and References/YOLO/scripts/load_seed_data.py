#!/usr/bin/env python3
"""
Smart Office/Home Surveillance System - Seed Data Loader
Loads sample data into the database for testing and development
"""

import sys
import psycopg2
from psycopg2 import sql
import argparse
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Database configuration
DEFAULT_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'smartoffice',
    'user': 'smartoffice_user',
    'password': 'smartoffice_password'
}

def print_header(text):
    """Print a formatted header"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    """Print success message"""
    print(f"{GREEN}✓{RESET} {text}")

def print_error(text):
    """Print error message"""
    print(f"{RED}✗{RESET} {text}")

def print_warning(text):
    """Print warning message"""
    print(f"{YELLOW}⚠{RESET} {text}")

def print_info(text):
    """Print info message"""
    print(f"{BLUE}ℹ{RESET} {text}")

def connect_to_database(config):
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        print_success(f"Connected to database: {config['database']}")
        return conn
    except Exception as e:
        print_error(f"Failed to connect to database: {e}")
        return None

def load_sql_file(conn, sql_file_path):
    """Load and execute SQL file"""
    try:
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()

        cursor = conn.cursor()
        cursor.execute(sql_content)
        conn.commit()
        cursor.close()

        print_success(f"Successfully loaded: {sql_file_path.name}")
        return True
    except Exception as e:
        conn.rollback()
        print_error(f"Failed to load {sql_file_path.name}: {e}")
        return False

def verify_seed_data(conn):
    """Verify that seed data was loaded correctly"""
    print_header("Verifying Seed Data")

    queries = {
        'Users': 'SELECT COUNT(*) FROM users',
        'Sites': 'SELECT COUNT(*) FROM sites',
        'Buildings': 'SELECT COUNT(*) FROM buildings',
        'Zones': 'SELECT COUNT(*) FROM zones',
        'Cameras': 'SELECT COUNT(*) FROM cameras',
        'Access Devices': 'SELECT COUNT(*) FROM access_devices',
        'Sensors': 'SELECT COUNT(*) FROM sensors',
        'Registered Persons': 'SELECT COUNT(*) FROM registered_persons',
        'Automation Rules': 'SELECT COUNT(*) FROM automation_rules',
        'Events': 'SELECT COUNT(*) FROM events',
        'Detections': 'SELECT COUNT(*) FROM detections'
    }

    cursor = conn.cursor()
    all_ok = True

    for name, query in queries.items():
        try:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            if count > 0:
                print_success(f"{name}: {count} records")
            else:
                print_warning(f"{name}: No records found")
        except Exception as e:
            print_error(f"{name}: Table might not exist - {e}")
            all_ok = False

    cursor.close()
    return all_ok

def clear_existing_data(conn):
    """Clear existing seed data (optional)"""
    print_header("Clearing Existing Data")
    print_warning("This will delete all existing data!")

    response = input("Are you sure you want to continue? (yes/no): ")
    if response.lower() != 'yes':
        print_info("Skipping data clearing")
        return True

    # Tables in reverse order of dependencies
    tables = [
        'detections',
        'events',
        'automation_rules',
        'registered_persons',
        'sensors',
        'access_devices',
        'cameras',
        'zones',
        'buildings',
        'sites',
        'users'
    ]

    cursor = conn.cursor()
    try:
        for table in tables:
            try:
                cursor.execute(f"TRUNCATE TABLE {table} CASCADE")
                print_success(f"Cleared table: {table}")
            except Exception as e:
                print_warning(f"Could not clear {table}: {e}")

        conn.commit()
        print_success("Data clearing completed")
        return True
    except Exception as e:
        conn.rollback()
        print_error(f"Error clearing data: {e}")
        return False
    finally:
        cursor.close()

def print_login_info():
    """Print default login credentials"""
    print_header("Default Login Credentials")
    print(f"{BOLD}Administrator:{RESET}")
    print(f"  Email:    admin@smartoffice.com")
    print(f"  Password: password123")
    print()
    print(f"{BOLD}Security Manager:{RESET}")
    print(f"  Email:    security@smartoffice.com")
    print(f"  Password: password123")
    print()
    print(f"{BOLD}Operator:{RESET}")
    print(f"  Email:    operator@smartoffice.com")
    print(f"  Password: password123")
    print()
    print(f"{YELLOW}Note: Change these passwords in production!{RESET}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Load seed data into Smart Office/Home database'
    )
    parser.add_argument(
        '--host',
        default=DEFAULT_CONFIG['host'],
        help='Database host (default: localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=DEFAULT_CONFIG['port'],
        help='Database port (default: 5432)'
    )
    parser.add_argument(
        '--database',
        default=DEFAULT_CONFIG['database'],
        help='Database name (default: smartoffice)'
    )
    parser.add_argument(
        '--user',
        default=DEFAULT_CONFIG['user'],
        help='Database user (default: smartoffice_user)'
    )
    parser.add_argument(
        '--password',
        default=DEFAULT_CONFIG['password'],
        help='Database password'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing data before loading'
    )
    parser.add_argument(
        '--sql-file',
        type=Path,
        help='Path to SQL seed file (default: scripts/seed_data.sql)'
    )

    args = parser.parse_args()

    # Determine SQL file path
    if args.sql_file:
        sql_file = args.sql_file
    else:
        # Try to find seed_data.sql in the scripts directory
        script_dir = Path(__file__).parent
        sql_file = script_dir / 'seed_data.sql'

    if not sql_file.exists():
        print_error(f"SQL file not found: {sql_file}")
        print_info("Use --sql-file to specify a different path")
        return 1

    print_header("Smart Office/Home Seed Data Loader")

    # Database configuration
    config = {
        'host': args.host,
        'port': args.port,
        'database': args.database,
        'user': args.user,
        'password': args.password
    }

    print_info(f"Database: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
    print_info(f"SQL File: {sql_file}")
    print()

    # Connect to database
    conn = connect_to_database(config)
    if not conn:
        return 1

    try:
        # Clear existing data if requested
        if args.clear:
            if not clear_existing_data(conn):
                return 1

        # Load seed data
        print_header("Loading Seed Data")
        if not load_sql_file(conn, sql_file):
            return 1

        # Verify data was loaded
        if not verify_seed_data(conn):
            print_warning("Some tables might not exist yet. Run migrations first.")

        # Print login information
        print_login_info()

        print_header("Seed Data Loading Complete")
        print_success("All seed data has been loaded successfully!")

        return 0

    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1
    finally:
        conn.close()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Operation cancelled by user{RESET}")
        sys.exit(1)
