# badmintellect

## Features of the application
* Account system with login and signup
* Ability to view and create reservations
* Ability to modify reservations
* Search for reservations
* Tags for reservations
* Commenting on reservations

## TO:DO
* More sophisticated user profile including a description and a profile picture.
* Search by tags and other filters
* Statistics page
* Ability to join a reservation.

## Using the application
1. Initialize the database
```
sqlite3 database.db < schema.sql
```

2. Start the server (development only)
```
flask run
```