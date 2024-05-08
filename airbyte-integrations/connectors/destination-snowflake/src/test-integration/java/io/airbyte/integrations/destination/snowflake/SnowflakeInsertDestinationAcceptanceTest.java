/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static org.assertj.core.api.AssertionsForClassTypes.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.DestinationConfig;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataArgumentsProvider;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.configoss.StandardCheckConnectionOutput;
import io.airbyte.configoss.StandardCheckConnectionOutput.Status;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.snowflake.typing_deduping.SnowflakeSqlGenerator;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.nio.file.Path;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.TimeZone;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;

@Disabled
public class SnowflakeInsertDestinationAcceptanceTest extends DestinationAcceptanceTest {

  private static final NamingConventionTransformer NAME_TRANSFORMER = new SnowflakeSQLNameTransformer();
  protected static final String NO_ACTIVE_WAREHOUSE_ERR_MSG =
      "No active warehouse selected in the current session.  Select an active warehouse with the 'use warehouse' command.";

  protected static final String NO_USER_PRIVILEGES_ERR_MSG =
      "Encountered Error with Snowflake Configuration: Current role does not have permissions on the target schema please verify your privileges";

  protected static final String IP_NOT_IN_WHITE_LIST_ERR_MSG = "is not allowed to access Snowflake. Contact your local security administrator";

  // this config is based on the static config, and it contains a random
  // schema name that is different for each test run
  private JsonNode config;
  private JdbcDatabase database;
  private DataSource dataSource;

  @BeforeEach
  public void setup() {
    DestinationConfig.initialize(getConfig());
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-snowflake:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return config;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new SnowflakeTestDataComparator();
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

  protected boolean supportsInDestinationNormalization() {
    return true;
  }

  public JsonNode getStaticConfig() {
    final JsonNode insertConfig = Jsons.deserialize(IOs.readFile(Path.of("secrets/insert_config.json")));
    return insertConfig;
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode invalidConfig = Jsons.clone(config);
    ((ObjectNode) invalidConfig.get("credentials")).put("password", "wrong password");
    return invalidConfig;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv env,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    final StreamId streamId = new SnowflakeSqlGenerator(0).buildStreamId(namespace, streamName, JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE);
    return retrieveRecordsFromTable(streamId.getRawName(), streamId.getRawNamespace())
        .stream()
        .map(r -> r.get(JavaBaseConstants.COLUMN_NAME_DATA))
        .collect(Collectors.toList());
  }

  @Override
  protected boolean implementsNamespaces() {
    return true;
  }

  @Override
  protected boolean supportNamespaceTest() {
    return true;
  }

  @Override
  protected Optional<NamingConventionTransformer> getNameTransformer() {
    return Optional.of(NAME_TRANSFORMER);
  }

  @Override
  protected List<JsonNode> retrieveNormalizedRecords(final TestDestinationEnv testEnv, final String streamName, final String namespace)
      throws Exception {
    final String tableName = NAME_TRANSFORMER.getIdentifier(streamName);
    final String schema = NAME_TRANSFORMER.getNamespace(namespace);
    return retrieveRecordsFromTable(tableName, schema);
  }

  private List<JsonNode> retrieveRecordsFromTable(final String tableName, final String schema) throws SQLException {
    final TimeZone timeZone = TimeZone.getTimeZone("UTC");
    TimeZone.setDefault(timeZone);

    return database.bufferedResultSetQuery(
        connection -> {
          try (final ResultSet tableInfo = connection.createStatement()
              .executeQuery(String.format("SHOW TABLES LIKE '%s' IN SCHEMA \"%s\";", tableName, schema))) {
            assertTrue(tableInfo.next());
            // check that we're creating permanent tables. DBT defaults to transient tables, which have
            // `TRANSIENT` as the value for the `kind` column.
            assertEquals("TABLE", tableInfo.getString("kind"));
            connection.createStatement().execute("ALTER SESSION SET TIMEZONE = 'UTC';");
            return connection.createStatement()
                .executeQuery(String.format("SELECT * FROM \"%s\".\"%s\" ORDER BY \"%s\" ASC;", schema, tableName,
                    JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT));
          }
        },
        new SnowflakeSourceOperations()::rowToJson);
  }

  // for each test we create a new schema in the database. run the test in there and then remove it.
  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) throws Exception {
    final String schemaName = Strings.addRandomSuffix("integration_test", "_", 5);
    final String createSchemaQuery = String.format("CREATE SCHEMA %s", schemaName);
    TEST_SCHEMAS.add(schemaName);

    this.config = Jsons.clone(getStaticConfig());
    ((ObjectNode) config).put("schema", schemaName);

    dataSource = SnowflakeDatabase.createDataSource(config, OssCloudEnvVarConsts.AIRBYTE_OSS);
    database = SnowflakeDatabase.getDatabase(dataSource);
    database.execute(createSchemaQuery);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) throws Exception {
    getTestSchemas().add(config.get("schema").asText());
    for (final String schema : getTestSchemas()) {
      // we need to wrap namespaces in quotes, but that means we have to manually upcase them.
      // thanks, v1 destinations!
      // this probably doesn't actually work, because v1 destinations are mangling namespaces and names
      // but it's approximately correct and maybe works for some things.
      final String mangledSchema = schema.toUpperCase();
      final String dropSchemaQuery = String.format("DROP SCHEMA IF EXISTS \"%s\"", mangledSchema);
      database.execute(dropSchemaQuery);
    }

    DataSourceFactory.close(dataSource);
  }

  @Disabled("See README for why this test is disabled")
  @Test
  public void testCheckWithNoTextSchemaPermissionConnection() throws Exception {
    // Config to user (creds) that has no permission to schema
    final JsonNode config = Jsons.deserialize(IOs.readFile(
        Path.of("secrets/config_no_text_schema_permission.json")));

    final StandardCheckConnectionOutput standardCheckConnectionOutput = runCheck(config);

    assertEquals(Status.FAILED, standardCheckConnectionOutput.getStatus());
    assertThat(standardCheckConnectionOutput.getMessage()).contains(NO_USER_PRIVILEGES_ERR_MSG);
  }

  @Test
  public void testCheckIpNotInWhiteListConnection() throws Exception {
    // Config to user(creds) that has no warehouse assigned
    final JsonNode config = Jsons.deserialize(IOs.readFile(
        Path.of("secrets/insert_ip_not_in_whitelist_config.json")));

    final StandardCheckConnectionOutput standardCheckConnectionOutput = runCheck(config);

    assertEquals(Status.FAILED, standardCheckConnectionOutput.getStatus());
    assertThat(standardCheckConnectionOutput.getMessage()).contains(IP_NOT_IN_WHITE_LIST_ERR_MSG);
  }

  @Test
  public void testBackwardCompatibilityAfterAddingOauth() {
    final JsonNode deprecatedStyleConfig = Jsons.clone(config);
    final JsonNode password = deprecatedStyleConfig.get("credentials").get("password");

    ((ObjectNode) deprecatedStyleConfig).remove("credentials");
    ((ObjectNode) deprecatedStyleConfig).set("password", password);

    assertEquals(Status.SUCCEEDED, runCheckWithCatchedException(deprecatedStyleConfig));
  }

  @Test
  void testCheckWithKeyPairAuth() throws Exception {
    final JsonNode credentialsJsonString = Jsons.deserialize(IOs.readFile(Path.of("secrets/config_key_pair.json")));
    final AirbyteConnectionStatus check = new SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_OSS).check(credentialsJsonString);
    assertEquals(AirbyteConnectionStatus.Status.SUCCEEDED, check.getStatus());
  }

  /**
   * This test is disabled because it is very slow, and should only be run manually for now.
   */
  @Disabled
  @ParameterizedTest
  @ArgumentsSource(DataArgumentsProvider.class)
  public void testSyncWithBillionRecords(final String messagesFilename, final String catalogFilename) throws Exception {
    final AirbyteCatalog catalog = Jsons.deserialize(MoreResources.readResource(catalogFilename), AirbyteCatalog.class);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = MoreResources.readResource(messagesFilename).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).toList();

    final List<AirbyteMessage> largeNumberRecords =
        Collections.nCopies(15000000, messages).stream().flatMap(List::stream).collect(Collectors.toList());

    final JsonNode config = getConfig();
    runSyncAndVerifyStateOutput(config, largeNumberRecords, configuredCatalog, false);
  }

}
