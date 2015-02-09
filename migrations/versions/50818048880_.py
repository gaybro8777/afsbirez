"""empty message

Revision ID: 50818048880
Revises: 3c71c2aac63
Create Date: 2015-02-04 11:44:12.780163

"""

# revision identifiers, used by Alembic.
revision = '50818048880'
down_revision = '3c71c2aac63'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('topics', sa.Column('agency', sa.Text()))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('topics', 'agency')
    ### end Alembic commands ###
