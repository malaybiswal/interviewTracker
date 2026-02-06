#!/usr/bin/env python3

import pymysql

# Database configuration
DB_HOST = '192.168.1.186'
DB_PORT = 3306
DB_USER = 'marisa'
DB_PASSWORD = 'marisa@123'
DB_NAME = 'misc'

try:
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
        # Clear all users
        cursor.execute("DELETE FROM user")
        deleted_count = cursor.rowcount
        
        # Reset auto-increment
        cursor.execute("ALTER TABLE user AUTO_INCREMENT = 1")
        
        connection.commit()
        
        print(f"🗑️  Deleted {deleted_count} users from the database")
        print("✅ User table cleared and auto-increment reset")

except pymysql.Error as e:
    print(f"❌ Database error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
        print("🔌 Database connection closed")