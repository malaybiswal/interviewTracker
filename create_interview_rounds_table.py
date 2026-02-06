#!/usr/bin/env python3

import pymysql

# Database configuration
DB_HOST = '192.168.1.186'
DB_PORT = 3306
DB_USER = 'marisa'
DB_PASSWORD = 'marisa@123'
DB_NAME = 'misc'

def create_interview_rounds_table():
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
            # Check if interview_round table exists
            cursor.execute("SHOW TABLES LIKE 'interview_round'")
            table_exists = cursor.fetchone()
            
            if table_exists:
                print("⚠️  interview_round table already exists")
                return
            
            # Create interview_round table
            create_table_sql = """
            CREATE TABLE interview_round (
                id INT AUTO_INCREMENT PRIMARY KEY,
                interview_id INT NOT NULL,
                round_number INT NOT NULL,
                interviewer_name VARCHAR(120),
                interview_date DATETIME,
                interview_type VARCHAR(100),
                custom_interview_type VARCHAR(100),
                status VARCHAR(50) NOT NULL DEFAULT 'Scheduled',
                comments TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (interview_id) REFERENCES interview(id) ON DELETE CASCADE,
                INDEX idx_interview_id (interview_id),
                INDEX idx_round_number (round_number)
            )
            """
            
            cursor.execute(create_table_sql)
            print("✅ Created interview_round table")
            
            # Update interview table to change status to overall_status
            try:
                cursor.execute("ALTER TABLE interview CHANGE COLUMN status overall_status VARCHAR(50) NOT NULL DEFAULT 'Applied'")
                print("✅ Updated interview table: renamed status to overall_status")
            except Exception as e:
                if "doesn't exist" in str(e).lower():
                    print("⚠️  Column 'status' doesn't exist, skipping rename")
                else:
                    print(f"⚠️  Error updating interview table: {e}")
            
            connection.commit()
            print("✅ Database migration completed successfully")
            
            # Show table structure
            cursor.execute("DESCRIBE interview_round")
            columns = cursor.fetchall()
            print(f"\n🏗️  interview_round table structure:")
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
    create_interview_rounds_table()