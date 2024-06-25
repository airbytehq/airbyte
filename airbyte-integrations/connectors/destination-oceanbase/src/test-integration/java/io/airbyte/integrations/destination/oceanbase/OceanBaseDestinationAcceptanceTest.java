/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oceanbase;

import static java.util.concurrent.TimeUnit.SECONDS;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.DestinationConfig;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import java.sql.SQLException;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.output.Slf4jLogConsumer;

// Disabled after DV2 migration. Re-enable with fixtures updated to DV2.
@Disabled
public class OceanBaseDestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  private static final Logger LOG = LoggerFactory.getLogger(OceanBaseDestinationAcceptanceTest.class);

  public final static OceanBaseContainer db = new OceanBaseContainer(OceanBaseContainer.DOCKER_IMAGE_NAME + ":" + OceanBaseContainer.IMAGE_TAG)
      .withSysPassword("123456")
      .withLogConsumer(new Slf4jLogConsumer(LOG));

  private final OceanBaseDestination destination = new OceanBaseDestination();
  private final StandardNameTransformer namingResolver = new OceanBaseNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-oceanbase:dev";
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
    db.start();
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new OceanBaseTestDataComparator();
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
  protected JsonNode getConfig() {
    return getConfigFromTestContainer(db);
  }

  public static ObjectNode getConfigFromTestContainer(final OceanBaseContainer db) {
    return (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(db))
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
        .put(JdbcUtils.SCHEMA_KEY, db.getDatabaseName())
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(db))
        .put(JdbcUtils.SSL_KEY, false)
        .build());
  }

  private JsonNode getConfigForBareMetalConnection() {
    return ((ObjectNode) getConfig())
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final ObjectNode config = (ObjectNode) getConfig();
    config.put(JdbcUtils.PASSWORD_KEY, "wrong password");
    return config;
  }

  @Override
  protected String getDefaultSchema(final JsonNode config) {
    if (config.get(JdbcUtils.DATABASE_KEY) == null) {
      return null;
    }
    return config.get(JdbcUtils.DATABASE_KEY).asText();
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(r -> r.get(JavaBaseConstants.COLUMN_NAME_DATA))
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    final DSLContext dslContext = DSL.using(destination.getDataSource(getConfigForBareMetalConnection()), SQLDialect.DEFAULT);
    return new Database(dslContext).query(
        ctx -> ctx
            .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName,
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
            .stream()
            .map(this::getJsonFromRecord)
            .collect(Collectors.toList()));
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv, final String streamName, final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    final String schema = namingResolver.getIdentifier(namespace);
    return retrieveRecordsFromTable(tableName, schema);
  }

  public void configureTestContainer(final OceanBaseContainer db) {
    setLocalInFileToTrue(db);
  }

  private void setLocalInFileToTrue(final OceanBaseContainer db) {
    final OceanBaseDestination destination = new OceanBaseDestination();
    executeQuery("set global local_infile=true", getConfig(), destination);
  }

  private static void executeQuery(final OceanBaseContainer db, final String query) {
    final DSLContext dslContext = DSLContextFactory.create(
        db.getUsername(),
        db.getPassword(),
        db.getDriverClassName(),
        String.format("jdbc:oceanbase://%s:%s/%s",
            db.getHost(),
            db.getFirstMappedPort(),
            db.getDatabaseName()),
        SQLDialect.MYSQL);
    try {
      new Database(dslContext).query(ctx -> ctx.execute(query));
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  private static void executeQuery(final String query, JsonNode config, OceanBaseDestination oceanBaseDestination) {
    DSLContext dslContext = DSL.using(oceanBaseDestination.getDataSource(config), SQLDialect.DEFAULT);
    try {
      new Database(dslContext).query(ctx -> ctx.execute(query));
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    db.stop();
    db.close();
  }

  @Timeout(value = 300,
           unit = SECONDS)
  @Test
  void testCheckIncorrectPasswordFailure() {
    final JsonNode config = ((ObjectNode) getConfigForBareMetalConnection()).put(JdbcUtils.PASSWORD_KEY, "fake");
    final OceanBaseDestination destination = new OceanBaseDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertStringContains(status.getMessage(), "State code: 28000; Error code: 1045;");
  }

  @Timeout(value = 300,
           unit = SECONDS)
  @Test
  public void testCheckIncorrectUsernameFailure() {
    final JsonNode config = ((ObjectNode) getConfigForBareMetalConnection()).put(JdbcUtils.USERNAME_KEY, "fake");
    final OceanBaseDestination destination = new OceanBaseDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertStringContains(status.getMessage(), "State code: 28000; Error code: 1045;");
  }

  @Timeout(value = 300,
           unit = SECONDS)
  @Test
  public void testCheckIncorrectHostFailure() {
    final JsonNode config = ((ObjectNode) getConfigForBareMetalConnection()).put(JdbcUtils.HOST_KEY, "localhost2");
    final OceanBaseDestination destination = new OceanBaseDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertStringContains(status.getMessage(), "State code: 08S01;");
  }

  @Timeout(value = 300,
           unit = SECONDS)
  @Test
  public void testCheckIncorrectPortFailure() {
    final JsonNode config = ((ObjectNode) getConfigForBareMetalConnection()).put(JdbcUtils.PORT_KEY, "0000");
    final OceanBaseDestination destination = new OceanBaseDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertStringContains(status.getMessage(), "State code: 08S01;");
  }

  @Timeout(value = 300,
           unit = SECONDS)
  @Test
  public void testCheckIncorrectDataBaseFailure() {
    final JsonNode config = ((ObjectNode) getConfigForBareMetalConnection()).put(JdbcUtils.DATABASE_KEY, "wrongdatabase");
    final OceanBaseDestination destination = new OceanBaseDestination();
    DestinationConfig.Companion.initialize(config);
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
  }

  private static void assertStringContains(final String str, final String target) {
    assertTrue(str.contains(target), "Expected message to contain \"" + target + "\" but got " + str);
  }

}
