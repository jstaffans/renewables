"""empty message

Revision ID: 772f3a38c932
Revises: 
Create Date: 2018-01-31 21:43:38.665826

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '772f3a38c932'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('generation_report',
    sa.Column('ba_name', sa.String(), nullable=False),
    sa.Column('control_area', sa.String(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('renewables', sa.Float(), nullable=False),
    sa.Column('non_renewables', sa.Float(), nullable=False),
    sa.PrimaryKeyConstraint('ba_name', 'control_area', 'timestamp')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('generation_report')
    # ### end Alembic commands ###
