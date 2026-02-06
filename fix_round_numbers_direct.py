#!/usr/bin/env python3
"""
Script to fix round numbers in the database.
The initial interview should be Round 1, so all InterviewRound entries need to be incremented by 1.
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

print("Fetching current round numbers...")
cursor.execute('SELECT id, interview_id, round_number, interview_type, custom_interview_type FROM interview_round ORDER BY interview_id, round_number DESC')
rounds = cursor.fetchall()

print(f"Found {len(rounds)} rounds to update\n")

# Update each round (process in reverse order to avoid conflicts)
for round_id, interview_id, old_number, interview_type, custom_type in rounds:
    new_number = old_number + 1
    type_display = custom_type or interview_type or 'Not specified'
    print(f"Interview {interview_id}, Round {round_id}: {old_number} -> {new_number} ({type_display})")
    
    cursor.execute(
        'UPDATE interview_round SET round_number = %s WHERE id = %s',
        (new_number, round_id)
    )

conn.commit()
print("\n✅ Successfully updated all round numbers!")

# Verify the changes
print("\nVerifying changes:")
cursor.execute('SELECT id, interview_id, round_number, interview_type, custom_interview_type FROM interview_round ORDER BY interview_id, round_number')
updated_rounds = cursor.fetchall()

for round_id, interview_id, round_number, interview_type, custom_type in updated_rounds:
    type_display = custom_type or interview_type or 'Not specified'
    print(f"  Interview {interview_id}, Round {round_number}: {type_display}")

cursor.close()
conn.close()
