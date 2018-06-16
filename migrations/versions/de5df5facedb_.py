"""empty message

Revision ID: de5df5facedb
Revises: 
Create Date: 2018-06-15 22:49:29.106068

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de5df5facedb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('generation_report',
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('renewables', sa.Float(), nullable=False),
    sa.Column('non_renewables', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('timestamp')
    )
    op.create_table('weather_forecast',
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('wind_speed', sa.Float(), nullable=False),
    sa.Column('cloud_cover', sa.Float(), nullable=False),
    sa.Column('temperature', sa.Float(), nullable=False),
    sa.Column('pressure', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('timestamp')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('weather_forecast')
    op.drop_table('generation_report')
    # ### end Alembic commands ###