/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle;

import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import java.sql.SQLException;
import java.util.List;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.junit.Test;

public class UnencryptedOracleDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private final ExtendedNameTransformer namingResolver = new OracleNameTransformer();
  private static OracleContainer db;
  private static JsonNode config;
  private final String schemaName = "TEST_ORCL";

  @Override
  protected String getImageName() {
    return "airbyte/destination-oracle:dev";
  }

  private JsonNode getConfig(final OracleContainer db) {

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", db.getFirstMappedPort())
        .put("sid", db.getSid())
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .put("schemas", List.of("JDBC_SPACE"))
        .put("encryption", Jsons.jsonNode(ImmutableMap.builder()
            .put("encryption_method", "unencrypted")
            .build()))
        .build());
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.clone(config);
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> Jsons.deserialize(
            r.get(OracleDestination.COLUMN_NAME_DATA.replace("\"", "")).asText()))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected boolean supportsDBT() {
    return false;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new OracleTestDataComparator();
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
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv env,
                                                     final String streamName,
                                                     final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    return retrieveRecordsFromTable(tableName, namespace);
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode invalidConfig = getConfig();
    ((ObjectNode) invalidConfig).put("password", "wrong password");
    return invalidConfig;
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName)
      throws SQLException {
    try (final DSLContext dslContext = getDSLContext(config)) {
      final List<org.jooq.Record> result = getDatabase(dslContext)
          .query(ctx -> ctx.fetch(
                  String.format("SELECT * FROM %s.%s ORDER BY %s ASC", schemaName, tableName,
                      OracleDestination.COLUMN_NAME_EMITTED_AT))
              .stream()
              .collect(Collectors.toList()));
      return result
          .stream()
          .map(r -> r.formatJSON(JdbcUtils.getDefaultJSONFormat()))
          .map(Jsons::deserialize)
          .collect(Collectors.toList());
    }
  }

  private static DSLContext getDSLContext(final JsonNode config) {
    return DSLContextFactory.create(
        config.get("username").asText(), config.get("password").asText(), DatabaseDriver.ORACLE.getDriverClassName(),
        String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
            config.get("host").asText(),
            config.get("port").asInt(),
            config.get("sid").asText()), null);
  }

  private static Database getDatabase(final DSLContext dslContext) {
    return new Database(dslContext);
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) throws Exception {
    final String dbName = Strings.addRandomSuffix("db", "_", 10);
    db = new OracleContainer()
        .withUsername("test")
        .withPassword("oracle")
        .usingSid();
    db.start();

    config = getConfig(db);

    try (final DSLContext dslContext = getDSLContext(config)) {
      final Database database = getDatabase(dslContext);
      database.query(
          ctx -> ctx.fetch(String.format("CREATE USER %s IDENTIFIED BY %s", schemaName, schemaName)));
      database.query(ctx -> ctx.fetch(String.format("GRANT ALL PRIVILEGES TO %s", schemaName)));

      ((ObjectNode) config).put("schema", dbName);
    }
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    db.stop();
    db.close();
  }

  @Test
  public void testNoneEncryption() throws SQLException {
    final JsonNode config = getConfig();

    final DataSource dataSource =
        DataSourceFactory.create(config.get("username").asText(), config.get("password").asText(), DatabaseDriver.ORACLE.getDriverClassName(),
            String.format(DatabaseDriver.ORACLE.getUrlFormatString(),
                config.get("host").asText(),
                config.get("port").asInt(),
                config.get("sid").asText()));
    final JdbcDatabase database = new DefaultJdbcDatabase(dataSource);

    final String networkServiceBanner =
        "select network_service_banner from v$session_connect_info where sid in (select distinct sid from v$mystat)";
    final List<JsonNode> collect = database.queryJsons(networkServiceBanner);

    assertTrue(collect.get(1).get("NETWORK_SERVICE_BANNER").asText()
        .contains("Oracle Advanced Security: encryption"));
  }

}
