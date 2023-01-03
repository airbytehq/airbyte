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
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .build());
    final String dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();

    try (final DSLContext dslContext = getDslContext(configWithoutDbName)) {
      final Database database = getDatabase(dslContext);
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
    }

    config = Jsons.clone(configWithoutDbName);
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, dbName);
  }

  private static DSLContext getDslContext(final JsonNode baseConfig) {
    return DSLContextFactory.create(
        baseConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        baseConfig.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MSSQLSERVER.getDriverClassName(),
        String.format("jdbc:sqlserver://%s:%d;encrypt=true;trustServerCertificate=true;",
            baseConfig.get(JdbcUtils.HOST_KEY).asText(),
            baseConfig.get(JdbcUtils.PORT_KEY).asInt()),
        null);
  }

  private static Database getDatabase(final DSLContext dslContext) {
    return new Database(dslContext);
  }

}
