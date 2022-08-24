#!/bin/bash

# Apply Database Migrations
python -m flask db upgrade

# Start Python Flask Application
python -m flask run --host="0.0.0.0"
