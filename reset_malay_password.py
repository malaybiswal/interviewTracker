#!/usr/bin/env python3

import pymysql
from werkzeug.security import generate_password_hash

# Database configuration
DB_HOST = '192.168.1.186'
DB_PORT = 3306
DB_USER = 'marisa'
DB_PASSWORD = 'marisa@123'
DB_NAME = 'misc'

# New password to set
NEW_PASSWORD = "password123"

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
        # Generate new password hash
        new_hash = generate_password_hash(NEW_PASSWORD)
        
        # Update the password for user 'malay'
        cursor.execute("UPDATE user SET password_hash = %s WHERE username = 'malay'", (new_hash,))
        
        if cursor.rowcount > 0:
            connection.commit()
            print(f"✅ Password updated for user 'malay'")
            print(f"🔑 New password: {NEW_PASSWORD}")
            print(f"👤 Username: malay")
            print("\n🚀 You can now login with:")
            print(f"   Username: malay")
            print(f"   Password: {NEW_PASSWORD}")
        else:
            print("❌ No user found to update")

except pymysql.Error as e:
    print(f"❌ Database error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
        print("\n🔌 Database connection closed")