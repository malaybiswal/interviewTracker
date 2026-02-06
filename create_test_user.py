#!/usr/bin/env python3

import pymysql
from werkzeug.security import generate_password_hash

# Database configuration
DB_HOST = '192.168.1.186'
DB_PORT = 3306
DB_USER = 'marisa'
DB_PASSWORD = 'marisa@123'
DB_NAME = 'misc'

def create_test_user():
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
            # Check if user already exists
            cursor.execute("SELECT id FROM user WHERE username = 'testuser'")
            existing_user = cursor.fetchone()
            
            if existing_user:
                print("⚠️  Test user already exists")
                return existing_user[0]
            
            # Create password hash
            password_hash = generate_password_hash('password123')
            
            # Insert test user
            cursor.execute(
                "INSERT INTO user (username, email, password_hash) VALUES (%s, %s, %s)",
                ('testuser', 'test@example.com', password_hash)
            )
            
            user_id = cursor.lastrowid
            connection.commit()
            
            print(f"✅ Created test user with ID: {user_id}")
            print("   Username: testuser")
            print("   Password: password123")
            print("   Email: test@example.com")
            
            return user_id

    except pymysql.Error as e:
        print(f"❌ Database error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        if 'connection' in locals():
            connection.close()
            print("🔌 Database connection closed")

if __name__ == "__main__":
    create_test_user()