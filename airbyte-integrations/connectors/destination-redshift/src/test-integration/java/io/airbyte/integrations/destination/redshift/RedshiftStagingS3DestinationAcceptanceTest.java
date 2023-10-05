/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.factory.ConnectionFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer;
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.TestingNamespaces;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.destination.redshift.operations.RedshiftSqlOperations;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.HashSet;
import java.util.List;
import java.util.stream.Collectors;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Integration test testing {@link RedshiftStagingS3Destination}. The default Redshift integration
 * test credentials contain S3 credentials - this automatically causes COPY to be selected.
 */
public abstract class RedshiftStagingS3DestinationAcceptanceTest extends JdbcDestinationAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftStagingS3DestinationAcceptanceTest.class);

  // config from which to create / delete schemas.
  private JsonNode baseConfig;
  // config which refers to the schema that the test is being run in.
  protected JsonNode config;
  private final RedshiftSQLNameTransformer namingResolver = new RedshiftSQLNameTransformer();
  private final String USER_WITHOUT_CREDS = Strings.addRandomSuffix("test_user", "_", 5);

  private Database database;
  private Connection connection;
  protected TestDestinationEnv testDestinationEnv;

  private final ObjectMapper mapper = new ObjectMapper();

  @Override
  protected String getImageName() {
    return "airbyte/destination-redshift:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  public JsonNode getStaticConfig() throws IOException {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config_staging.json")));
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode invalidConfig = Jsons.clone(config);
    ((ObjectNode) invalidConfig).put("password", "wrong password");
    return invalidConfig;
  }

  @Test
  void testCheckIncorrectPasswordFailure() throws Exception {
    final JsonNode invalidConfig = Jsons.clone(config);
    ((ObjectNode) invalidConfig).put("password", "fake");
    final RedshiftDestination destination = new RedshiftDestination();
    final AirbyteConnectionStatus status = destination.check(invalidConfig);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: 28000; Error code: 500310;"));
  }

  @Test
  public void testCheckIncorrectUsernameFailure() throws Exception {
    final JsonNode invalidConfig = Jsons.clone(config);
    ((ObjectNode) invalidConfig).put("username", "");
    final RedshiftDestination destination = new RedshiftDestination();
    final AirbyteConnectionStatus status = destination.check(invalidConfig);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: 28000; Error code: 500310;"));
  }

  @Test
  public void testCheckIncorrectHostFailure() throws Exception {
    final JsonNode invalidConfig = Jsons.clone(config);
    ((ObjectNode) invalidConfig).put("host", "localhost2");
    final RedshiftDestination destination = new RedshiftDestination();
    final AirbyteConnectionStatus status = destination.check(invalidConfig);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: HY000; Error code: 500150;"));
  }

  @Test
  public void testCheckIncorrectDataBaseFailure() throws Exception {
    final JsonNode invalidConfig = Jsons.clone(config);
    ((ObjectNode) invalidConfig).put("database", "wrongdatabase");
    final RedshiftDestination destination = new RedshiftDestination();
    final AirbyteConnectionStatus status = destination.check(invalidConfig);
    assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
    assertTrue(status.getMessage().contains("State code: 3D000; Error code: 500310;"));
  }

  /*
   * FileBuffer Default Tests
   */
  @Test
  public void testGetFileBufferDefault() {
    final RedshiftStagingS3Destination destination = new RedshiftStagingS3Destination();
    assertEquals(destination.getNumberOfFileBuffers(config), FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER);
  }

  @Test
  public void testGetFileBufferMaxLimited() {
    final JsonNode defaultConfig = Jsons.clone(config);
    ((ObjectNode) defaultConfig).put(FileBuffer.FILE_BUFFER_COUNT_KEY, 100);
    final RedshiftStagingS3Destination destination = new RedshiftStagingS3Destination();
    assertEquals(destination.getNumberOfFileBuffers(defaultConfig), FileBuffer.MAX_CONCURRENT_STREAM_IN_BUFFER);
  }

  @Test
  public void testGetMinimumFileBufferCount() {
    final JsonNode defaultConfig = Jsons.clone(config);
    ((ObjectNode) defaultConfig).put(FileBuffer.FILE_BUFFER_COUNT_KEY, 1);
    final RedshiftStagingS3Destination destination = new RedshiftStagingS3Destination();
    // User cannot set number of file counts below the default file buffer count, which is existing
    // behavior
    assertEquals(destination.getNumberOfFileBuffers(defaultConfig), FileBuffer.DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER);
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new RedshiftTestDataComparator();
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
  protected boolean supportIncrementalSchemaChanges() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    return retrieveRecordsFromTable(namingResolver.getRawTableName(streamName), namespace)
        .stream()
        .map(j -> j.get(JavaBaseConstants.COLUMN_NAME_DATA))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv, final String streamName, final String namespace)
      throws Exception {
    String tableName = namingResolver.getIdentifier(streamName);
    if (!tableName.startsWith("\"")) {
      // Currently, Normalization always quote tables identifiers
      tableName = "\"" + tableName + "\"";
    }
    return retrieveRecordsFromTable(tableName, namespace);
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schemaName) throws SQLException {
    return getDatabase().query(
        ctx -> ctx
            .fetch(String.format("SELECT * FROM %s.%s ORDER BY %s ASC;", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_EMITTED_AT))
            .stream()
            .map(this::getJsonFromRecord)
            .collect(Collectors.toList()));
  }

  // for each test we create a new schema in the database. run the test in there and then remove it.
  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) throws Exception {
    final String schemaName = TestingNamespaces.generate();
    final String createSchemaQuery = String.format("CREATE SCHEMA %s", schemaName);
    baseConfig = getStaticConfig();
    database = createDatabase();
    removeOldNamespaces();
    getDatabase().query(ctx -> ctx.execute(createSchemaQuery));
    final String createUser = String.format("create user %s with password '%s' SESSION TIMEOUT 60;",
        USER_WITHOUT_CREDS, baseConfig.get("password").asText());
    getDatabase().query(ctx -> ctx.execute(createUser));
    final JsonNode configForSchema = Jsons.clone(baseConfig);
    ((ObjectNode) configForSchema).put("schema", schemaName);
    TEST_SCHEMAS.add(schemaName);
    config = configForSchema;
    testDestinationEnv = testEnv;
  }

  private void removeOldNamespaces() {
    final List<String> schemas;
    try {
      schemas = getDatabase().query(ctx -> ctx.fetch("SELECT schema_name FROM information_schema.schemata;"))
          .stream()
          .map(record -> record.get("schema_name").toString())
          .toList();
    } catch (final SQLException e) {
      // if we can't fetch the schemas, just return.
      return;
    }

    int schemasDeletedCount = 0;
    for (final String schema : schemas) {
      if (TestingNamespaces.isOlderThan2Days(schema)) {
        try {
          getDatabase().query(ctx -> ctx.execute(String.format("DROP SCHEMA IF EXISTS %s CASCADE", schema)));
          schemasDeletedCount++;
        } catch (final SQLException e) {
          LOGGER.error("Failed to delete old dataset: {}", schema, e);
        }
      }
    }
    LOGGER.info("Deleted {} old schemas.", schemasDeletedCount);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    System.out.println("TEARING_DOWN_SCHEMAS: " + TEST_SCHEMAS);
    getDatabase().query(ctx -> ctx.execute(String.format("DROP SCHEMA IF EXISTS %s CASCADE", config.get("schema").asText())));
    for (final String schema : TEST_SCHEMAS) {
      getDatabase().query(ctx -> ctx.execute(String.format("DROP SCHEMA IF EXISTS %s CASCADE", schema)));
    }
    getDatabase().query(ctx -> ctx.execute(String.format("drop user if exists %s;", USER_WITHOUT_CREDS)));
    RedshiftConnectionHandler.close(connection);
  }

  protected Database createDatabase() {
    connection = ConnectionFactory.create(baseConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        baseConfig.get(JdbcUtils.PASSWORD_KEY).asText(),
        RedshiftInsertDestination.SSL_JDBC_PARAMETERS,
        String.format(DatabaseDriver.REDSHIFT.getUrlFormatString(),
            baseConfig.get(JdbcUtils.HOST_KEY).asText(),
            baseConfig.get(JdbcUtils.PORT_KEY).asInt(),
            baseConfig.get(JdbcUtils.DATABASE_KEY).asText()));

    return new Database(DSL.using(connection));
  }

  protected Database getDatabase() {
    return database;
  }

  public RedshiftSQLNameTransformer getNamingResolver() {
    return namingResolver;
  }

  @Override
  protected int getMaxRecordValueLimit() {
    return RedshiftSqlOperations.REDSHIFT_VARCHAR_MAX_BYTE_SIZE;
  }

  @Override
  protected int getGenerateBigStringAddExtraCharacters() {
    return 1;
  }

}
