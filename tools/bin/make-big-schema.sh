for i in {1..15000}
do
  docker exec -it airbyte-source psql -U postgres -c "CREATE TABLE users$i(id SERIAL PRIMARY KEY, col1 VARCHAR(200));";
  docker exec -it airbyte-source psql -U postgres -c "INSERT INTO public.users$i(col1) VALUES('record1');";
  docker exec -it airbyte-source psql -U postgres -c "INSERT INTO public.users$i(col1) VALUES('record2');";
  docker exec -it airbyte-source psql -U postgres -c "INSERT INTO public.users$i(col1) VALUES('record3');";
done