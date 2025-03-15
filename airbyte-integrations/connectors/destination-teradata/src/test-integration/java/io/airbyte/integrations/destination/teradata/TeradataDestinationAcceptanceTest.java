/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.destination.teradata.envclient.TeradataHttpClient;
import io.airbyte.integrations.destination.teradata.envclient.dto.*;
import io.airbyte.integrations.destination.teradata.envclient.exception.BaseException;
import io.airbyte.integrations.destination.teradata.util.TeradataConstants;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.SQLException;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ExecutionException;
import javax.sql.DataSource;
import org.junit.jupiter.api.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public class TeradataDestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(TeradataDestinationAcceptanceTest.class);
  private final StandardNameTransformer namingResolver = new StandardNameTransformer();

  private static final String SCHEMA_NAME = Strings.addRandomSuffix("acc_test", "_", 5);

  private static final String CREATE_DATABASE = "CREATE DATABASE \"%s\" AS PERMANENT = 60e6, SPOOL = 60e6 SKEW = 10 PERCENT";

  private static final String DELETE_DATABASE = "DELETE DATABASE \"%s\"";

  private static final String DROP_DATABASE = "DROP DATABASE \"%s\"";

  private JsonNode configJson;
  private JdbcDatabase database;
  private DataSource dataSource;
  private final TeradataDestination destination = new TeradataDestination();

  @Override
  protected String getImageName() {
    return "airbyte/destination-teradata:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  @BeforeAll
  void initEnvironment() throws Exception {
    this.configJson = Jsons.clone(getStaticConfig());
    TeradataHttpClient teradataHttpClient = new TeradataHttpClient(configJson.get("env_url").asText());
    String name = configJson.get("env_name").asText();
    String token = configJson.get("env_token").asText();
    var getRequest = new GetEnvironmentRequest(name);
    EnvironmentResponse response = null;
    try {
      response = teradataHttpClient.getEnvironment(getRequest, token);
    } catch (BaseException be) {
      LOGGER.error("Environemnt " + name + " is not available. " + be.getMessage());
    }
    if (response == null || response.ip() == null) {
      var request = new CreateEnvironmentRequest(
          name,
          configJson.get("env_region").asText(),
          configJson.get("env_password").asText());
      response = teradataHttpClient.createEnvironment(request, token).get();
      LOGGER.info("Environemnt " + configJson.get("env_name").asText() + " is created successfully ");
    } else if (response.state() == EnvironmentResponse.State.STOPPED) {
      var request = new EnvironmentRequest(name, new OperationRequest("start"));
      teradataHttpClient.startEnvironment(request, token);
    }
    ((ObjectNode) configJson).put("host", response.ip());
    if (configJson.get("password") == null) {
      ((ObjectNode) configJson).put("password", configJson.get("env_password").asText());
    }
  }

  @AfterAll
  void cleanupEnvironment() throws ExecutionException, InterruptedException {
    try {
      TeradataHttpClient teradataHttpClient = new TeradataHttpClient(configJson.get("env_url").asText());
      var request = new DeleteEnvironmentRequest(configJson.get("env_name").asText());
      teradataHttpClient.deleteEnvironment(request, configJson.get("env_token").asText());
      LOGGER.info("Environemnt " + configJson.get("env_name").asText() + " is deleted successfully ");
    } catch (BaseException be) {
      LOGGER.error("Environemnt " + configJson.get("env_name").asText() + " is not available. " + be.getMessage());
    }
  }

  public JsonNode getStaticConfig() throws Exception {
    return Jsons.deserialize(Files.readString(Paths.get("secrets/config.json")));
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    JsonNode failureConfig = Jsons.clone(this.configJson);
    ((ObjectNode) failureConfig).put("password", "wrongpassword");
    return failureConfig;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace);

  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName)
      throws SQLException {
    return database.bufferedResultSetQuery(
        connection -> {
          var statement = connection.createStatement();
          return statement.executeQuery(
              String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName,
                  JavaBaseConstants.COLUMN_NAME_EMITTED_AT));
        },
        rs -> Jsons.deserialize(rs.getString(JavaBaseConstants.COLUMN_NAME_DATA)));
  }

  @Override
  protected void setup(TestDestinationEnv testEnv, HashSet<String> TEST_SCHEMAS) {
    final String createSchemaQuery = String.format(CREATE_DATABASE, SCHEMA_NAME);
    try {
      ((ObjectNode) configJson).put("schema", SCHEMA_NAME);
      dataSource = getDataSource(configJson);
      database = destination.getDatabase(dataSource);
      database.execute(createSchemaQuery);
    } catch (Exception e) {
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e, "Database " + SCHEMA_NAME + " creation got failed.");
    }
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws Exception {
    final String deleteQuery = String.format(String.format(DELETE_DATABASE, SCHEMA_NAME));
    final String dropQuery = String.format(String.format(DROP_DATABASE, SCHEMA_NAME));
    try {
      database.execute(deleteQuery);
      database.execute(dropQuery);
    } catch (Exception e) {
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e, "Database " + SCHEMA_NAME + " delete got failed.");
    } finally {
      DataSourceFactory.close(dataSource);
    }
  }

  @Override
  @Test
  public void testLineBreakCharacters() {
    // overrides test in coming releases
  }

  @Override
  @Test
  public void testSecondSync() {
    // overrides test in coming releases
  }

  @Override
  @Test
  public void testCustomDbtTransformations() throws Exception {
    // overrides test in coming releases
  }

  protected DataSource getDataSource(final JsonNode config) {
    final JsonNode jdbcConfig = destination.toJdbcConfig(config);
    return DataSourceFactory.create(jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        TeradataConstants.DRIVER_CLASS, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText(),
        getConnectionProperties(config));
  }

  protected Map<String, String> getConnectionProperties(final JsonNode config) {
    final Map<String, String> customProperties = JdbcUtils.parseJdbcParameters(config,
        JdbcUtils.JDBC_URL_PARAMS_KEY);
    final Map<String, String> defaultProperties = getDefaultConnectionProperties(config);
    assertCustomParametersDontOverwriteDefaultParameters(customProperties, defaultProperties);
    return MoreMaps.merge(customProperties, defaultProperties);
  }

  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    return destination.getDefaultConnectionProperties(config);
  }

  private void assertCustomParametersDontOverwriteDefaultParameters(final Map<String, String> customParameters,
                                                                    final Map<String, String> defaultParameters) {
    for (final String key : defaultParameters.keySet()) {
      if (customParameters.containsKey(key)
          && !Objects.equals(customParameters.get(key), defaultParameters.get(key))) {
        throw new IllegalArgumentException("Cannot overwrite default JDBC parameter " + key);
      }
    }
  }

}
