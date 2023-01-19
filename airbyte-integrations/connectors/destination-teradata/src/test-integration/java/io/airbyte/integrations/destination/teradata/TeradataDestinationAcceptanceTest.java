/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import javax.sql.DataSource;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TeradataDestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(TeradataDestinationAcceptanceTest.class);
  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  private JsonNode configJson;
  private JdbcDatabase database;
  private DataSource dataSource;
  private TeradataDestination destination = new TeradataDestination();
  private final JdbcSourceOperations sourceOperations = JdbcUtils.getDefaultSourceOperations();

  @Override
  protected String getImageName() {
    return "airbyte/destination-teradata:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return configJson;
  }

  public JsonNode getStaticConfig() throws Exception {
    final JsonNode config = Jsons.deserialize(Files.readString(Paths.get("secrets/config.json")));
    return config;
  }

  @Override
  protected JsonNode getFailCheckConfig() throws Exception {
    final JsonNode credentialsJsonString = Jsons
        .deserialize(Files.readString(Paths.get("secrets/failureconfig.json")));
    final AirbyteConnectionStatus check = new TeradataDestination().check(credentialsJsonString);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, check.getStatus());
    return credentialsJsonString;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    final List<JsonNode> records = retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace);
    return records;

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
  protected void setup(TestDestinationEnv testEnv) {
    final String schemaName = Strings.addRandomSuffix("integration_test_teradata", "_", 5);
    final String createSchemaQuery = String
        .format(String.format("CREATE DATABASE \"%s\" AS PERM = 1e9 SKEW = 10 PERCENT", schemaName));
    try {
      this.configJson = Jsons.clone(getStaticConfig());
      ((ObjectNode) configJson).put("schema", schemaName);

      dataSource = getDataSource(configJson);
      database = getDatabase(dataSource);
      database.execute(createSchemaQuery);
    } catch (Exception e) {
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e, "Database " + schemaName + " creation got failed.");
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
  protected void tearDown(TestDestinationEnv testEnv) {}

  protected DataSource getDataSource(final JsonNode config) {
    final JsonNode jdbcConfig = destination.toJdbcConfig(config);
    return DataSourceFactory.create(jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        TeradataDestination.DRIVER_CLASS, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText(),
        getConnectionProperties(config));
  }

  protected JdbcDatabase getDatabase(final DataSource dataSource) {
    return new DefaultJdbcDatabase(dataSource);
  }

  protected Map<String, String> getConnectionProperties(final JsonNode config) {
    final Map<String, String> customProperties = JdbcUtils.parseJdbcParameters(config,
        JdbcUtils.JDBC_URL_PARAMS_KEY);
    final Map<String, String> defaultProperties = getDefaultConnectionProperties(config);
    assertCustomParametersDontOverwriteDefaultParameters(customProperties, defaultProperties);
    return MoreMaps.merge(customProperties, defaultProperties);
  }

  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    return Collections.emptyMap();
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
