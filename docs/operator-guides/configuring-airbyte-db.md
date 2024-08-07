---
products: oss-*
---

# Configuring the Airbyte Database

Airbyte uses different objects to store internal state and metadata. This data is stored and manipulated by the various Airbyte components, but you have the ability to manage the deployment of this database in the following two ways:

- Using the default Postgres database that Airbyte spins-up as part of the Docker service described in the `docker-compose.yml` file: `airbyte/db`.
- Through a dedicated custom Postgres instance \(the `airbyte/db` is in this case unused, and can therefore be removed or de-activated from the `docker-compose.yml` file\). It's not a good practice to deploy mission-critical databases on Docker or Kubernetes.
  Using a dedicated instance will provide more reliability to your Airbyte deployment.
  Moreover, using a Cloud-managed Postgres instance (such as AWS RDS our GCP Cloud SQL), you will benefit from automatic backup and fine-grained sizing. You can start with a pretty small instance, but according to your Airbyte usage, the job database might grow and require more storage if you are not truncating the job history.

The various entities are persisted in two internal databases:

- Job database
  - Data about executions of Airbyte Jobs and various runtime metadata.
  - Data about the internal orchestrator used by Airbyte, Temporal.io \(Tasks, Workflow data, Events, and visibility data\).
- Config database
  - Connectors, Sync Connections and various Airbyte configuration objects.

Note that no actual data from the source \(or destination\) connectors ever transits or is retained in this internal database.

If you need to interact with it, for example, to make back-ups or perform some clean-up maintenances, you can also gain access to the Export and Import functionalities of this database via the API or the UI \(in the Admin page, in the Configuration Tab\).

## Connecting to an External Postgres database

Let's walk through what is required to use a Postgres instance that is not managed by Airbyte. First, for the sake of the tutorial, we will run a new instance of Postgres in its own docker container with the command below. If you already have Postgres running elsewhere, you can skip this step and use the credentials for that in future steps.

```bash
docker run --rm --name airbyte-postgres -e POSTGRES_PASSWORD=password -p 3000:5432 -d postgres
```

In order to configure Airbyte services with this new database, we need to edit the following environment variables declared in the `.env` file \(used by the docker-compose command afterward\):

```bash
DATABASE_USER=postgres
DATABASE_PASSWORD=password
DATABASE_HOST=host.docker.internal # refers to localhost of host
DATABASE_PORT=3000
DATABASE_DB=postgres
```

By default, the Config Database and the Job Database use the same database instance based on the above setting. It is possible, however, to separate the former from the latter by specifying a separate parameters. For example:

```bash
CONFIG_DATABASE_USER=airbyte_config_db_user
CONFIG_DATABASE_PASSWORD=password
```

Additionally, you must redefine the JDBC URL constructed in the environment variable `DATABASE_URL` to include the correct host, port, and database. If you need to provide extra arguments to the JDBC driver \(for example, to handle SSL\) you should add it here as well:

```bash
DATABASE_URL=jdbc:postgresql://host.docker.internal:3000/postgres?ssl=true&sslmode=require
```

Same for the config database if it is separate from the job database:

```bash
CONFIG_DATABASE_URL=jdbc:postgresql://<host>:<port>/<database>?<extra-parameters>
```

## Initializing the database

:::info

This step is only required when you setup Airbyte with a custom database for the first time.

:::

If you provide an empty database to Airbyte and start Airbyte up for the first time, the server will automatically create the relevant tables in your database, and copy the data. Please make sure:

- The database exists in the server.
- The user has both read and write permissions to the database.
- The database is empty.
  - If the database is not empty, and has a table that shares the same name as one of the Airbyte tables, the server will assume that the database has been initialized, and will not copy the data over, resulting in server failure. If you run into this issue, just wipe out the database, and launch the server again.

## Accessing the default database located in docker airbyte-db

In extraordinary circumstances while using the default `airbyte-db` Postgres database, if a developer wants to access the data that tracks jobs, they can do so with the following instructions.

As we've seen previously, the credentials for the database are specified in the `.env` file that is used to run Airbyte. By default, the values are:

```text
DATABASE_USER=docker
DATABASE_PASSWORD=docker
DATABASE_DB=airbyte
```

If you have overridden these defaults, you will need to substitute them in the instructions below.

The following command will allow you to access the database instance using `psql`.

```text
docker exec -ti airbyte-db psql -U docker -d airbyte
```

Following tables are created

1. `workspace` : Contains workspace information such as name, notification configuration, etc.
2. `actor_definition` : Contains the source and destination connector definitions.
3. `actor` : Contains source and destination connectors information.
4. `actor_oauth_parameter` : Contains source and destination oauth parameters.
5. `operation` : Contains dbt and custom normalization operations.
6. `connection` : Contains connection configuration such as catalog details, source, destination, etc.
7. `connection_operation` : Contains the operations configured for a given connection.
8. `state`. Contains the last saved state for a connection.
