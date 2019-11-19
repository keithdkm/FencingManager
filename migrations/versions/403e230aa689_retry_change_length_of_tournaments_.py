"""retry change length of tournaments.status

Revision ID: 403e230aa689
Revises: b23578e99891
Create Date: 2019-11-17 17:41:29.379438

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '403e230aa689'
down_revision = 'b23578e99891'
branch_labels = None
depends_on = None


def upgrade():

   # hand edited by Keith M 
   
    op.alter_column(
        table_name='tournaments',
        column_name='status',
        nullable=True,
        existing_type=sa.String(length=5),
        type_=sa.String(length=15)
    )
    # ### end Alembic commands ###


def downgrade():
    # hand edited by Keith M 
     op.alter_column(
        table_name='tournaments',
        column_name='status',
        nullable=True,
        type_=sa.String(length=5),
        existing_type=sa.String(length=15)
    )
    # ### end Alembic commands ###
