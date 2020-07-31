#!/bin/sh

# Setup local source database
./init_db.sh src-postgres 9988 ./populate_db.sql

# Setup Target database
./init_db.sh target-postgres 9999

# Load data from local database

# load catalog then edit it
#./tap-postgres/bin/tap-postgres --config local_tap_config.json --discover > local_tap_catalog.json
./tap-postgres/bin/tap-postgres --config local_tap_config.json --properties local_tap_catalog.json | ./target-postgres/bin/target-postgres --config target_config.json >> state.json

# Load data from remote database
#./tap-postgres/bin/tap-postgres --config remote_tap_config.json
./tap-postgres/bin/tap-postgres --config remote_tap_config.json --properties remote_tap_catalog.json | ./target-postgres/bin/target-postgres --config target_config.json >> state.json
