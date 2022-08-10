/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import org.jooq.DSLContext;
import org.testcontainers.containers.MSSQLServerContainer;

public class MssqlSourceDatatypeTest extends AbstractMssqlSourceDatatypeTest {

  @Override
  protected Database setupDatabase() throws Exception {
    container = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2019-latest")
        .acceptLicense();
    container.start();

    final JsonNode configWithoutDbName = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, container.getHost())
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.USERNAME_KEY, container.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .build());

    dslContext = getDslContext(configWithoutDbName);
    final Database database = getDatabase(dslContext);
    database.query(ctx -> {
      ctx.fetch(String.format("CREATE DATABASE %s;", DB_NAME));
      ctx.fetch(String.format("USE %s;", DB_NAME));
      return null;
    });

    config = Jsons.clone(configWithoutDbName);
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, DB_NAME);

    return database;
  }

  private static DSLContext getDslContext(final JsonNode config) {
    return DSLContextFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MSSQLSERVER.getDriverClassName(),
        String.format("jdbc:sqlserver://%s:%d;",
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt()),
        null);
  }

  private static Database getDatabase(final DSLContext dslContext) {
    return new Database(dslContext);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    dslContext.close();
    container.stop();
    container.close();
  }

  @Override
  public boolean testCatalog() {
    return true;
  }

}
