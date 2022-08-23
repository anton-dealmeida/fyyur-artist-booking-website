"""empty message

Revision ID: 898404f56424
Revises: eb98a69265cd
Create Date: 2022-08-20 15:59:41.392296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '898404f56424'
down_revision = 'eb98a69265cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('description', sa.String(), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('website', sa.String(), nullable=True))
    op.add_column('Venue', sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    op.drop_column('Venue', 'website')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'description')
    # ### end Alembic commands ###
