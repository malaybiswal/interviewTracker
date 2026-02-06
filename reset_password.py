#!/usr/bin/env python3

import pymysql
import hashlib
import os
import base64

# Database configuration
DB_HOST = '192.168.1.186'
DB_PORT = 3306
DB_USER = 'marisa'
DB_PASSWORD = 'marisa@123'
DB_NAME = 'misc'

# New password to set
NEW_PASSWORD = "password123"

def generate_password_hash(password):
    """Generate a simple SHA256 hash for compatibility"""
    salt = os.urandom(32)  # 32 bytes salt
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return f"pbkdf2:sha256:100000${base64.b64encode(salt).decode('ascii')}${base64.b64encode(pwdhash).decode('ascii')}"

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
        
        # Update the password for user 'Malay'
        cursor.execute("UPDATE user SET password_hash = %s WHERE username = 'Malay'", (new_hash,))
        
        if cursor.rowcount > 0:
            connection.commit()
            print(f"✅ Password updated for user 'Malay'")
            print(f"🔑 New password: {NEW_PASSWORD}")
            print(f"👤 Username: Malay")
            print("\n🚀 You can now login with:")
            print(f"   Username: Malay")
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