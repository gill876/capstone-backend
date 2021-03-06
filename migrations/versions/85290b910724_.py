"""empty message

Revision ID: 85290b910724
Revises: c36bf094edc3
Create Date: 2021-04-01 04:36:13.263154

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '85290b910724'
down_revision = 'c36bf094edc3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('app_package_category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('app_name', sa.String(length=100), nullable=True),
    sa.Column('package_name', sa.String(length=100), nullable=True),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('app_usage',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=True),
    sa.Column('app_pkg_cat', sa.Integer(), nullable=True),
    sa.Column('time_sec', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('phone',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_id', sa.String(length=255), nullable=True),
    sa.Column('os_version', sa.String(length=50), nullable=True),
    sa.Column('cpu_utilization', sa.Integer(), nullable=True),
    sa.Column('memory_utilization', sa.Integer(), nullable=True),
    sa.Column('running_apps', sa.Integer(), nullable=True),
    sa.Column('battery_percentage', sa.Integer(), nullable=True),
    sa.Column('battery_state', sa.Integer(), nullable=True),
    sa.Column('phone_model', sa.String(length=50), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone_id')
    )
    op.create_table('profile',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_id', sa.String(length=255), nullable=True),
    sa.Column('gender', sa.Integer(), nullable=True),
    sa.Column('extraversion', sa.Integer(), nullable=True),
    sa.Column('agreeableness', sa.Integer(), nullable=True),
    sa.Column('conscientiousness', sa.Integer(), nullable=True),
    sa.Column('emotional_stability', sa.Integer(), nullable=True),
    sa.Column('intellect_imagination', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone_id')
    )
    op.create_table('running_apps',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('running_apps', sa.Integer(), nullable=True),
    sa.Column('app_pkg_cat', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('user_xphone',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_id', sa.String(length=255), nullable=True),
    sa.Column('username', sa.String(length=80), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_xphone')
    op.drop_table('user')
    op.drop_table('running_apps')
    op.drop_table('profile')
    op.drop_table('phone')
    op.drop_table('app_usage')
    op.drop_table('app_package_category')
    # ### end Alembic commands ###
