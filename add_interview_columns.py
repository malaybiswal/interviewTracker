#!/usr/bin/env python3

import pymysql

# Database configuration
DB_HOST = '192.168.1.186'
DB_PORT = 3306
DB_USER = 'marisa'
DB_PASSWORD = 'marisa@123'
DB_NAME = 'misc'

def add_missing_columns():
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
            # Check if interview table exists
            cursor.execute("SHOW TABLES LIKE 'interview'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                print("❌ Interview table does not exist")
                return
            
            # Get current table structure
            cursor.execute("DESCRIBE interview")
            columns = cursor.fetchall()
            existing_columns = [col[0] for col in columns]
            
            print(f"📋 Current columns: {existing_columns}")
            
            # Define columns to add
            columns_to_add = [
                ("interviewer_name", "VARCHAR(120)"),
                ("interview_date", "DATETIME"),
                ("interview_type", "VARCHAR(100)"),
                ("custom_interview_type", "VARCHAR(100)"),
                ("notes", "TEXT")
            ]
            
            # Add missing columns
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    try:
                        sql = f"ALTER TABLE interview ADD COLUMN {column_name} {column_type}"
                        cursor.execute(sql)
                        print(f"✅ Added column: {column_name}")
                    except Exception as e:
                        print(f"❌ Error adding column {column_name}: {e}")
                else:
                    print(f"⚠️  Column {column_name} already exists")
            
            connection.commit()
            print("✅ Database migration completed successfully")
            
            # Show updated table structure
            cursor.execute("DESCRIBE interview")
            columns = cursor.fetchall()
            print(f"\n🏗️  Updated table structure:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]} ({col[2]})")

    except pymysql.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'connection' in locals():
            connection.close()
            print("\n🔌 Database connection closed")

if __name__ == "__main__":
    add_missing_columns()