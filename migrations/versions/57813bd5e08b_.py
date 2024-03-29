"""empty message

Revision ID: 57813bd5e08b
Revises: 
Create Date: 2019-11-16 01:15:49.765139

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57813bd5e08b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('members',
    sa.Column('last_name', sa.String(length=80), nullable=True),
    sa.Column('first_name', sa.String(length=80), nullable=True),
    sa.Column('middle_name', sa.String(length=80), nullable=True),
    sa.Column('suffix', sa.String(length=80), nullable=True),
    sa.Column('nickname', sa.String(length=80), nullable=True),
    sa.Column('gender', sa.String(length=80), nullable=True),
    sa.Column('birthdate', sa.Integer(), nullable=True),
    sa.Column('division', sa.String(length=80), nullable=True),
    sa.Column('club_1_name', sa.String(length=80), nullable=True),
    sa.Column('club_1_abbreviation', sa.String(length=80), nullable=True),
    sa.Column('club_1_id', sa.String(length=80), nullable=True),
    sa.Column('club_2_name', sa.String(length=80), nullable=True),
    sa.Column('club_2_abbreviation', sa.String(length=80), nullable=True),
    sa.Column('club_2_id', sa.String(length=80), nullable=True),
    sa.Column('id_', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('member_type', sa.String(length=80), nullable=True),
    sa.Column('competitive', sa.String(length=80), nullable=True),
    sa.Column('expiration', sa.Date(), nullable=True),
    sa.Column('saber', sa.String(length=5), nullable=True),
    sa.Column('epee', sa.String(length=5), nullable=True),
    sa.Column('foil', sa.String(length=5), nullable=True),
    sa.Column('representing_country', sa.String(length=80), nullable=True),
    sa.Column('region', sa.Integer(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('updated_on', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id_')
    )
    op.create_table('seasons',
    sa.Column('id_', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('start', sa.DateTime(), nullable=True),
    sa.Column('end', sa.DateTime(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('updated_on', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id_')
    )
    op.create_table('tournaments',
    sa.Column('id_', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('ft_id', sa.String(length=80), nullable=True),
    sa.Column('venue', sa.String(length=80), nullable=True),
    sa.Column('city', sa.String(length=80), nullable=True),
    sa.Column('state', sa.String(length=5), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('opens', sa.DateTime(), nullable=True),
    sa.Column('closes', sa.DateTime(), nullable=True),
    sa.Column('withdraw', sa.DateTime(), nullable=True),
    sa.Column('start', sa.DateTime(), nullable=True),
    sa.Column('end', sa.DateTime(), nullable=True),
    sa.Column('region', sa.String(length=5), nullable=True),
    sa.Column('type', sa.String(length=20), nullable=True),
    sa.Column('season_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=5), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('updated_on', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['season_id'], ['seasons.id_'], ),
    sa.PrimaryKeyConstraint('id_')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password_hash', sa.String(length=120), nullable=True),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['member_id'], ['members.id_'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('events',
    sa.Column('id_', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('name', sa.String(length=40), nullable=False),
    sa.Column('type', sa.String(length=10), nullable=False),
    sa.Column('weapon', sa.String(length=10), nullable=False),
    sa.Column('gender', sa.String(length=1), nullable=False),
    sa.Column('abbreviation', sa.String(length=3), nullable=True),
    sa.Column('count', sa.Integer(), nullable=True),
    sa.Column('rating', sa.String(length=2), nullable=True),
    sa.Column('tournament_id', sa.Integer(), nullable=True),
    sa.Column('start', sa.DateTime(), nullable=True),
    sa.Column('status', sa.String(length=10), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('updated_on', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id_'], ),
    sa.PrimaryKeyConstraint('id_')
    )
    op.create_table('bouts',
    sa.Column('id_', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('red_member_id', sa.Integer(), nullable=True),
    sa.Column('green_member_id', sa.Integer(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('pool_id', sa.Integer(), nullable=True),
    sa.Column('round', sa.Integer(), nullable=True),
    sa.Column('red_score', sa.Integer(), nullable=True),
    sa.Column('green_score', sa.Integer(), nullable=True),
    sa.Column('referee', sa.String(length=40), nullable=True),
    sa.Column('winner', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id_'], ),
    sa.ForeignKeyConstraint(['green_member_id'], ['members.id_'], ),
    sa.ForeignKeyConstraint(['red_member_id'], ['members.id_'], ),
    sa.ForeignKeyConstraint(['winner'], ['members.id_'], ),
    sa.PrimaryKeyConstraint('id_')
    )
    op.create_table('entrants',
    sa.Column('id_', sa.Integer(), autoincrement=False, nullable=False),
    sa.Column('member_id', sa.Integer(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('initial_seeding', sa.Integer(), nullable=True),
    sa.Column('seeding_after_pools', sa.Integer(), nullable=True),
    sa.Column('final_placing', sa.Integer(), nullable=True),
    sa.Column('rating_earned', sa.String(length=5), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('updated_on', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id_'], ),
    sa.ForeignKeyConstraint(['member_id'], ['members.id_'], ),
    sa.PrimaryKeyConstraint('id_')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('entrants')
    op.drop_table('bouts')
    op.drop_table('events')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('tournaments')
    op.drop_table('seasons')
    op.drop_table('members')
    # ### end Alembic commands ###
