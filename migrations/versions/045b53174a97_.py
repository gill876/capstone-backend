"""empty message

Revision ID: 045b53174a97
Revises: 7fecf51cff1b
Create Date: 2021-05-18 03:31:03.388947

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '045b53174a97'
down_revision = '7fecf51cff1b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dd_app_usage', sa.Column('timestamp', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('dd_app_usage', 'timestamp')
    # ### end Alembic commands ###
