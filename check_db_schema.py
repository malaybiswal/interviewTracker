#!/usr/bin/env python3
"""Check current database schema"""
import os
from sqlalchemy import create_engine, inspect

# Database connection
DB_HOST = os.getenv('DB_HOST', '192.168.1.186')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USER', 'marisa')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'marisa@123')
DB_NAME = os.getenv('DB_NAME', 'misc')

DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_engine(DATABASE_URI)
inspector = inspect(engine)

print("=== Current Database Tables ===")
tables = inspector.get_table_names()
for table in sorted(tables):
    print(f"  - {table}")

print("\n=== Interview Tracker Tables ===")
interview_tables = ['user', 'interview', 'interview_round', 'interviewer', 'interviewer_comment', 'interviewer_rating', 'phone_screen', 'onsite_interview']
for table in interview_tables:
    if table in tables:
        print(f"✓ {table} exists")
        columns = inspector.get_columns(table)
        for col in columns:
            print(f"    - {col['name']}: {col['type']}")
    else:
        print(f"✗ {table} does not exist")

print("\n=== Checking for interviewer table structure ===")
if 'interviewer' in tables:
    columns = {col['name']: col for col in inspector.get_columns('interviewer')}
    print(f"Has 'difficulty_rating': {'difficulty_rating' in columns}")
    print(f"Has 'average_difficulty': {'average_difficulty' in columns}")
    print(f"Has 'created_at': {'created_at' in columns}")
    
    # Check constraints
    unique_constraints = inspector.get_unique_constraints('interviewer')
    print(f"Unique constraints: {unique_constraints}")

if 'interviewer_comment' in tables:
    print("\n'interviewer_comment' table exists")
    columns = {col['name']: col for col in inspector.get_columns('interviewer_comment')}
    print(f"Has 'comment': {'comment' in columns}")
    print(f"Has 'comments': {'comments' in columns}")
    
if 'interviewer_rating' in tables:
    print("\n'interviewer_rating' table exists")
    columns = {col['name']: col for col in inspector.get_columns('interviewer_rating')}
    print(f"Has 'comment': {'comment' in columns}")
    print(f"Has 'comments': {'comments' in columns}")
