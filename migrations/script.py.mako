"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
# Added to give access to database engine type. 
# If it's sqlite, use a different upgrade path
from config import Config
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}




if Config.SQLALCHEMY_DATABASE_URI[0:6]=='sqlite':
# if database to be upgraded is a sqlite database use batch update scripts
#    def upgrade():
#        with op.batch_alter_table('') as batch:
#            batch.alter_column(
#                   column_name = '',
#                   type_ =  ,
#                   existing_type= ,
#                   nullable= )    
#
#
#    def downgrade():
#        
#        with op.batch_alter_table('') as batch:
#            batch.alter_column(
#                   column_name = '',
#                   type_ =  ,
#                   existing_type= ,
#                   nullable= )   
    pass
else:
    def upgrade():
            ${upgrades if upgrades else "pass"}


    def downgrade():
            ${downgrades if downgrades else "pass"}
