"""lengthen events.abbreviation

Revision ID: 6a3ff88da143
Revises: a485de8c06db
Create Date: 2019-11-19 18:22:20.111881

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a3ff88da143'
down_revision = 'a485de8c06db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
        op.alter_column('events', 'abbreviation',
               type_ = sa.VARCHAR(length=10),
               existing_type=sa.VARCHAR(length=3),
               nullable=True)    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
        op.alter_column('events', 'abbreviation',
           type_ = sa.VARCHAR(length=3),
           existing_type=sa.VARCHAR(length=10),
           nullable=True) 
    # ### end Alembic commands ###
