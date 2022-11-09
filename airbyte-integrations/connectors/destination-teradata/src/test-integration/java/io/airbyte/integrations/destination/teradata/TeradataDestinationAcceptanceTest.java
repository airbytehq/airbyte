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
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import javax.sql.DataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class TeradataDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(TeradataDestinationAcceptanceTest.class);

  private JsonNode configJson;
  private JdbcDatabase database;
  private DataSource dataSource;
  private TeradataDestination destination = new TeradataDestination();

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
    /*
     * return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace).stream()
     * .map(r -> r.get(JavaBaseConstants.COLUMN_NAME_DATA)).collect(Collectors.toList());
     */
    return null;
  }

  /*
   * private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName)
   * throws SQLException {
   *
   * final List<JsonNode> actual = database.bufferedResultSetQuery( connection ->
   * connection.createStatement().executeQuery("SELECT * FROM id_and_name;"),
   * sourceOperations::rowToJson); return actual; }
   */

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    final String schemaName = Strings.addRandomSuffix("integration_test", "_", 5);
    LOGGER.info("Satish TeradataDestinationAcceptanceTest setup : schemaName - " + schemaName);
    final String createSchemaQuery = String
        .format(String.format("CREATE DATABASE %s AS PERM = 1e9 SKEW = 10 PERCENT;", schemaName));
    LOGGER.info("Satish TeradataDestinationAcceptanceTest setup : createSchemaQuery - " + createSchemaQuery);

    try {
      this.configJson = Jsons.clone(getStaticConfig());
      LOGGER.info("Satish TeradataDestinationAcceptanceTest setup : configJson - " + configJson);
      ((ObjectNode) configJson).put("schema", schemaName);

      dataSource = getDataSource(configJson);
      LOGGER.info("Satish TeradataDestinationAcceptanceTest : setup dataSource - " + dataSource);
      database = getDatabase(dataSource);
      LOGGER.info("Satish TeradataDestinationAcceptanceTest : setup database - " + database);
      database.execute(createSchemaQuery);
      LOGGER.info("Satish TeradataDestinationAcceptanceTest setup : execute success ");
    } catch (Exception e) {
      LOGGER.info("Satish TeradataDestinationAcceptanceTest setup : failed - " + e.getMessage());
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e, "setup failed");
    }
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {}

  protected DataSource getDataSource(final JsonNode config) {
    final JsonNode jdbcConfig = destination.toJdbcConfig(config);
    return DataSourceFactory.create(jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        TeradataDestination.DRIVER_CLASS, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText(), getConnectionProperties(config));
  }

  protected JdbcDatabase getDatabase(final DataSource dataSource) {
    return new DefaultJdbcDatabase(dataSource);
  }

  protected Map<String, String> getConnectionProperties(final JsonNode config) {
    final Map<String, String> customProperties = JdbcUtils.parseJdbcParameters(config, JdbcUtils.JDBC_URL_PARAMS_KEY);
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
      if (customParameters.containsKey(key) && !Objects.equals(customParameters.get(key), defaultParameters.get(key))) {
        throw new IllegalArgumentException("Cannot overwrite default JDBC parameter " + key);
      }
    }
  }

}
