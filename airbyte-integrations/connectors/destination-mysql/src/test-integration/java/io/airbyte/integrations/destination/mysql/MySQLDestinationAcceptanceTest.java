/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.protocol.models.*;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

import java.io.File;
import java.net.URL;
import java.nio.file.Paths;
import java.sql.SQLException;
import java.time.Instant;
import java.util.List;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class MySQLDestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  protected static final String USERNAME_WITHOUT_PERMISSION = "new_user";
  protected static final String PASSWORD_WITHOUT_PERMISSION = "new_password";

  private TestDestinationEnv testEnv;

  private MySQLContainer<?> db;
  private final ExtendedNameTransformer namingResolver = new MySQLNameTransformer();

  @Override
  protected String getImageName() {
    return "airbyte/destination-mysql:dev";
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
  protected boolean supportsNormalization() {
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
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort())
        .put(JdbcUtils.SSL_KEY, false)
        .build());
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, "wrong password")
        .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort())
        .put(JdbcUtils.SSL_KEY, false)
        .build());
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
    try (final DSLContext dslContext = DSLContextFactory.create(
        db.getUsername(),
        db.getPassword(),
        db.getDriverClassName(),
        String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
            db.getHost(),
            db.getFirstMappedPort(),
            db.getDatabaseName()),
        SQLDialect.MYSQL)) {
      return new Database(dslContext).query(
          ctx -> ctx
              .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName,
                  JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
              .stream()
              .map(this::getJsonFromRecord)
              .collect(Collectors.toList()));
    }
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv, final String streamName, final String namespace)
      throws Exception {
    final String tableName = namingResolver.getIdentifier(streamName);
    final String schema = namingResolver.getIdentifier(namespace);
    return retrieveRecordsFromTable(tableName, schema);
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    this.testEnv = testEnv;
    db = new MySQLContainer<>("mysql:8.0");
    db.start();
    setLocalInFileToTrue();
    revokeAllPermissions();
    grantCorrectPermissions();
  }

  private void setLocalInFileToTrue() {
    executeQuery("set global local_infile=true");
  }

  private void revokeAllPermissions() {
    executeQuery("REVOKE ALL PRIVILEGES, GRANT OPTION FROM " + db.getUsername() + "@'%';");
  }

  private void grantCorrectPermissions() {
    executeQuery("GRANT ALTER, CREATE, INSERT, SELECT, DROP ON *.* TO " + db.getUsername() + "@'%';");
  }

  private void executeQuery(final String query) {
    try (final DSLContext dslContext = DSLContextFactory.create(
            "root",
            "test",
            db.getDriverClassName(),
            String.format(DatabaseDriver.MYSQL.getUrlFormatString()+"?allowLoadLocalInfile=true",
                    db.getHost(),
                    db.getFirstMappedPort(),
                    db.getDatabaseName()),
            SQLDialect.MYSQL)) {
      new Database(dslContext).query(
              ctx -> ctx
                      .execute(query));
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
    executeQuery("GRANT CREATE VIEW ON *.* TO " + db.getUsername() + "@'%';");
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

    private String retrieveTableCharset(final String schemaName, final String tableName) throws SQLException {
        try (final DSLContext dslContext = DSLContextFactory.create(
                db.getUsername(),
                db.getPassword(),
                db.getDriverClassName(),
                String.format(DatabaseDriver.MYSQL.getUrlFormatString(),
                        db.getHost(),
                        db.getFirstMappedPort(),
                        db.getDatabaseName()),
                SQLDialect.MYSQL)) {
            return new Database(dslContext).query(
                    ctx -> ctx
                            .fetch(String.format("SELECT CCSA.character_set_name \n" +
                                    "FROM information_schema.`TABLES` T,information_schema.`COLLATION_CHARACTER_SET_APPLICABILITY` CCSA\n" +
                                    "WHERE CCSA.collation_name = T.table_collation\n" +
                                    "AND T.table_schema = \"%s\" AND T.table_name = \"%s\";", schemaName, tableName))
                            .stream().map(this::getJsonFromRecord).toList().get(0).get("CHARACTER_SET_NAME").asText());
        }
    }


    @Test
    public void testUTF8() throws Exception {
      // create table
      String streamName = "mysql_utf8_test_table";
      String testCreateTableName = namingResolver.getRawTableName(streamName);

      String createSQL = String.format(
              "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
                      + "%s VARCHAR(256) PRIMARY KEY,\n"
                      + "%s JSON,\n"
                      + "%s TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6)\n"
                      + ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4; \n",
              db.getDatabaseName(), testCreateTableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);

      executeQuery(createSQL);

      // check charset
      String utf8mb4Charset = "utf8mb4";
      assertEquals(utf8mb4Charset, retrieveTableCharset(db.getDatabaseName(), testCreateTableName));

      // load data
      String data = "{\"content\":\"你好\uD83E\uDD73\"}"; // 你好🥳
      String resourceFile = "load_data_test.csv";
      URL resource = getClass().getClassLoader().getResource(resourceFile);
      File file = Paths.get(resource.toURI()).toFile();

      String absoluteFile = "'" + file.getAbsolutePath() + "'";
      String loadDataSQL = String.format("LOAD DATA LOCAL INFILE %s INTO TABLE %s.%s CHARACTER SET utf8mb4 FIELDS " +
              "TERMINATED BY ',' ENCLOSED BY '\"' ESCAPED BY '\\\"' LINES TERMINATED BY '\\r\\n'",
              absoluteFile, db.getDatabaseName(), testCreateTableName);
      executeQuery(loadDataSQL);

      List<JsonNode> records = retrieveRecords(this.testEnv,streamName,db.getDatabaseName(),null);
      assertEquals(data, records.get(0).toString());
    }

  protected void assertSameValue(final JsonNode expectedValue, final JsonNode actualValue) {
    if (expectedValue.isBoolean()) {
      // Boolean in MySQL are stored as TINYINT (0 or 1) so we force them to boolean values here
      assertEquals(expectedValue.asBoolean(), actualValue.asBoolean());
    } else {
      assertEquals(expectedValue, actualValue);
    }
  }

  @Test
  void testCheckIncorrectPasswordFailure() {
    final JsonNode config = ((ObjectNode) getConfig()).put(JdbcUtils.PASSWORD_KEY, "fake");
    final MySQLDestination destination = new MySQLDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: 28000; Error code: 1045;"));
  }

  @Test
  public void testCheckIncorrectUsernameFailure() {
    final JsonNode config = ((ObjectNode) getConfig()).put(JdbcUtils.USERNAME_KEY, "fake");
    final MySQLDestination destination = new MySQLDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: 28000; Error code: 1045;"));
  }

  @Test
  public void testCheckIncorrectHostFailure() {
    final JsonNode config = ((ObjectNode) getConfig()).put(JdbcUtils.HOST_KEY, "localhost2");
    final MySQLDestination destination = new MySQLDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: 08S01;"));
  }

  @Test
  public void testCheckIncorrectPortFailure() {
    final JsonNode config = ((ObjectNode) getConfig()).put(JdbcUtils.PORT_KEY, "0000");
    final MySQLDestination destination = new MySQLDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: 08S01;"));
  }

  @Test
  public void testCheckIncorrectDataBaseFailure() {
    final JsonNode config = ((ObjectNode) getConfig()).put(JdbcUtils.DATABASE_KEY, "wrongdatabase");
    final MySQLDestination destination = new MySQLDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: 42000; Error code: 1049;"));
  }

  @Test
  public void testUserHasNoPermissionToDataBase() {
    executeQuery("create user '" + USERNAME_WITHOUT_PERMISSION + "'@'%' IDENTIFIED BY '" + PASSWORD_WITHOUT_PERMISSION + "';\n");
    final JsonNode config = ((ObjectNode) getConfig()).put(JdbcUtils.USERNAME_KEY, USERNAME_WITHOUT_PERMISSION);
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, PASSWORD_WITHOUT_PERMISSION);
    final MySQLDestination destination = new MySQLDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: 42000; Error code: 1044;"));
  }

}
