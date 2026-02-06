#!/usr/bin/env python3

import pymysql
import os
from urllib.parse import quote_plus

# Database configuration
DB_HOST = '192.168.1.186'
DB_PORT = 3306
DB_USER = 'marisa'
DB_PASSWORD = 'marisa@123'
DB_NAME = 'misc'

try:
    # Connect to the database
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8mb4'
    )
    
    print(f"✅ Connected to MySQL database at {DB_HOST}")
    
    with connection.cursor() as cursor:
        # Check if user table exists
        cursor.execute("SHOW TABLES LIKE 'user'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ 'user' table exists")
            
            # Get all users
            cursor.execute("SELECT id, username, email FROM user")
            users = cursor.fetchall()
            
            if users:
                print(f"\n📋 Found {len(users)} existing users:")
                for user in users:
                    print(f"  - ID: {user[0]}, Username: {user[1]}, Email: {user[2]}")
            else:
                print("\n📋 No users found in the database")
                
            # Show table structure
            cursor.execute("DESCRIBE user")
            columns = cursor.fetchall()
            print(f"\n🏗️  User table structure:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} ({col[2]})")
                
        else:
            print("❌ 'user' table does not exist")
            
            # Show all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"\n📋 Available tables:")
            for table in tables:
                print(f"  - {table[0]}")

except pymysql.Error as e:
    print(f"❌ Database error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
        print("\n🔌 Database connection closed")