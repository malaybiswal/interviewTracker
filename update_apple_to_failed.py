#!/usr/bin/env python3
"""
Update Apple interview Round 2 to Failed and overall status to Rejected
"""

import mysql.connector

# Database connection
conn = mysql.connector.connect(
    host='192.168.1.186',
    user='root',
    password='root',
    database='interview_tracker'
)

cursor = conn.cursor()

print("Updating Apple Round 2 to Failed...")
cursor.execute("UPDATE interview_round SET status = 'Failed' WHERE id = 3")

print("Updating Apple overall status to Rejected...")
cursor.execute("UPDATE interview SET overall_status = 'Rejected' WHERE id = 3")

conn.commit()

print("✅ Successfully updated!")

# Verify
cursor.execute("SELECT status FROM interview_round WHERE id = 3")
round_status = cursor.fetchone()
print(f"Round 2 status: {round_status[0]}")

cursor.execute("SELECT overall_status FROM interview WHERE id = 3")
interview_status = cursor.fetchone()
print(f"Overall status: {interview_status[0]}")

cursor.close()
conn.close()
