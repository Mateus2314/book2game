"""add user_books table

Revision ID: 4f8c9d1e2a3b
Revises: b2b36b660250
Create Date: 2026-01-08 14:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f8c9d1e2a3b'
down_revision = 'b2b36b660250'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_books table
    op.create_table(
        'user_books',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('book_id', sa.Integer(), nullable=False),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reading_status', sa.String(length=20), nullable=False, server_default='to_read'),
        sa.Column('personal_rating', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['book_id'], ['books.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'book_id', name='uq_user_book')
    )
    
    # Create indexes
    op.create_index('idx_user_books_user', 'user_books', ['user_id'])
    op.create_index('idx_user_books_book', 'user_books', ['book_id'])
    op.create_index('idx_user_books_favorite', 'user_books', ['user_id', 'is_favorite'])
    op.create_index('idx_user_books_status', 'user_books', ['user_id', 'reading_status'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_user_books_status', 'user_books')
    op.drop_index('idx_user_books_favorite', 'user_books')
    op.drop_index('idx_user_books_book', 'user_books')
    op.drop_index('idx_user_books_user', 'user_books')
    
    # Drop table
    op.drop_table('user_books')
