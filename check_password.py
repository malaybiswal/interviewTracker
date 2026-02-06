#!/usr/bin/env python3

import pymysql
from werkzeug.security import check_password_hash

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
        # Get user details including password hash
        cursor.execute("SELECT id, username, email, password_hash FROM user WHERE username = 'Malay'")
        user = cursor.fetchone()
        
        if user:
            user_id, username, email, password_hash = user
            print(f"\n👤 User found:")
            print(f"  - ID: {user_id}")
            print(f"  - Username: {username}")
            print(f"  - Email: {email}")
            print(f"  - Password Hash: {password_hash[:50]}..." if password_hash else "  - Password Hash: None")
            
            # Check if password hash exists and looks valid
            if password_hash:
                if password_hash.startswith('pbkdf2:sha256:') or password_hash.startswith('scrypt:'):
                    print("  ✅ Password hash format looks valid (Werkzeug format)")
                else:
                    print("  ⚠️  Password hash format might be invalid")
                    print(f"  Hash starts with: {password_hash[:20]}")
            else:
                print("  ❌ No password hash found!")
                
        else:
            print("❌ User 'Malay' not found")

except pymysql.Error as e:
    print(f"❌ Database error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'connection' in locals():
        connection.close()
        print("\n🔌 Database connection closed")