"""Add unique constraints and rename interviewer models

Revision ID: interviewer_constraints
Revises: 142a4eeb141a
Create Date: 2026-02-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'interviewer_constraints'
down_revision = '142a4eeb141a'  # Chain from the password hash migration
branch_labels = None
depends_on = None


def upgrade():
    # Rename interviewer_comment table to interviewer_rating
    op.rename_table('interviewer_comment', 'interviewer_rating')
    
    # Rename column in interviewer table
    op.alter_column('interviewer', 'difficulty_rating',
                    new_column_name='average_difficulty',
                    existing_type=sa.Float(),
                    existing_nullable=True)
    
    # Rename column in interviewer_rating table
    op.alter_column('interviewer_rating', 'comment',
                    new_column_name='comments',
                    existing_type=sa.Text(),
                    existing_nullable=True)
    
    # Add created_at to interviewer if it doesn't exist
    with op.batch_alter_table('interviewer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
    
    # Add unique constraint to interviewer (name, company)
    op.create_unique_constraint('unique_interviewer', 'interviewer', ['name', 'company'])
    
    # Add unique constraint to interviewer_rating (interviewer_id, user_id)
    op.create_unique_constraint('unique_user_rating', 'interviewer_rating', ['interviewer_id', 'user_id'])


def downgrade():
    # Remove unique constraints
    op.drop_constraint('unique_user_rating', 'interviewer_rating', type_='unique')
    op.drop_constraint('unique_interviewer', 'interviewer', type_='unique')
    
    # Remove created_at from interviewer
    with op.batch_alter_table('interviewer', schema=None) as batch_op:
        batch_op.drop_column('created_at')
    
    # Rename columns back
    op.alter_column('interviewer_rating', 'comments',
                    new_column_name='comment',
                    existing_type=sa.Text(),
                    existing_nullable=True)
    
    op.alter_column('interviewer', 'average_difficulty',
                    new_column_name='difficulty_rating',
                    existing_type=sa.Float(),
                    existing_nullable=True)
    
    # Rename table back
    op.rename_table('interviewer_rating', 'interviewer_comment')
