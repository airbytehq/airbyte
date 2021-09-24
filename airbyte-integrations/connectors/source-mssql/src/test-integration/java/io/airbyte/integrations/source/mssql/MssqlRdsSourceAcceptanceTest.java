/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import java.nio.file.Path;
import java.sql.SQLException;
import org.apache.commons.lang3.RandomStringUtils;

public class MssqlRdsSourceAcceptanceTest extends MssqlSourceAcceptanceTest {

  private JsonNode baseConfig;

  @Override
  protected void setupEnvironment(TestDestinationEnv environment) throws SQLException {
    baseConfig = getStaticConfig();
    String dbName = "db_" + RandomStringUtils.randomAlphabetic(10).toLowerCase();

    final Database database = getDatabase();
    database.query(ctx -> {
      ctx.fetch(String.format("CREATE DATABASE %s;", dbName));
      ctx.fetch(String.format("ALTER DATABASE %s SET AUTO_CLOSE OFF WITH NO_WAIT;", dbName));
      ctx.fetch(String.format("USE %s;", dbName));
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), born DATETIMEOFFSET(7));");
      ctx.fetch(
          "INSERT INTO id_and_name (id, name, born) VALUES (1,'picard', '2124-03-04T01:01:01Z'),  (2, 'crusher', '2124-03-04T01:01:01Z'), (3, 'vash', '2124-03-04T01:01:01Z');");
      return null;
    });

    config = Jsons.clone(baseConfig);
    ((ObjectNode) config).put("database", dbName);
  }

  public JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  private Database getDatabase() {
    String additionalParameter = "";
    JsonNode sslMethod = baseConfig.get("ssl_method");
    switch (sslMethod.get("ssl_method").asText()) {
      case "unencrypted" -> additionalParameter = "encrypt=false;";
      case "encrypted_trust_server_certificate" -> additionalParameter = "encrypt=true;trustServerCertificate=true;";
    }
    return Databases.createDatabase(
        baseConfig.get("username").asText(),
        baseConfig.get("password").asText(),
        String.format("jdbc:sqlserver://%s:%s;%s",
            baseConfig.get("host").asText(),
            baseConfig.get("port").asInt(),
            additionalParameter),
        "com.microsoft.sqlserver.jdbc.SQLServerDriver",
        null);
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    String database = config.get("database").asText();
    getDatabase().query(ctx -> {
      ctx.fetch(String.format("ALTER DATABASE %s SET single_user with rollback immediate;", database));
      ctx.fetch(String.format("DROP DATABASE %s;", database));
      return null;
    });
  }

}
