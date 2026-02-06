#!/usr/bin/env python3
"""
Script to fix round numbers in the database.
The initial interview should be Round 1, so all InterviewRound entries need to be incremented by 1.
"""

from app import app
from models import db, InterviewRound

def fix_round_numbers():
    with app.app_context():
        # Get all interview rounds ordered by interview_id and round_number
        rounds = InterviewRound.query.order_by(
            InterviewRound.interview_id, 
            InterviewRound.round_number.desc()
        ).all()
        
        print(f"Found {len(rounds)} rounds to update")
        
        # Group by interview_id to process each interview separately
        interview_rounds = {}
        for round in rounds:
            if round.interview_id not in interview_rounds:
                interview_rounds[round.interview_id] = []
            interview_rounds[round.interview_id].append(round)
        
        # Update round numbers (increment by 1)
        for interview_id, rounds_list in interview_rounds.items():
            print(f"\nProcessing interview {interview_id}:")
            # Process in reverse order (highest round number first) to avoid conflicts
            for round in rounds_list:
                old_number = round.round_number
                new_number = old_number + 1
                round.round_number = new_number
                print(f"  Round {round.id}: {old_number} -> {new_number}")
        
        # Commit changes
        db.session.commit()
        print("\n✅ Successfully updated all round numbers!")
        
        # Verify the changes
        print("\nVerifying changes:")
        all_rounds = InterviewRound.query.order_by(
            InterviewRound.interview_id, 
            InterviewRound.round_number
        ).all()
        
        for round in all_rounds:
            print(f"  Interview {round.interview_id}, Round {round.round_number}: {round.interview_type or round.custom_interview_type}")

if __name__ == '__main__':
    fix_round_numbers()
