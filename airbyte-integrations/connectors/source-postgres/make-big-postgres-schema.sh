# This script creates lots of tables in a database. It is used to test the handling of large schemas.
# Pre-requisite: follow https://airbyte.com/tutorials/postgres-replication to create the source container.

for i in {1..15000}
do
  docker exec -it airbyte-source psql -U postgres -c "CREATE TABLE users$i(id SERIAL PRIMARY KEY, col1 VARCHAR(200));";
  docker exec -it airbyte-source psql -U postgres -c "INSERT INTO public.users$i(col1) VALUES('record1');";
  docker exec -it airbyte-source psql -U postgres -c "INSERT INTO public.users$i(col1) VALUES('record2');";
  docker exec -it airbyte-source psql -U postgres -c "INSERT INTO public.users$i(col1) VALUES('record3');";
done
