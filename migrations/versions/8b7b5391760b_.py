"""empty message

Revision ID: 8b7b5391760b
Revises: 403e230aa689
Create Date: 2019-11-18 17:25:42.369358

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b7b5391760b'
down_revision = 'b23578e99891'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        column_name='region',
        nullable=True,
        existing_type=sa.String(length=5),
        type_=sa.String(length=15))
    op.alter_column(
        column_name='state',
        nullable=True,
        existing_type=sa.String(length=5),
        type_=sa.String(length=15)
        )    # ### end Alembic commands ###


def downgrade():
    op.alter_column(
        column_name='region',
        nullable=True,
        existing_type=sa.String(length=15),
        type_=sa.String(length=5))
    op.alter_column(
        column_name='state',
        nullable=True,
        existing_type=sa.String(length=15),
        type_=sa.String(length=5)
        )    # ### end Alembic commands ###

    # ### end Alembic commands ###
