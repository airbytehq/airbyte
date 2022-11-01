/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.integrations.util.HostPortResolver;
import java.sql.SQLException;
import org.jooq.SQLDialect;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class PostgresSourceDatatypeTest extends AbstractPostgresSourceDatatypeTest {

  @Override
  protected Database setupDatabase() throws SQLException {
    container = new PostgreSQLContainer<>("postgres:14-alpine")
        .withCopyFileToContainer(MountableFile.forClasspathResource("postgresql.conf"),
            "/etc/postgresql/postgresql.conf")
        .withCommand("postgres -c config_file=/etc/postgresql/postgresql.conf");
    container.start();
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(container))
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(container))
        .put(JdbcUtils.DATABASE_KEY, container.getDatabaseName())
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .put(JdbcUtils.SSL_KEY, false)
        .put("replication_method", replicationMethod)
        .build());

    dslContext = DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            container.getHost(),
            container.getFirstMappedPort(),
            config.get(JdbcUtils.DATABASE_KEY).asText()),
        SQLDialect.POSTGRES);
    final Database database = new Database(dslContext);

    database.query(ctx -> {
      ctx.execute(String.format("CREATE SCHEMA %S;", SCHEMA_NAME));
      ctx.execute("CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');");
      ctx.execute("CREATE TYPE inventory_item AS (name text, supplier_id integer, price numeric);");
      // In one of the test case, we have some money values with currency symbol. Postgres can only
      // understand those money values if the symbol corresponds to the monetary locale setting. For
      // example,
      // if the locale is 'en_GB', '£100' is valid, but '$100' is not. So setting the monetary locate is
      // necessary here to make sure the unit test can pass, no matter what the locale the runner VM has.
      ctx.execute("SET lc_monetary TO 'en_US.utf8';");
      // Set up a fixed timezone here so that timetz and timestamptz always have the same time zone
      // wherever the tests are running on.
      ctx.execute("SET TIMEZONE TO 'MST'");
      ctx.execute("CREATE EXTENSION hstore;");
      return null;
    });

    return database;
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    dslContext.close();
    container.close();
  }

  @Override
  public boolean testCatalog() {
    return true;
  }

}
