#!/usr/bin/env python3

import pymysql

# Database configuration
DB_HOST = '192.168.1.186'
DB_PORT = 3306
DB_USER = 'marisa'
DB_PASSWORD = 'marisa@123'
DB_NAME = 'misc'

def test_connection():
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
            # Check if tables exist
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"📋 Available tables: {[table[0] for table in tables]}")
            
            # Check user table
            if ('user',) in tables:
                cursor.execute("SELECT COUNT(*) FROM user")
                user_count = cursor.fetchone()[0]
                print(f"👥 Users in database: {user_count}")
                
                if user_count > 0:
                    cursor.execute("SELECT username FROM user LIMIT 3")
                    users = cursor.fetchall()
                    print(f"📝 Sample users: {[user[0] for user in users]}")
            
            # Check interview table
            if ('interview',) in tables:
                cursor.execute("DESCRIBE interview")
                columns = cursor.fetchall()
                print(f"🏗️  Interview table columns: {[col[0] for col in columns]}")
                
                cursor.execute("SELECT COUNT(*) FROM interview")
                interview_count = cursor.fetchone()[0]
                print(f"📅 Interviews in database: {interview_count}")
            else:
                print("❌ Interview table does not exist")

    except pymysql.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'connection' in locals():
            connection.close()
            print("🔌 Database connection closed")

if __name__ == "__main__":
    test_connection()