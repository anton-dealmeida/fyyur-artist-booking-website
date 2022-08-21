import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect# DATABASE SETTINGS
pg_db_username = 'postgres'
pg_db_password = 'password123!'
pg_db_name = 'fyyur-db'
pg_db_hostname = 'localhost'

# IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(DB_USER=pg_db_username,
                                                                                        DB_PASS=pg_db_password,
                                                                                        DB_ADDR=pg_db_hostname,
                                                                                        DB_NAME=pg_db_name)
SQLALCHEMY_TRACK_MODIFICATIONS = False
