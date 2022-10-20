"""empty message

Revision ID: 6e421dcb3320
Revises: 898404f56424
Create Date: 2022-08-20 16:22:18.633617

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table
from app import Artist, Show, Venue

# revision identifiers, used by Alembic.
revision = '6e421dcb3320'
down_revision = '898404f56424'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
                    sa.Column('id', sa.Integer(), nullable=False,
                              autoincrement=True),
                    sa.Column('venue_id', sa.Integer(), nullable=False),
                    sa.Column('artist_id', sa.Integer(), nullable=False),
                    sa.Column('start_time', sa.String(), nullable=False),
                    sa.ForeignKeyConstraint(
                        ['artist_id'], ['Artist.id'], ),
                    sa.ForeignKeyConstraint(
                        ['venue_id'], ['Venue.id'], ),
                    sa.PrimaryKeyConstraint(
                        'id', 'venue_id', 'artist_id')
                    )
    op.add_column('Artist', sa.Column(
        'seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column(
        'seeking_description', sa.String(), nullable=True))
    op.add_column('Artist', sa.Column(
        'website_link', sa.String(), nullable=True))
    # ### end Alembic commands ###

    # data seed
    seed()

    # reset auto increment
    # op.execute(
    #     '''
    #         SELECT setval(\'artist_id_seq\', max(id)) FROM Artist;
    #         SELECT setval(\'venue_id_seq\', max(id)) FROM Venue;
    #         SELECT setval(\'show_id_seq\', max(id)) FROM Show;
    #         '''
    # )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'website_link')
    op.drop_column('Artist', 'seeking_description')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_table('Show')
    # ### end Alembic commands ###


def seed():
    artists = [
        {'id': 1, 'name': 'Guns N Petals', 'city': 'San Francisco', 'state': 'CA', 'phone': '326-123-5000', 'genres': ['Rock n Roll'], 'image_link': 'https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80',
         'facebook_link': 'https://www.facebook.com/GunsNPetals', 'seeking_venue': True, 'seeking_description': 'Looking for shows to perform at in the San Francisco Bay Area!', 'website_link': 'https://www.gunsnpetalsband.com'},
        {'id': 2, 'name': 'Matt Quevedo', 'city': 'New York', 'state': 'NY', 'phone': '300-400-5000', 'genres': ['Jazz'], 'image_link': 'https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80',
         'facebook_link': 'https://www.facebook.com/mattquevedo923251523', 'seeking_venue': False, 'seeking_description': '', 'website_link': ''},
        {'id': 3, 'name': 'The Wild Sax Band', 'city': 'San Francisco', 'state': 'CA', 'phone': '432-325-5432', 'genres': ['Jazz', 'Classical'],
         'image_link': 'https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80', 'facebook_link': '', 'seeking_venue': False, 'seeking_description': '', 'website_link': ''}
    ]

    venues = [
        {'id': 1, 'name': 'The Musical Hop', 'city': 'San Francisco', 'state': 'CA', 'address': '1015 Folsom Street', 'phone': '123-123-1234', 'image_link': 'https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60',
         'facebook_link': 'https://www.facebook.com/TheMusicalHop', 'description': 'We are on the lookout for a local artist to play every two weeks. Please call us.', 'seeking_talent': True, 'website_link': 'https://www.themusicalhop.com', 'genres': ['Jazz', 'Reggae', 'Swing', 'Classical', 'Folk']},
        {'id': 2, 'name': 'The Dueling Pianos Bar', 'city': 'New York', 'state': 'NY', 'address': '335 Delancey Street', 'phone': '914-003-1132', 'image_link': 'https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80',
         'facebook_link': 'https://www.facebook.com/theduelingpianos', 'description': '', 'seeking_talent': False, 'website_link': 'https://www.theduelingpianos.com', 'genres': ['Classical', 'R&B', 'Hip-Hop']},
        {'id': 3, 'name': 'Park Square Live Music & Coffee', 'city': 'San Francisco', 'state': 'CA', 'address': '34 Whiskey Moore Ave', 'phone': '415-000-1234', 'image_link': 'https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80',
         'facebook_link': 'https://www.facebook.com/ParkSquareLiveMusicAndCoffee', 'description': '', 'seeking_talent': False, 'website_link': 'https://www.parksquarelivemusicandcoffee.com', 'genres': ['Rock n Roll', 'Jazz', 'Classical', 'Folk']}
    ]

    shows = [
        {'id': 1, 'venue_id': 1, 'artist_id': 1,
         'start_time': '2019-05-21 21:30:00'},
        {'id': 2, 'venue_id': 3, 'artist_id': 2,
         'start_time': '2019-06-15 23:00:00'},
        {'id': 3, 'venue_id': 3, 'artist_id': 3,
         'start_time': '2035-04-01 20:00:00'},
        {'id': 4, 'venue_id': 3, 'artist_id': 3,
         'start_time': '2035-04-08 20:00:00'},
        {'id': 5, 'venue_id': 3, 'artist_id': 3,
         'start_time': '2035-04-18 20:00:00'}
    ]

    op.bulk_insert(
        Artist.__table__,
        artists
    )
    op.bulk_insert(
        Venue.__table__,
        venues
    )
    op.bulk_insert(
        Show.__table__,
        shows
    )
