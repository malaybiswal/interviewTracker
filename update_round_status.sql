-- Update Apple Round 2 to Failed
UPDATE interview_round SET status = 'Failed' WHERE id = 3;

-- Update Apple overall status to Rejected  
UPDATE interview SET overall_status = 'Rejected' WHERE id = 3;
