"""empty message

Revision ID: a485de8c06db
Revises: 7fa9b0f30ee7
Create Date: 2019-11-18 23:14:33.566578

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a485de8c06db'
down_revision = '7fa9b0f30ee7'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table('events') as batch:
        batch.alter_column(
            column_name='type',
            nullable=True,
            existing_type=sa.String(length=10),
            type_=sa.String(length=20))

        batch.alter_column(
            column_name = 'gender',
            type_ = sa.VARCHAR(length=10),
            existing_type=sa.VARCHAR(length=1),
            nullable=True)



def downgrade():
       with op.batch_alter_table('events') as batch:
            batch.alter_column(
                column_name='type',
                nullable=True,
                type_=sa.String(length=10),
                existing_type=sa.String(length=20))
                
            batch.alter_column(
                column_name = 'gender',
                type_ = sa.VARCHAR(length=1),
                existing_type=sa.VARCHAR(length=10),
                nullable=True)
    # ### end Alembic commands ###
