/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bytehouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.nio.file.Path;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BytehouseDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BytehouseDestinationAcceptanceTest.class);

  private ObjectNode config;
  private JdbcDatabase db;

  @Override
  protected String getImageName() {
    return "airbyte/destination-bytehouse:dev";
  }

  @Override
  protected JsonNode getConfig() {
    // TODO: Generate the configuration JSON file to be used for running the destination during the test
    // configJson can either be static and read from secrets/config.json directly
    // or created in the setup method
    if (config != null)
      return config;

    config = (ObjectNode) Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
    final String jdbcUrl = String.format(DatabaseDriver.BYTEHOUSE.getUrlFormatString(),
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asInt());
    config.put(JdbcUtils.JDBC_URL_KEY, jdbcUrl);

    return config;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    // TODO return an invalid config which, when used to run the connector's check connection operation,
    // should result in a failed connection check
    final ObjectNode config = (ObjectNode) Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
    config.put("password", "wrong password");
    config.put(JdbcUtils.JDBC_URL_PARAMS_KEY, "");
    return config;
  }

  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws Exception {
    // TODO Implement this method to retrieve records which written to the destination by the connector.
    // Records returned from this method will be compared against records provided to the connector
    // to verify they were written correctly
    LOGGER.info("Retriving records, env: {}, stream: {}, namespace: {}", testEnv, streamName, namespace);
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    final String query = String.format("SELECT * FROM %s.%s ORDER BY %s ASC", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    return this.db.queryJsons(query);
  }

  @Override
  protected String getDefaultSchema(JsonNode config) throws Exception {
    String schema = config.get(JdbcUtils.DATABASE_KEY).asText();
    LOGGER.warn("default schema: " + schema);
    System.out.println("default schema: " + schema);
    return schema;
  }

  @Override
  protected boolean supportsNormalization() {
    return false;
  }

  private static JdbcDatabase getDatabase(final JsonNode config) {
    return new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.has(JdbcUtils.PASSWORD_KEY) ? config.get(JdbcUtils.PASSWORD_KEY).asText() : null,
            BytehouseDestination.DRIVER_CLASS,
            config.get(JdbcUtils.JDBC_URL_KEY).asText(),
            getConnectionProperties(config)),
        new BytehouseTestSourceOperations());
  }

  private static Map<String, String> getConnectionProperties(final JsonNode config) {
    final Map<String, String> customProperties = JdbcUtils.parseJdbcParameters(config, JdbcUtils.JDBC_URL_PARAMS_KEY);
    final Map<String, String> defaultProperties = Collections.emptyMap();
    return MoreMaps.merge(customProperties, defaultProperties);
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    // TODO Implement this method to run any setup actions needed before every test case
    this.db = getDatabase(getConfig());
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    // TODO Implement this method to run any cleanup actions needed after every test case
    try {
      String sql = String.format("TRUNCATE TABLE %s._airbyte_raw_exchange_rate", getConfig().get(JdbcUtils.DATABASE_KEY).asText());
      this.db.execute(sql);
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
  }

}
