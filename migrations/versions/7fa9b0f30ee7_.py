"""empty message

Revision ID: 7fa9b0f30ee7
Revises: 8b7b5391760b
Create Date: 2019-11-18 22:28:05.524168

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7fa9b0f30ee7'
down_revision = '8b7b5391760b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('events') as batch:
        batch.alter_column(
            column_name='type',
            nullable=True,
            existing_type=sa.String(length=10),
            type_=sa.String(length=20))
    # ### end Alembic commands ###


def downgrade():
   with op.batch_alter_table('events') as batch:
        batch.alter_column(
            column_name='type',
            nullable=True,
            type_=sa.String(length=10),
            existing_type=sa.String(length=20))
    # ### end Alembic commands ###
