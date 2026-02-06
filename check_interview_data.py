#!/usr/bin/env python3

import pymysql

# Database configuration
DB_HOST = '192.168.1.186'
DB_PORT = 3306
DB_USER = 'marisa'
DB_PASSWORD = 'marisa@123'
DB_NAME = 'misc'

def check_interviews():
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
            # Get all interviews
            cursor.execute("SELECT * FROM interview ORDER BY id DESC LIMIT 5")
            interviews = cursor.fetchall()
            
            if interviews:
                # Get column names
                cursor.execute("DESCRIBE interview")
                columns = cursor.fetchall()
                column_names = [col[0] for col in columns]
                
                print(f"\n📋 Recent interviews:")
                print(f"Columns: {column_names}")
                print("-" * 100)
                
                for interview in interviews:
                    print(f"Interview ID: {interview[0]}")
                    for i, value in enumerate(interview):
                        print(f"  {column_names[i]}: {value}")
                    print("-" * 50)
            else:
                print("📋 No interviews found")

    except pymysql.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'connection' in locals():
            connection.close()
            print("🔌 Database connection closed")

if __name__ == "__main__":
    check_interviews()