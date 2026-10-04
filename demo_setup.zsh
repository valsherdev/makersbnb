#!/usr/bin/env zsh

echo ">>> Creating new db"
dropdb makersbnb-db_test
createdb makersbnb-db_test

echo ">>> Creating tables"
psql makersbnb-db_test < seeds/users.sql
psql makersbnb-db_test < seeds/listings.sql
psql makersbnb-db_test < seeds/booking_requests.sql
psql makersbnb-db_test < seeds/confirmed_bookings.sql

echo ">>> Insert test data"
psql makersbnb-db_test < seeds/add_to_users.sql
psql makersbnb-db_test < seeds/add_to_listings.sql

echo ">>> Starting app"
APP_ENV=test python app.py