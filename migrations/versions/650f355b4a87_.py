"""empty message

Revision ID: 650f355b4a87
Revises: 6e421dcb3320
Create Date: 2022-10-20 17:25:45.659576

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '650f355b4a87'
down_revision = '6e421dcb3320'
branch_labels = None
depends_on = '898404f56424'


def upgrade():
    # set the autoincrementing ids
    op.execute(
        '''
        SELECT setval('public."Artist_id_seq"', (SELECT max(id) FROM public."Artist"))
        '''
    )
    op.execute(
        '''
        SELECT setval('public."Venue_id_seq"', (SELECT max(id) FROM public."Venue"))
        '''
    )
    op.execute(
        '''
        SELECT setval('public."Show_id_seq"', (SELECT max(id) FROM public."Show"))
        '''
    )


def downgrade():
    # reverse the autoincrementing ids
    op.execute(
        '''
        SELECT setval('public."Artist_id_seq"', 1)
        '''
    )
    op.execute(
        '''
        SELECT setval('public."Venue_id_seq"', 1)
        '''
    )
    op.execute(
        '''
        SELECT setval('public."Show_id_seq"', 1)
        '''
    )
