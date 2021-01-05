"""Rename tables

Revision ID: f8e40a2518df
Revises: 6c2452322fd1
Create Date: 2021-01-05 11:57:58.452477

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f8e40a2518df'
down_revision = '6c2452322fd1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'gameinstance', ['name'])
    op.create_unique_constraint(None, 'gamestats', ['id'])
    op.create_unique_constraint(None, 'moves', ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'moves', type_='unique')
    op.drop_constraint(None, 'gamestats', type_='unique')
    op.drop_constraint(None, 'gameinstance', type_='unique')
    # ### end Alembic commands ###
