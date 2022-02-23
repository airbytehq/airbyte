## Testing a temporal migration

`tools/bin/test_temporal_migration.sh` is available to test that a bump of the temporal version won't break the docker compose build. Here is what 
the script does:
- checkout master
- build the docker image
- run docker compose up in the background
- Sleep for 75 secondes
- shutdown docker compose
- checkout the commit being tested
- build the docker image
- run docker compose up.

At the end of the script you should be able to access a local airbyte in `localhost:8000`.
