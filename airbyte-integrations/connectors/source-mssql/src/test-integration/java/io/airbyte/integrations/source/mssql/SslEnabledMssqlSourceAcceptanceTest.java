/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import java.sql.SQLException;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.DSLContext;
import org.testcontainers.containers.MSSQLServerContainer;
import org.testcontainers.utility.DockerImageName;

public class SslEnabledMssqlSourceAcceptanceTest extends MssqlSourceAcceptanceTest {

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws SQLException {
    db = new MSSQLServerContainer<>(DockerImageName
        .parse("airbyte/mssql_ssltest:dev")
        .asCompatibleSubstituteFor("mcr.microsoft.com/mssql/server"))
            .acceptLicense();
    db.start();

    final JsonNode configWithoutDbName = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", db.getFirstMappedPort())
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .build());
    final String dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();

    final Database database = getDatabase(configWithoutDbName);
    database.query(ctx -> {
      ctx.fetch(String.format("CREATE DATABASE %s;", dbName));
      ctx.fetch(String.format("USE %s;", dbName));
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), born DATETIMEOFFSET(7));");
      ctx.fetch(
          "INSERT INTO id_and_name (id, name, born) VALUES " +
              "(1,'picard', '2124-03-04T01:01:01Z'),  " +
              "(2, 'crusher', '2124-03-04T01:01:01Z'), " +
              "(3, 'vash', '2124-03-04T01:01:01Z');");
      return null;
    });

    config = Jsons.clone(configWithoutDbName);
    ((ObjectNode) config).put("database", dbName);
  }

  private static Database getDatabase(final JsonNode baseConfig) {
    final DSLContext dslContext = DSLContextFactory.create(
        baseConfig.get("username").asText(),
        baseConfig.get("password").asText(),
        DatabaseDriver.MSSQLSERVER.getDriverClassName(),
        String.format("jdbc:sqlserver://%s:%s;encrypt=true;trustServerCertificate=true;",
            baseConfig.get("host").asText(),
            baseConfig.get("port").asInt()), null);
    return new Database(dslContext);
  }

}
