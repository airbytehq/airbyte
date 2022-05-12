/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import org.junit.jupiter.api.Disabled;
import org.testcontainers.containers.ClickHouseContainer;

public class ClickhouseDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final String DB_NAME = "default";

  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  private ClickHouseContainer db;

  @Override
  protected String getImageName() {
    return "airbyte/destination-clickhouse:dev";
  }

  @Override
  protected boolean supportsNormalization() {
    return false;
  }

  @Override
  protected boolean supportsDBT() {
    return false;
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new ClickhouseTestDataComparator();
  }

  @Override
  protected boolean supportBasicDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportArrayDataTypeTest() {
    return true;
  }

  @Override
  protected boolean supportObjectDataTypeTest() {
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
    // Note: ClickHouse official JDBC driver uses HTTP protocol, its default port is 8123
    // dbt clickhouse adapter uses native protocol, its default port is 9000
    // Since we disabled normalization and dbt test, we only use the JDBC port here.
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", db.getFirstMappedPort())
        .put("database", DB_NAME)
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("schema", DB_NAME)
        .put("ssl", false)
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode clone = Jsons.clone(getConfig());
    ((ObjectNode) clone).put("password", "wrong password");
    return clone;
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv,
                                                     final String streamName,
                                                     final String namespace)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getIdentifier(streamName), namespace);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(r.get(JavaBaseConstants.COLUMN_NAME_DATA).asText()))
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    final JdbcDatabase jdbcDB = getDatabase(getConfig());
    final String query = String.format("SELECT * FROM %s.%s ORDER BY %s ASC", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    return jdbcDB.queryJsons(query);
  }

  private static JdbcDatabase getDatabase(final JsonNode config) {
    return new DefaultJdbcDatabase(
        DataSourceFactory.create(
            config.get("username").asText(),
            config.has("password") ? config.get("password").asText() : null,
            ClickhouseDestination.DRIVER_CLASS,
            String.format(DatabaseDriver.CLICKHOUSE.getUrlFormatString(),
                config.get("host").asText(),
                config.get("port").asInt(),
                config.get("database").asText())
        )
    );
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    db = new ClickHouseContainer("yandex/clickhouse-server");
    db.start();
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    db.stop();
    db.close();
  }

  /**
   * The SQL script generated by old version of dbt in 'test' step isn't compatible with ClickHouse,
   * so we skip this test for now.
   *
   * Ref: https://github.com/dbt-labs/dbt-core/issues/3905
   *
   * @throws Exception
   */
  @Disabled
  public void testCustomDbtTransformations() throws Exception {
    super.testCustomDbtTransformations();
  }

  @Disabled
  public void testCustomDbtTransformationsFailure() throws Exception {}

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

  @Disabled
  public void specNormalizationValueShouldBeCorrect() throws Exception {
    super.specNormalizationValueShouldBeCorrect();
  }
}
