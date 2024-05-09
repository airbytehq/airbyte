/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import static java.util.concurrent.TimeUnit.SECONDS;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.DSLContextFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataTypeTestArgumentProvider;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.cdk.integrations.util.HostPortResolver;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.sql.SQLException;
import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.testcontainers.containers.MySQLContainer;

@Disabled
public class MySQLDestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  protected static final String USERNAME_WITHOUT_PERMISSION = "new_user";
  protected static final String PASSWORD_WITHOUT_PERMISSION = "new_password";

  protected MySQLContainer<?> db;
  private final StandardNameTransformer namingResolver = new MySQLNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-mysql:dev";
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new MySqlTestDataComparator();
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

  public static ObjectNode getConfigFromTestContainer(final MySQLContainer<?> db) {
    return (ObjectNode) Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(db))
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(db))
        .put(JdbcUtils.SSL_KEY, false)
        .build());
  }

  /**
   * {@link #getConfig()} returns a config with host/port set to the in-docker values. This works for
   * running the destination-mysql container, but we have some tests which run the destination code
   * directly from the JUnit process. These tests need to connect using the "normal" host/port.
   */
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
    final DSLContext dslContext = DSLContextFactory.create(
        db.getUsername(),
        db.getPassword(),
        db.getDriverClassName(),
        String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
            db.getHost(),
            db.getFirstMappedPort(),
            db.getDatabaseName()),
        SQLDialect.MYSQL);
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

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
    db = new MySQLContainer<>("mysql:8.0");
    db.start();
    configureTestContainer(db);
  }

  public static void configureTestContainer(final MySQLContainer<?> db) {
    setLocalInFileToTrue(db);
    revokeAllPermissions(db);
    grantCorrectPermissions(db);
  }

  private static void setLocalInFileToTrue(final MySQLContainer<?> db) {
    executeQuery(db, "set global local_infile=true");
  }

  private static void revokeAllPermissions(final MySQLContainer<?> db) {
    executeQuery(db, "REVOKE ALL PRIVILEGES, GRANT OPTION FROM " + db.getUsername() + "@'%';");
  }

  private static void grantCorrectPermissions(final MySQLContainer<?> db) {
    executeQuery(db, "GRANT ALTER, CREATE, INSERT, INDEX, UPDATE, DELETE, SELECT, DROP ON *.* TO " + db.getUsername() + "@'%';");
  }

  private static void executeQuery(final MySQLContainer<?> db, final String query) {
    final DSLContext dslContext = DSLContextFactory.create(
        "root",
        "test",
        db.getDriverClassName(),
        String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
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

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    db.stop();
    db.close();
  }

  @Override
  @Test
  public void testCustomDbtTransformations() throws Exception {
    // We need to create view for testing custom dbt transformations
    executeQuery(db, "GRANT CREATE VIEW ON *.* TO " + db.getUsername() + "@'%';");
    super.testCustomDbtTransformations();
  }

  @Test
  public void testJsonSync() throws Exception {
    final String catalogAsText = "{\n"
        + "  \"streams\": [\n"
        + "    {\n"
        + "      \"name\": \"exchange_rate\",\n"
        + "      \"json_schema\": {\n"
        + "        \"properties\": {\n"
        + "          \"id\": {\n"
        + "            \"type\": \"integer\"\n"
        + "          },\n"
        + "          \"data\": {\n"
        + "            \"type\": \"string\"\n"
        + "          }"
        + "        }\n"
        + "      }\n"
        + "    }\n"
        + "  ]\n"
        + "}\n";

    final AirbyteCatalog catalog = Jsons.deserialize(catalogAsText, AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = Lists.newArrayList(
        new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(catalog.getStreams().get(0).getName())
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.builder()
                    .put("id", 1)
                    .put("data", "{\"name\":\"Conferência Faturamento - Custo - Taxas - Margem - Resumo ano inicial até -2\",\"description\":null}")
                    .build()))),
        new AirbyteMessage()
            .withType(Type.STATE)
            .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of("checkpoint", 2)))));

    final JsonNode config = getConfig();
    final String defaultSchema = getDefaultSchema(config);
    runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false);
    retrieveRawRecordsAndAssertSameMessages(catalog, messages, defaultSchema);
  }

  @Override
  @Test
  public void testLineBreakCharacters() {
    // overrides test with a no-op until we handle full UTF-8 in the destination
  }

  protected void assertSameValue(final JsonNode expectedValue, final JsonNode actualValue) {
    if (expectedValue.isBoolean()) {
      // Boolean in MySQL are stored as TINYINT (0 or 1) so we force them to boolean values here
      assertEquals(expectedValue.asBoolean(), actualValue.asBoolean());
    } else {
      assertEquals(expectedValue, actualValue);
    }
  }

  // Something is very weird in our connection check code. A wrong password takes >1 minute to return.
  // TODO investigate why invalid creds take so long to detect
  @Timeout(value = 300,
           unit = SECONDS)
  @Test
  void testCheckIncorrectPasswordFailure() {
    final JsonNode config = ((ObjectNode) getConfigForBareMetalConnection()).put(JdbcUtils.PASSWORD_KEY, "fake");
    final MySQLDestination destination = new MySQLDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertStringContains(status.getMessage(), "State code: 28000; Error code: 1045;");
  }

  @Timeout(value = 300,
           unit = SECONDS)
  @Test
  public void testCheckIncorrectUsernameFailure() {
    final JsonNode config = ((ObjectNode) getConfigForBareMetalConnection()).put(JdbcUtils.USERNAME_KEY, "fake");
    final MySQLDestination destination = new MySQLDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertStringContains(status.getMessage(), "State code: 28000; Error code: 1045;");
  }

  @Timeout(value = 300,
           unit = SECONDS)
  @Test
  public void testCheckIncorrectHostFailure() {
    final JsonNode config = ((ObjectNode) getConfigForBareMetalConnection()).put(JdbcUtils.HOST_KEY, "localhost2");
    final MySQLDestination destination = new MySQLDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertStringContains(status.getMessage(), "State code: 08S01;");
  }

  @Timeout(value = 300,
           unit = SECONDS)
  @Test
  public void testCheckIncorrectPortFailure() {
    final JsonNode config = ((ObjectNode) getConfigForBareMetalConnection()).put(JdbcUtils.PORT_KEY, "0000");
    final MySQLDestination destination = new MySQLDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertStringContains(status.getMessage(), "State code: 08S01;");
  }

  @Timeout(value = 300,
           unit = SECONDS)
  @Test
  public void testCheckIncorrectDataBaseFailure() {
    final JsonNode config = ((ObjectNode) getConfigForBareMetalConnection()).put(JdbcUtils.DATABASE_KEY, "wrongdatabase");
    final MySQLDestination destination = new MySQLDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertStringContains(status.getMessage(), "State code: 42000; Error code: 1049;");
  }

  @Timeout(value = 300,
           unit = SECONDS)
  @Test
  public void testUserHasNoPermissionToDataBase() {
    executeQuery(db, "create user '" + USERNAME_WITHOUT_PERMISSION + "'@'%' IDENTIFIED BY '" + PASSWORD_WITHOUT_PERMISSION + "';\n");
    final JsonNode config = ((ObjectNode) getConfigForBareMetalConnection()).put(JdbcUtils.USERNAME_KEY, USERNAME_WITHOUT_PERMISSION);
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, PASSWORD_WITHOUT_PERMISSION);
    final MySQLDestination destination = new MySQLDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertStringContains(status.getMessage(), "State code: 42000; Error code: 1044;");
  }

  private static void assertStringContains(final String str, final String target) {
    assertTrue(str.contains(target), "Expected message to contain \"" + target + "\" but got " + str);
  }

  /**
   * Legacy mysql normalization is broken, and uses the FLOAT type for numbers. This rounds off e.g.
   * 12345.678 to 12345.7. We can fix this in DV2, but will not fix legacy normalization. As such,
   * disabling the test case.
   */
  @Override
  @Disabled("MySQL normalization uses the wrong datatype for numbers. This will not be fixed, because we intend to replace normalization with DV2.")
  public void testDataTypeTestWithNormalization(final String messagesFilename,
                                                final String catalogFilename,
                                                final DataTypeTestArgumentProvider.TestCompatibility testCompatibility)
      throws Exception {
    super.testDataTypeTestWithNormalization(messagesFilename, catalogFilename, testCompatibility);
  }

}
