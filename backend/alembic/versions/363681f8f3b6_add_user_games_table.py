"""add user_games table

Revision ID: 363681f8f3b6
Revises: 4f8c9d1e2a3b
Create Date: 2026-01-08 18:25:45.259732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '363681f8f3b6'
down_revision: Union[str, None] = '4f8c9d1e2a3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create user_games table
    op.create_table(
        'user_games',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('game_id', sa.Integer(), nullable=False),
        sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('play_status', sa.String(length=20), nullable=False, server_default='to_play'),
        sa.Column('personal_rating', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('hours_played', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'game_id', name='uq_user_game'),
    )
    
    # Create indexes for better query performance
    op.create_index('ix_user_games_user_id', 'user_games', ['user_id'])
    op.create_index('ix_user_games_game_id', 'user_games', ['game_id'])
    op.create_index('ix_user_games_user_id_is_favorite', 'user_games', ['user_id', 'is_favorite'])
    op.create_index('ix_user_games_user_id_play_status', 'user_games', ['user_id', 'play_status'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_user_games_user_id_play_status', table_name='user_games')
    op.drop_index('ix_user_games_user_id_is_favorite', table_name='user_games')
    op.drop_index('ix_user_games_game_id', table_name='user_games')
    op.drop_index('ix_user_games_user_id', table_name='user_games')
    
    # Drop table
    op.drop_table('user_games')
