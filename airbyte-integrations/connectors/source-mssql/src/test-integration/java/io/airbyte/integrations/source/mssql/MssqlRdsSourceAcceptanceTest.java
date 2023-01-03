/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import java.nio.file.Path;
import java.sql.SQLException;
import org.apache.commons.lang3.RandomStringUtils;
import org.jooq.DSLContext;

public class MssqlRdsSourceAcceptanceTest extends MssqlSourceAcceptanceTest {

  private JsonNode baseConfig;

  @Override
  protected void setupEnvironment(final TestDestinationEnv environment) throws SQLException {
    baseConfig = getStaticConfig();
    final String dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();
    try (final DSLContext dslContext = getDslContext(baseConfig)) {
      final Database database = getDatabase(dslContext);
      database.query(ctx -> {
        ctx.fetch(String.format("CREATE DATABASE %s;", dbName));
        ctx.fetch(String.format("ALTER DATABASE %s SET AUTO_CLOSE OFF WITH NO_WAIT;", dbName));
        ctx.fetch(String.format("USE %s;", dbName));
        ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), born DATETIMEOFFSET(7));");
        ctx.fetch(
            "INSERT INTO id_and_name (id, name, born) VALUES (1,'picard', '2124-03-04T01:01:01Z'),  (2, 'crusher', '2124-03-04T01:01:01Z'), (3, 'vash', '2124-03-04T01:01:01Z');");
        return null;
      });
    }

    config = Jsons.clone(baseConfig);
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, dbName);
  }

  public JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  private DSLContext getDslContext(final JsonNode baseConfig) {
    String additionalParameter = "";
    final JsonNode sslMethod = baseConfig.get("ssl_method");
    switch (sslMethod.get("ssl_method").asText()) {
      case "unencrypted" -> additionalParameter = "encrypt=false;";
      case "encrypted_trust_server_certificate" -> additionalParameter = "encrypt=true;trustServerCertificate=true;";
    }
    return DSLContextFactory.create(
        baseConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        baseConfig.get(JdbcUtils.PASSWORD_KEY).asText(),
        DatabaseDriver.MSSQLSERVER.getDriverClassName(),
        String.format("jdbc:sqlserver://%s:%d;%s",
            baseConfig.get(JdbcUtils.HOST_KEY).asText(),
            baseConfig.get(JdbcUtils.PORT_KEY).asInt(),
            additionalParameter),
        null);
  }

  private Database getDatabase(final DSLContext dslContext) {
    return new Database(dslContext);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    final String database = config.get(JdbcUtils.DATABASE_KEY).asText();
    try (final DSLContext dslContext = getDslContext(baseConfig)) {
      getDatabase(dslContext).query(ctx -> {
        ctx.fetch(String.format("ALTER DATABASE %s SET single_user with rollback immediate;", database));
        ctx.fetch(String.format("DROP DATABASE %s;", database));
        return null;
      });
    }
  }

}
