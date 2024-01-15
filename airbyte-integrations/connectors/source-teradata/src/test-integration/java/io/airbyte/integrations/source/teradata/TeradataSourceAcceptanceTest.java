/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.teradata;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.teradata.envclient.TeradataHttpClient;
import io.airbyte.integrations.source.teradata.envclient.dto.CreateEnvironmentRequest;
import io.airbyte.integrations.source.teradata.envclient.dto.DeleteEnvironmentRequest;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.HashMap;
import java.util.List;
import java.util.concurrent.ExecutionException;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.TestInstance;

@Disabled
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class TeradataSourceAcceptanceTest extends SourceAcceptanceTest {

  private static final String CREATE_DATABASE =
      "CREATE DATABASE \"database_name\" AS PERMANENT = 120e6, SPOOL = 120e6;";

  private static final String CREATE_TABLE = """
                                             CREATE TABLE database_name.table_name(
                                               id INTEGER NOT NULL,
                                               strength VARCHAR(30) NOT NULL,
                                               agility INTEGER NOT NULL,
                                               updated_at TIMESTAMP(6),
                                               PRIMARY KEY(id))
                                             """;

  private static final String DELETE_DATABASE = "DELETE DATABASE \"database_name\";";

  private static final String DROP_DATABASE = "DROP DATABASE \"database_name\";";

  private static final String INSERT =
      "INSERT INTO database_name.table_name VALUES(%d, '%s', %d, CURRENT_TIMESTAMP(6))";

  private JsonNode jsonConfig;

  @BeforeAll
  void initEnvironment() throws ExecutionException, InterruptedException {
    jsonConfig = Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
    TeradataHttpClient teradataHttpClient = new TeradataHttpClient(jsonConfig.get("env_host").asText());
    var request = new CreateEnvironmentRequest(
        jsonConfig.get("env_name").asText(),
        jsonConfig.get("env_region").asText(),
        jsonConfig.get("env_password").asText());
    var response = teradataHttpClient.createEnvironment(request, jsonConfig.get("env_token").asText()).get();
    ((ObjectNode) jsonConfig).put("host", response.ip());
    try {
      Class.forName("com.teradata.jdbc.TeraDriver");
    } catch (ClassNotFoundException e) {
      throw new RuntimeException(e);
    }
  }

  @AfterAll
  void cleanupEnvironment() throws ExecutionException, InterruptedException {
    TeradataHttpClient teradataHttpClient = new TeradataHttpClient(jsonConfig.get("env_host").asText());
    var request = new DeleteEnvironmentRequest(jsonConfig.get("env_name").asText());
    teradataHttpClient.deleteEnvironment(request, jsonConfig.get("env_token").asText()).get();
  }

  @Override
  protected void setupEnvironment(final TestDestinationEnv testEnv) {
    var config = getConfig();
    executeStatements(List.of(
        statement -> statement.executeUpdate(CREATE_DATABASE),
        statement -> statement.executeUpdate(CREATE_TABLE),
        statement -> statement.executeUpdate(String.format(INSERT, 1, "laser power", 9)),
        statement -> statement.executeUpdate(String.format(INSERT, 2, "night vision", 7))), config.get("host").asText(),
        config.get("username").asText(), config.get("password").asText());

  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    var config = getConfig();
    executeStatements(List.of(
        statement -> statement.executeUpdate(DELETE_DATABASE),
        statement -> statement.executeUpdate(DROP_DATABASE)), config.get("host").asText(), config.get("username").asText(),
        config.get("password").asText());
  }

  @Override
  protected String getImageName() {
    return "airbyte/source-teradata:dev";
  }

  @Override
  protected ConnectorSpecification getSpec() throws Exception {
    return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.clone(jsonConfig);
  }

  @Override
  protected ConfiguredAirbyteCatalog getConfiguredCatalog() {
    return createConfiguredAirbyteCatalog();
  }

  @Override
  protected JsonNode getState() {
    return Jsons.jsonNode(new HashMap<>());
  }

  static ConfiguredAirbyteCatalog createConfiguredAirbyteCatalog() {
    return new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(List.of("updated_at"))
            .withPrimaryKey(List.of(List.of("id")))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                "table_name",
                "database_name",
                Field.of("strength", JsonSchemaType.STRING),
                Field.of("agility", JsonSchemaType.INTEGER),
                Field.of("updated_at", JsonSchemaType.TIMESTAMP_WITH_TIMEZONE_V1))
                .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
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
