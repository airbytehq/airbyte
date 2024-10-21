/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.teradata;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.teradata.envclient.TeradataHttpClient;
import io.airbyte.integrations.source.teradata.envclient.dto.CreateEnvironmentRequest;
import io.airbyte.integrations.source.teradata.envclient.dto.DeleteEnvironmentRequest;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import java.util.concurrent.ExecutionException;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.TestInstance;

@Disabled
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class TeradataJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest<TeradataSource, TeradataTestDatabase> {

  private static JsonNode staticConfig;

  public static void cleanUpBeforeStarting() {
    try {
      cleanupEnvironment();
    } catch (final Exception ignored) {}
  }

  @BeforeAll
  static void initEnvironment() throws ExecutionException, InterruptedException {
    staticConfig = Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
    cleanUpBeforeStarting();
    final TeradataHttpClient teradataHttpClient = new TeradataHttpClient(staticConfig.get("env_host").asText());
    var request = new CreateEnvironmentRequest(
        staticConfig.get("env_name").asText(),
        staticConfig.get("env_region").asText(),
        staticConfig.get("env_password").asText());
    var response = teradataHttpClient.createEnvironment(request, staticConfig.get("env_token").asText()).get();
    ((ObjectNode) staticConfig).put("host", response.ip());
    try {
      Class.forName("com.teradata.jdbc.TeraDriver");
    } catch (ClassNotFoundException e) {
      throw new RuntimeException(e);
    }

    COLUMN_CLAUSE_WITH_PK = "id INTEGER NOT NULL, name VARCHAR(200) NOT NULL, updated_at DATE NOT NULL";

    CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s ST_Geometry) NO PRIMARY INDEX;";
    INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES('POLYGON((1 1, 1 3, 6 3, 6 0, 1 1))');";

    COL_TIMESTAMP = "tmstmp";
    INSERT_TABLE_NAME_AND_TIMESTAMP_QUERY = "INSERT INTO %s (name, tmstmp) VALUES ('%s', '%s')";
    COL_TIMESTAMP_TYPE = "TIMESTAMP(0)";
  }

  @AfterAll
  public static void cleanupEnvironment() throws ExecutionException, InterruptedException {
    final TeradataHttpClient teradataHttpClient = new TeradataHttpClient(staticConfig.get("env_host").asText());
    final var request = new DeleteEnvironmentRequest(staticConfig.get("env_name").asText());
    teradataHttpClient.deleteEnvironment(request, staticConfig.get("env_token").asText()).get();
  }

  static void deleteDatabase() {
    executeStatements(List.of(
        statement -> statement.executeUpdate("DELETE DATABASE \"database_name\";"),
        statement -> statement.executeUpdate("DROP DATABASE \"database_name\";")), staticConfig.get("host").asText(),
        staticConfig.get("username").asText(), staticConfig.get("password").asText());
  }

  @Override
  protected TeradataTestDatabase createTestDatabase() {
    executeStatements(List.of(
        statement -> statement.executeUpdate("CREATE DATABASE \"database_name\" AS PERMANENT = 120e6, SPOOL = 120e6;")),
        staticConfig.get("host").asText(), staticConfig.get("username").asText(), staticConfig.get("password").asText());
    return new TeradataTestDatabase(source().toDatabaseConfig(Jsons.clone(staticConfig))).initialized();
  }

  @Override
  public boolean supportsSchemas() {
    return false;
  }

  @Override
  public JsonNode config() {
    return Jsons.clone(staticConfig);
  }

  @Override
  protected TeradataSource source() {
    return new TeradataSource();
  }

  @Override
  public String getFullyQualifiedTableName(String tableName) {
    return staticConfig.get(JdbcUtils.DATABASE_KEY).asText() + "." + tableName;
  }

  private static void executeStatements(List<SqlConsumer> consumers, String host, String username, String password) {
    try (
        Connection con = DriverManager.getConnection("jdbc:teradata://" + host + "/", username, password);
        Statement stmt = con.createStatement();) {
      for (SqlConsumer consumer : consumers) {
        consumer.accept(stmt);
      }
    } catch (SQLException sqle) {
      throw new RuntimeException(sqle);
    }

  }

  @FunctionalInterface
  private interface SqlConsumer {

    void accept(Statement statement) throws SQLException;

  }

}
