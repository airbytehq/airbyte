/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Disabled;
import org.testcontainers.containers.ClickHouseContainer;

public class ClickhouseDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final String DB_NAME = "default";

  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  private ClickHouseContainer db;

  private boolean useNativePort = false;

  @Override
  protected String getImageName() {
    return "airbyte/destination-clickhouse:dev";
  }

  @Override
  protected boolean supportsNormalization() {
    return true;
  }

  @Override
  protected boolean supportsDBT() {
    return true;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    if (config.get("database") == null) {
      return null;
    }
    return config.get("database").asText();
  }

  @Override
  protected JsonNode getConfig() {
    // ClickHouse official JDBC driver use HTTP protocal, its default port is 8123
    // dbt clickhouse adapter use native protocal, its default port is 9000
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", useNativePort ? db.getMappedPort(ClickHouseContainer.NATIVE_PORT) : db.getFirstMappedPort())
        .put("database", DB_NAME)
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("schema", DB_NAME)
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", db.getFirstMappedPort())
        .put("database", DB_NAME)
        .put("username", db.getUsername())
        .put("password", "wrong password")
        .put("schema", DB_NAME)
        .build());
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv,
                                                     final String streamName,
                                                     final String namespace)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getIdentifier(streamName), namespace);
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    boolean oldUseNativePort = useNativePort;
    useNativePort = false;
    final JdbcDatabase jdbcDB = getDatabase(getConfig());
    useNativePort = oldUseNativePort;
    return jdbcDB.query(String.format("SELECT * FROM %s.%s ORDER BY %s ASC", schemaName, tableName,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
        .collect(Collectors.toList());
  }

  @Override
  protected List<String> resolveIdentifier(final String identifier) {
    final List<String> result = new ArrayList<>();
    final String resolved = namingResolver.getIdentifier(identifier);
    result.add(identifier);
    result.add(resolved);
    if (!resolved.startsWith("\"")) {
      result.add(resolved.toLowerCase());
      result.add(resolved.toUpperCase());
    }
    return result;
  }

  private static JdbcDatabase getDatabase(final JsonNode config) {
    return Databases.createJdbcDatabase(
        config.get("username").asText(),
        config.has("password") ? config.get("password").asText() : null,
        String.format("jdbc:clickhouse://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        ClickhouseDestination.DRIVER_CLASS);
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    db = new ClickHouseContainer("yandex/clickhouse-server");
    db.start();
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    db.stop();
    db.close();
  }

  /**
   * The SQL script generated by dbt in 'test' step isn't compatible with ClickHouse, so we skip this
   * test for now
   *
   * @throws Exception
   */
  @Disabled
  public void testCustomDbtTransformations() throws Exception {
    useNativePort = true;
    super.testCustomDbtTransformations();
  }

  /**
   * The normalization container needs native port, while destination container needs HTTP port, we
   * can't inject the port switch statement into DestinationAcceptanceTest.runSync() method for this
   * test, so we skip it.
   *
   * @throws Exception
   */
  @Disabled
  public void testIncrementalDedupeSync() throws Exception {
    super.testIncrementalDedupeSync();
  }

  /**
   * The normalization container needs native port, while destination container needs HTTP port, we
   * can't inject the port switch statement into DestinationAcceptanceTest.runSync() method for this
   * test, so we skip it.
   *
   * @throws Exception
   */
  @Disabled
  public void testSyncWithNormalization(final String messagesFilename, final String catalogFilename) throws Exception {
    super.testSyncWithNormalization(messagesFilename, catalogFilename);
  }

}
