# Development plan timetable prototype

## Getting started

Create a python virtualenv then run:

    make init

Create a local development postgres db

    createdb development_plan_timetable

Create or update db schema

    make upgrade-db


There's a directory of sample/seed data for this application [here](/data). There are commands
for loading this into the application database.

Load data

    make load-data

Drop local data

    make drop-data

To run the application run:

    make run
