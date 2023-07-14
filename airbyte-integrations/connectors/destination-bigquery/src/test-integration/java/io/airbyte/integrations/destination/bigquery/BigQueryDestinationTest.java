/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.TestInstance.Lifecycle.PER_CLASS;
import static org.mockito.Mockito.spy;

import com.amazonaws.services.s3.AmazonS3;
import com.fasterxml.jackson.databind.JsonNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableInfo;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.DestinationConfig;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.gcs.GcsDestinationConfig;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@TestInstance(PER_CLASS)
class BigQueryDestinationTest {

  protected static final Path CREDENTIALS_STANDARD_INSERT_PATH = Path.of("secrets/credentials-standard.json");
  protected static final Path CREDENTIALS_BAD_PROJECT_PATH = Path.of("secrets/credentials-badproject.json");
  protected static final Path CREDENTIALS_NO_DATASET_CREATION_PATH =
      Path.of("secrets/credentials-standard-no-dataset-creation.json");
  protected static final Path CREDENTIALS_NON_BILLABLE_PROJECT_PATH =
      Path.of("secrets/credentials-standard-non-billable-project.json");
  protected static final Path CREDENTIALS_NO_EDIT_PUBLIC_SCHEMA_ROLE_PATH =
      Path.of("secrets/credentials-no-edit-public-schema-role.json");
  protected static final Path CREDENTIALS_WITH_GCS_STAGING_PATH =
      Path.of("secrets/credentials-gcs-staging.json");

  protected static final Path[] ALL_PATHS = {CREDENTIALS_STANDARD_INSERT_PATH, CREDENTIALS_BAD_PROJECT_PATH, CREDENTIALS_NO_DATASET_CREATION_PATH,
    CREDENTIALS_NO_EDIT_PUBLIC_SCHEMA_ROLE_PATH, CREDENTIALS_NON_BILLABLE_PROJECT_PATH, CREDENTIALS_WITH_GCS_STAGING_PATH};

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDestinationTest.class);
  private static final String DATASET_NAME_PREFIX = "bq_dest_integration_test";

  private static final Instant NOW = Instant.now();
  protected static final String USERS_STREAM_NAME = "users";
  protected static final String TASKS_STREAM_NAME = "tasks";
  protected static final AirbyteMessage MESSAGE_USERS1 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "john").put("id", "10").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  protected static final AirbyteMessage MESSAGE_USERS2 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "susan").put("id", "30").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  protected static final AirbyteMessage MESSAGE_TASKS1 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(TASKS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("goal", "announce the game.").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  protected static final AirbyteMessage MESSAGE_TASKS2 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(TASKS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("goal", "ship some code.").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  protected static final AirbyteMessage MESSAGE_STATE = new AirbyteMessage().withType(AirbyteMessage.Type.STATE)
      .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.builder().put("checkpoint", "now!").build())));

  private static final NamingConventionTransformer NAMING_RESOLVER = new BigQuerySQLNameTransformer();

  protected static String projectId;
  protected static String datasetId;
  protected static JsonNode config;
  protected static JsonNode configWithProjectId;
  protected static JsonNode configWithBadProjectId;
  protected static JsonNode insufficientRoleConfig;
  protected static JsonNode noEditPublicSchemaRoleConfig;
  protected static JsonNode nonBillableConfig;
  protected static JsonNode gcsStagingConfig; // default BigQuery config. Also used for setup/teardown
  protected BigQuery bigquery;
  protected Dataset dataset;
  protected static Map<String, JsonNode> configs;
  protected static ConfiguredAirbyteCatalog catalog;

  private AmazonS3 s3Client;

  /*
   * TODO: Migrate all BigQuery Destination configs (GCS, Denormalized, Normalized) to no longer use
   * #partitionIfUnpartitioned then recombine Base Provider. The reason for breaking this method into
   * a base class is because #testWritePartitionOverUnpartitioned is no longer used only in GCS
   * Staging
   */
  private Stream<Arguments> successTestConfigProviderBase() {
    return Stream.of(
        Arguments.of("config"),
        Arguments.of("configWithProjectId"));
  }

  private Stream<Arguments> successTestConfigProvider() {
    return Stream.concat(successTestConfigProviderBase(), Stream.of(Arguments.of("gcsStagingConfig")));
  }

  private Stream<Arguments> failCheckTestConfigProvider() {
    return Stream.of(
        Arguments.of("configWithBadProjectId", "User does not have bigquery.datasets.create permission in project"),
        Arguments.of("insufficientRoleConfig", "User does not have bigquery.datasets.create permission"),
        Arguments.of("nonBillableConfig", "Access Denied: BigQuery BigQuery: Streaming insert is not allowed in the free tier"));
  }

  private Stream<Arguments> failWriteTestConfigProvider() {
    return Stream.of(
        Arguments.of("configWithBadProjectId", "User does not have bigquery.datasets.create permission in project"),
        Arguments.of("noEditPublicSchemaRoleConfig", "Failed to write to destination schema."), // (or it may not exist)
        Arguments.of("insufficientRoleConfig", "Permission bigquery.tables.create denied"));
  }

  @BeforeAll
  public static void beforeAll() throws IOException {
    for (final Path path : ALL_PATHS) {
      if (!Files.exists(path)) {
        throw new IllegalStateException(
            String.format("Must provide path to a big query credentials file. Please add file with credentials to %s", path.toAbsolutePath()));
      }
    }

    datasetId = Strings.addRandomSuffix(DATASET_NAME_PREFIX, "_", 8);
    // Set up config objects for test scenarios
    // config - basic config for standard inserts that should succeed check and write tests
    // this config is also used for housekeeping (checking records, and cleaning up)
    config = BigQueryDestinationTestUtils.createConfig(CREDENTIALS_STANDARD_INSERT_PATH, datasetId);

    DestinationConfig.initialize(config);

    // all successful configs use the same project ID
    projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();

    // configWithProjectId - config that uses project:dataset notation for datasetId
    final String dataSetWithProjectId = String.format("%s:%s", projectId, datasetId);
    configWithProjectId = BigQueryDestinationTestUtils.createConfig(CREDENTIALS_STANDARD_INSERT_PATH, dataSetWithProjectId);

    // configWithBadProjectId - config that uses "fake" project ID and should fail
    final String dataSetWithBadProjectId = String.format("%s:%s", "fake", datasetId);
    configWithBadProjectId = BigQueryDestinationTestUtils.createConfig(CREDENTIALS_BAD_PROJECT_PATH, dataSetWithBadProjectId);

    // config that has insufficient privileges
    insufficientRoleConfig = BigQueryDestinationTestUtils.createConfig(CREDENTIALS_NO_DATASET_CREATION_PATH, datasetId);
    // config that tries to write to a project with disabled billing (free tier)
    nonBillableConfig = BigQueryDestinationTestUtils.createConfig(CREDENTIALS_NON_BILLABLE_PROJECT_PATH, "testnobilling");
    // config that has no privileges to edit anything in Public schema
    noEditPublicSchemaRoleConfig = BigQueryDestinationTestUtils.createConfig(CREDENTIALS_NO_EDIT_PUBLIC_SCHEMA_ROLE_PATH, "public");
    // config with GCS staging
    gcsStagingConfig = BigQueryDestinationTestUtils.createConfig(CREDENTIALS_WITH_GCS_STAGING_PATH, datasetId);

    MESSAGE_USERS1.getRecord().setNamespace(datasetId);
    MESSAGE_USERS2.getRecord().setNamespace(datasetId);
    MESSAGE_TASKS1.getRecord().setNamespace(datasetId);
    MESSAGE_TASKS2.getRecord().setNamespace(datasetId);

    catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        CatalogHelpers.createConfiguredAirbyteStream(USERS_STREAM_NAME, datasetId,
            io.airbyte.protocol.models.Field.of("name", JsonSchemaType.STRING),
            io.airbyte.protocol.models.Field
                .of("id", JsonSchemaType.STRING))
            .withDestinationSyncMode(DestinationSyncMode.APPEND),
        CatalogHelpers.createConfiguredAirbyteStream(TASKS_STREAM_NAME, datasetId, Field.of("goal", JsonSchemaType.STRING))));

    configs = new HashMap<String, JsonNode>() {

      {
        put("config", config);
        put("configWithProjectId", configWithProjectId);
        put("configWithBadProjectId", configWithBadProjectId);
        put("insufficientRoleConfig", insufficientRoleConfig);
        put("noEditPublicSchemaRoleConfig", noEditPublicSchemaRoleConfig);
        put("nonBillableConfig", nonBillableConfig);
        put("gcsStagingConfig", gcsStagingConfig);
      }

    };
  }

  protected void initBigQuery(final JsonNode config) throws IOException {
    bigquery = BigQueryDestinationTestUtils.initBigQuery(config, projectId);
    try {
      dataset = BigQueryDestinationTestUtils.initDataSet(config, bigquery, datasetId);
    } catch (final Exception ex) {
      // ignore
    }
  }

  @BeforeEach
  void setup(final TestInfo info) throws IOException {
    if (info.getDisplayName().equals("testSpec()")) {
      return;
    }
    bigquery = null;
    dataset = null;
    final GcsDestinationConfig gcsDestinationConfig = GcsDestinationConfig
        .getGcsDestinationConfig(BigQueryUtils.getGcsJsonNodeConfig(gcsStagingConfig));
    this.s3Client = gcsDestinationConfig.getS3Client();
  }

  @AfterEach
  void tearDown(final TestInfo info) {
    if (info.getDisplayName().equals("testSpec()")) {
      return;
    }
    BigQueryDestinationTestUtils.tearDownBigQuery(bigquery, dataset, LOGGER);
    BigQueryDestinationTestUtils.tearDownGcs(s3Client, config, LOGGER);
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = new BigQueryDestination().spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final ConnectorSpecification expected = Jsons.deserialize(resourceString, ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  @ParameterizedTest
  @MethodSource("successTestConfigProvider")
  void testCheckSuccess(final String configName) throws IOException {
    final JsonNode testConfig = configs.get(configName);
    final AirbyteConnectionStatus actual = new BigQueryDestination().check(testConfig);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    assertEquals(expected, actual);
  }

  @ParameterizedTest
  @MethodSource("failCheckTestConfigProvider")
  void testCheckFailures(final String configName, final String error) {
    // TODO: this should always throw ConfigErrorException
    final JsonNode testConfig = configs.get(configName);
    final Exception ex = assertThrows(Exception.class, () -> {
      new BigQueryDestination().check(testConfig);
    });
    assertThat(ex.getMessage()).contains(error);
  }

  @ParameterizedTest
  @MethodSource("successTestConfigProvider")
  void testWriteSuccess(final String configName) throws Exception {
    initBigQuery(config);
    final JsonNode testConfig = configs.get(configName);
    final BigQueryDestination destination = new BigQueryDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(testConfig, catalog, Destination::defaultOutputRecordCollector);

    consumer.start();
    consumer.accept(MESSAGE_USERS1);
    consumer.accept(MESSAGE_TASKS1);
    consumer.accept(MESSAGE_USERS2);
    consumer.accept(MESSAGE_TASKS2);
    consumer.accept(MESSAGE_STATE);
    consumer.close();

    final List<JsonNode> usersActual = retrieveRecords(NAMING_RESOLVER.getRawTableName(USERS_STREAM_NAME));
    final List<JsonNode> expectedUsersJson = Lists.newArrayList(MESSAGE_USERS1.getRecord().getData(), MESSAGE_USERS2.getRecord().getData());
    assertEquals(expectedUsersJson.size(), usersActual.size());
    assertTrue(expectedUsersJson.containsAll(usersActual) && usersActual.containsAll(expectedUsersJson));

    final List<JsonNode> tasksActual = retrieveRecords(NAMING_RESOLVER.getRawTableName(TASKS_STREAM_NAME));
    final List<JsonNode> expectedTasksJson = Lists.newArrayList(MESSAGE_TASKS1.getRecord().getData(), MESSAGE_TASKS2.getRecord().getData());
    assertEquals(expectedTasksJson.size(), tasksActual.size());
    assertTrue(expectedTasksJson.containsAll(tasksActual) && tasksActual.containsAll(expectedTasksJson));

    assertTmpTablesNotPresent(catalog.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        .collect(Collectors.toList()));
  }

  @Test
  void testCreateTableSuccessWhenTableAlreadyExists() throws Exception {
    initBigQuery(config);

    // Test schema where we will try to re-create existing table
    final String tmpTestSchemaName = "test_create_table_when_exists_schema";

    final com.google.cloud.bigquery.Schema schema = com.google.cloud.bigquery.Schema.of(
        com.google.cloud.bigquery.Field.of(JavaBaseConstants.COLUMN_NAME_AB_ID, StandardSQLTypeName.STRING),
        com.google.cloud.bigquery.Field.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, StandardSQLTypeName.TIMESTAMP),
        com.google.cloud.bigquery.Field.of(JavaBaseConstants.COLUMN_NAME_DATA, StandardSQLTypeName.STRING));

    final TableId tableId = TableId.of(tmpTestSchemaName, "test_already_existing_table");

    BigQueryUtils.getOrCreateDataset(bigquery, tmpTestSchemaName, BigQueryUtils.getDatasetLocation(config));

    assertDoesNotThrow(() -> {
      // Create table
      BigQueryUtils.createPartitionedTableIfNotExists(bigquery, tableId, schema);

      // Try to create it one more time. Shouldn't throw exception
      BigQueryUtils.createPartitionedTableIfNotExists(bigquery, tableId, schema);
    });
  }

  @ParameterizedTest
  @MethodSource("failWriteTestConfigProvider")
  void testWriteFailure(final String configName, final String error) throws Exception {
    initBigQuery(config);
    final JsonNode testConfig = configs.get(configName);
    final Exception ex = assertThrows(Exception.class, () -> {
      final AirbyteMessageConsumer consumer =
          spy(new BigQueryDestination().getConsumer(testConfig, catalog, Destination::defaultOutputRecordCollector));
      consumer.start();
    });
    assertThat(ex.getMessage()).contains(error);

    final List<String> tableNames = catalog.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        .toList();
    assertTmpTablesNotPresent(catalog.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        .collect(Collectors.toList()));
    // assert that no tables were created.
    assertTrue(fetchNamesOfTablesInDb().stream().noneMatch(tableName -> tableNames.stream().anyMatch(tableName::startsWith)));
  }

  private Set<String> fetchNamesOfTablesInDb() throws InterruptedException {
    if (dataset == null || bigquery == null) {
      return Collections.emptySet();
    }
    final QueryJobConfiguration queryConfig = QueryJobConfiguration
        .newBuilder(String.format("SELECT * FROM `%s.INFORMATION_SCHEMA.TABLES`;", dataset.getDatasetId().getDataset()))
        .setUseLegacySql(false)
        .build();

    if (!dataset.exists()) {
      return Collections.emptySet();
    }
    return StreamSupport
        .stream(BigQueryUtils.executeQuery(bigquery, queryConfig).getLeft().getQueryResults().iterateAll().spliterator(), false)
        .map(v -> v.get("TABLE_NAME").getStringValue()).collect(Collectors.toSet());
  }

  private void assertTmpTablesNotPresent(final List<String> tableNames) throws InterruptedException {
    final Set<String> tmpTableNamePrefixes = tableNames.stream().map(name -> name + "_").collect(Collectors.toSet());
    final Set<String> finalTableNames = tableNames.stream().map(name -> name + "_raw").collect(Collectors.toSet());
    // search for table names that have the tmp table prefix but are not raw tables.
    assertTrue(fetchNamesOfTablesInDb()
        .stream()
        .filter(tableName -> !finalTableNames.contains(tableName))
        .noneMatch(tableName -> tmpTableNamePrefixes.stream().anyMatch(tableName::startsWith)));
  }

  private List<JsonNode> retrieveRecords(final String tableName) throws Exception {
    final QueryJobConfiguration queryConfig =
        QueryJobConfiguration.newBuilder(String.format("SELECT * FROM `%s.%s`;", dataset.getDatasetId().getDataset(), tableName.toLowerCase()))
            .setUseLegacySql(false).build();

    BigQueryUtils.executeQuery(bigquery, queryConfig);

    return StreamSupport
        .stream(BigQueryUtils.executeQuery(bigquery, queryConfig).getLeft().getQueryResults().iterateAll().spliterator(), false)
        .map(v -> v.get(JavaBaseConstants.COLUMN_NAME_DATA).getStringValue())
        .map(Jsons::deserialize)
        .collect(Collectors.toList());
  }

  @ParameterizedTest
  @MethodSource("successTestConfigProviderBase")
  void testWritePartitionOverUnpartitioned(final String configName) throws Exception {
    final JsonNode testConfig = configs.get(configName);
    initBigQuery(config);
    final String raw_table_name = String.format("_airbyte_raw_%s", USERS_STREAM_NAME);
    createUnpartitionedTable(bigquery, dataset, raw_table_name);
    assertFalse(isTablePartitioned(bigquery, dataset, raw_table_name));
    final BigQueryDestination destination = new BigQueryDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(testConfig, catalog, Destination::defaultOutputRecordCollector);

    consumer.start();
    consumer.accept(MESSAGE_USERS1);
    consumer.accept(MESSAGE_TASKS1);
    consumer.accept(MESSAGE_USERS2);
    consumer.accept(MESSAGE_TASKS2);
    consumer.accept(MESSAGE_STATE);
    consumer.close();

    final List<JsonNode> usersActual = retrieveRecords(NAMING_RESOLVER.getRawTableName(USERS_STREAM_NAME));
    final List<JsonNode> expectedUsersJson = Lists.newArrayList(MESSAGE_USERS1.getRecord().getData(), MESSAGE_USERS2.getRecord().getData());
    assertEquals(expectedUsersJson.size(), usersActual.size());
    assertTrue(expectedUsersJson.containsAll(usersActual) && usersActual.containsAll(expectedUsersJson));

    final List<JsonNode> tasksActual = retrieveRecords(NAMING_RESOLVER.getRawTableName(TASKS_STREAM_NAME));
    final List<JsonNode> expectedTasksJson = Lists.newArrayList(MESSAGE_TASKS1.getRecord().getData(), MESSAGE_TASKS2.getRecord().getData());
    assertEquals(expectedTasksJson.size(), tasksActual.size());
    assertTrue(expectedTasksJson.containsAll(tasksActual) && tasksActual.containsAll(expectedTasksJson));

    assertTmpTablesNotPresent(catalog.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        .collect(Collectors.toList()));
    assertTrue(isTablePartitioned(bigquery, dataset, raw_table_name));
  }

  private void createUnpartitionedTable(final BigQuery bigquery, final Dataset dataset, final String tableName) {
    final TableId tableId = TableId.of(dataset.getDatasetId().getDataset(), tableName);
    bigquery.delete(tableId);
    final com.google.cloud.bigquery.Schema schema = com.google.cloud.bigquery.Schema.of(
        com.google.cloud.bigquery.Field.of(JavaBaseConstants.COLUMN_NAME_AB_ID, StandardSQLTypeName.STRING),
        com.google.cloud.bigquery.Field.of(JavaBaseConstants.COLUMN_NAME_EMITTED_AT, StandardSQLTypeName.TIMESTAMP),
        com.google.cloud.bigquery.Field.of(JavaBaseConstants.COLUMN_NAME_DATA, StandardSQLTypeName.STRING));
    final StandardTableDefinition tableDefinition =
        StandardTableDefinition.newBuilder()
            .setSchema(schema)
            .build();
    final TableInfo tableInfo = TableInfo.newBuilder(tableId, tableDefinition).build();
    bigquery.create(tableInfo);
  }

  private boolean isTablePartitioned(final BigQuery bigquery, final Dataset dataset, final String tableName) throws InterruptedException {
    final QueryJobConfiguration queryConfig = QueryJobConfiguration
        .newBuilder(
            String.format("SELECT max(is_partitioning_column) as is_partitioned FROM `%s.%s.INFORMATION_SCHEMA.COLUMNS` WHERE TABLE_NAME = '%s';",
                bigquery.getOptions().getProjectId(),
                dataset.getDatasetId().getDataset(),
                tableName))
        .setUseLegacySql(false)
        .build();
    final ImmutablePair<Job, String> result = BigQueryUtils.executeQuery(bigquery, queryConfig);
    for (final com.google.cloud.bigquery.FieldValueList row : result.getLeft().getQueryResults().getValues()) {
      return !row.get("is_partitioned").isNull() && row.get("is_partitioned").getStringValue().equals("YES");
    }
    return false;
  }

}
