"""empty message

Revision ID: b23578e99891
Revises: 57813bd5e08b
Create Date: 2019-11-17 00:46:30.760582

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b23578e99891'
down_revision = '57813bd5e08b'
branch_labels = None
depends_on = None


def upgrade():
   # hand edited by Keith M 
   
    op.alter_column(
        table_name='tournaments',
        column_name='status',
        nullable=False,
        existing_type=sa.String(length=5),
        type_=sa.String(length=5)
    )
    # ### end Alembic commands ###


def downgrade():
    # hand edited by Keith M 
     op.alter_column(
        table_name='tournaments',
        column_name='status',
        nullable=False,
        type_=sa.String(length=5),
        existing_type=sa.String(length=5)
    )
    # ### end Alembic commands ###
