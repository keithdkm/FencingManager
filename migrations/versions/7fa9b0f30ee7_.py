"""empty message

Revision ID: 7fa9b0f30ee7
Revises: 25044eae12b7
Create Date: 2019-11-18 22:28:05.524168

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7fa9b0f30ee7'
down_revision = '25044eae12b7'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        table_name='events',
        column_name='type',
        nullable=True,
        existing_type=sa.String(length=10),
        type_=sa.String(length=20))
    # ### end Alembic commands ###


def downgrade():
    op.alter_column(
        table_name='events',
        column_name='type',
        nullable=True,
        type=sa.String(length=10),
        existing_type_=sa.String(length=20))
    # ### end Alembic commands ###
