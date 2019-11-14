# SQLite does not support mosr usage of the SQL ALTER command which Flask-Migrations/Alembic
# uses to make changes to tables. Alembic has now introduced a BATCH mode that will 
# create an empty copy of a table with the changes applied, copy the data from the 
# original table, delete the original and rename the new one. 
# to use that with flask-migrations, the upgrade script for a migration
# must be edited to use the batch functions as flask-migrations will not do
# generate thais automatically.  these are just examples to show usage
# other examples are here:
# https://www.programcreek.com/python/example/87979/alembic.op.batch_alter_table

# Example 1 
def upgrade():
    table_prefix = context.config.get_main_option('table_prefix')
    table_name = table_prefix + 'environment_hierarchy_level_value'
    with op.batch_alter_table(table_name) as batch:
        batch.drop_column('parent_id')

        batch.drop_constraint(
            table_name + '_level_id_fkey',
            type_='foreignkey'
        )
        batch.create_foreign_key(
            table_name + '_level_id_fkey',
            table_prefix + 'environment_hierarchy_level',
            ['level_id'], ['id'], ondelete='CASCADE'
        )

        batch.create_unique_constraint(
            table_name + '_level_id_value_unique',
            ['level_id', 'value']
        ) 