/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.json.Jsons;
import java.sql.SQLException;
import java.util.Map;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.DSLContext;
import org.junit.jupiter.api.AfterAll;
import org.testcontainers.containers.MSSQLServerContainer;

public class SslEnabledMssqlSourceAcceptanceTest extends MssqlSourceAcceptanceTest {

  @AfterAll
  public static void closeContainer() {
    if (db != null) {
      db.close();
      db.stop();
    }
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws SQLException {
    if (db == null) {
      db = new MSSQLServerContainer<>("mcr.microsoft.com/mssql/server:2022-RTM-CU2-ubuntu-20.04").acceptLicense();
      db.start();
    }

    final JsonNode configWithoutDbName = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(db))
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(db))
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
    ((ObjectNode) config).put("ssl_method", Jsons.jsonNode(Map.of("ssl_method", "encrypted_trust_server_certificate")));
  }

  private DSLContext getDslContext(final JsonNode baseConfig) {
    return DSLContextFactory.create(
        baseConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        baseConfig.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MSSQLSERVER.getDriverClassName(),
        String.format("jdbc:sqlserver://%s:%d;encrypt=true;trustServerCertificate=true;",
            db.getHost(),
            db.getFirstMappedPort()),
        null);
  }

  private static Database getDatabase(final DSLContext dslContext) {
    return new Database(dslContext);
  }

}
