import psycopg2
import sys

try:
    print("Checking connection to PostgreSQL...")
    conn = psycopg2.connect(
        dbname='postgres',
        user='postgres',
        password='trungduc@123',
        host='localhost',
        port='5432'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    print("Connection successful! Password is correct.")
    
    # Check if database exists
    cursor.execute("SELECT datname FROM pg_database WHERE datname='meeting_minutes_db';")
    exists = cursor.fetchone()
    
    if exists:
        print("Database 'meeting_minutes_db' already exists.")
    else:
        print("Database 'meeting_minutes_db' is missing. Creating it now...")
        cursor.execute('CREATE DATABASE meeting_minutes_db;')
        print("Database 'meeting_minutes_db' created successfully!")
        
    conn.close()
    sys.exit(0)
except psycopg2.OperationalError as e:
    print(f"\nERROR CONNECTING TO POSTGRESQL:\n{e}")
    sys.exit(1)
