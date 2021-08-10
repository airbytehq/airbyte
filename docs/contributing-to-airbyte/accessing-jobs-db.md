# Accessing Jobs Database

In extraordinary circumstances, if a developer wants to access the database that tracks jobs, they can do so with the following instructions.

The credentials for the database are specified in the `.env` file that is used to run Airbyte. By default, the values are:
```shell
DATABASE_USER=docker
DATABASE_PASSWORD=docker
DATABASE_DB=airbyte
```

If you have overridden these defaults, you will need to substitute them in the instructions below.

The following command will allow you to access the database instance using `psql`. You can find the schema for the database [here](https://github.com/airbytehq/airbyte/blob/master/airbyte-db/src/main/resources/schema.sql).

```shell
docker exec -ti airbyte-db psql -U docker -d airbyte
```
