"""Rename tables

Revision ID: 846f48a4a670
Revises: f8e40a2518df
Create Date: 2021-01-05 12:18:03.189097

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '846f48a4a670'
down_revision = 'f8e40a2518df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gameplayerstats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('move_type', sa.String(length=10), nullable=False),
    sa.Column('game_name', sa.String(length=64), nullable=True),
    sa.Column('player_name', sa.String(length=64), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['game_name'], ['gameinstance.name'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['player_name'], ['users.username'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.drop_table('gamestats')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gamestats',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('move_type', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('game_name', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('player_name', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['game_name'], ['gameinstance.name'], name='gamestats_game_name_fkey', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['player_name'], ['users.username'], name='gamestats_player_name_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='gamestats_pkey'),
    sa.UniqueConstraint('id', name='gamestats_id_key')
    )
    op.drop_table('gameplayerstats')
    # ### end Alembic commands ###
