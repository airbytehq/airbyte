/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.auth.oauth2.ServiceAccountCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.Dataset;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.Job;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.StandardTableDefinition;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableInfo;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.List;
import java.util.Set;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class BigQueryDestinationTest {

  protected static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");
  protected static final Path CREDENTIALS_WITH_MISSED_CREATE_DATASET_ROLE_PATH =
      Path.of("secrets/credentials-with-missed-dataset-creation-role.json");
  protected static final Path CREDENTIALS_NON_BILLABLE_PROJECT_PATH =
      Path.of("secrets/credentials-non-billable-project.json");

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDestinationTest.class);
  private static final String DATASET_NAME_PREFIX = "bq_dest_integration_test";

  protected static final String DATASET_LOCATION = "EU";
  protected static final String BIG_QUERY_CLIENT_CHUNK_SIZE = "big_query_client_buffer_size_mb";
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

  protected JsonNode config;
  protected BigQuery bigquery;
  protected Dataset dataset;
  protected ConfiguredAirbyteCatalog catalog;
  protected boolean tornDown = true;

  private static Stream<Arguments> datasetIdResetterProvider() {
    // parameterized test with two dataset-id patterns: `dataset_id` and `project-id:dataset_id`
    return Stream.of(
        Arguments.arguments(new DatasetIdResetter(config -> {})),
        Arguments.arguments(new DatasetIdResetter(
            config -> {
              final String projectId = config.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();
              final String datasetId = config.get(BigQueryConsts.CONFIG_DATASET_ID).asText();
              ((ObjectNode) config).put(BigQueryConsts.CONFIG_DATASET_ID,
                  String.format("%s:%s", projectId, datasetId));
            })));
  }

  @BeforeEach
  void setup(final TestInfo info) throws IOException {
    if (info.getDisplayName().equals("testSpec()")) {
      return;
    }

    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a big query credentials file. By default {module-root}/config/credentials.json. Override by setting setting path with the CREDENTIALS_PATH constant.");
    }
    final String fullConfigAsString = Files.readString(CREDENTIALS_PATH);
    final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString).get(BigQueryConsts.BIGQUERY_BASIC_CONFIG);

    final String projectId = credentialsJson.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();

    final ServiceAccountCredentials credentials = ServiceAccountCredentials
        .fromStream(new ByteArrayInputStream(credentialsJson.toString().getBytes(StandardCharsets.UTF_8)));
    bigquery = BigQueryOptions.newBuilder()
        .setProjectId(projectId)
        .setCredentials(credentials)
        .build()
        .getService();

    final String datasetId = Strings.addRandomSuffix(DATASET_NAME_PREFIX, "_", 8);
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

    final DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetId).setLocation(DATASET_LOCATION).build();
    dataset = bigquery.create(datasetInfo);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryConsts.CONFIG_CREDS, credentialsJson.toString())
        .put(BigQueryConsts.CONFIG_DATASET_ID, datasetId)
        .put(BigQueryConsts.CONFIG_DATASET_LOCATION, DATASET_LOCATION)
        .put(BIG_QUERY_CLIENT_CHUNK_SIZE, 10)
        .build());

    tornDown = false;
    addShutdownHook();
  }

  protected void addShutdownHook() {
    Runtime.getRuntime().addShutdownHook(new Thread(() -> {
      if (!tornDown) {
        tearDownBigQuery();
      }
    }));
  }

  @AfterEach
  void tearDown(final TestInfo info) {
    if (info.getDisplayName().equals("testSpec()")) {
      return;
    }

    tearDownBigQuery();
  }

  protected void tearDownBigQuery() {
    // allows deletion of a dataset that has contents
    final BigQuery.DatasetDeleteOption option = BigQuery.DatasetDeleteOption.deleteContents();

    final boolean success = bigquery.delete(dataset.getDatasetId(), option);
    if (success) {
      LOGGER.info("BQ Dataset " + dataset + " deleted...");
    } else {
      LOGGER.info("BQ Dataset cleanup for " + dataset + " failed!");
    }

    tornDown = true;
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = new BigQueryDestination().spec();
    final String resourceString = MoreResources.readResource("spec.json");
    final ConnectorSpecification expected = Jsons.deserialize(resourceString, ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

  @ParameterizedTest
  @MethodSource("datasetIdResetterProvider")
  void testCheckSuccess(final DatasetIdResetter resetDatasetId) {
    resetDatasetId.accept(config);
    final AirbyteConnectionStatus actual = new BigQueryDestination().check(config);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    assertEquals(expected, actual);
  }

  @ParameterizedTest
  @MethodSource("datasetIdResetterProvider")
  void testCheckFailure(final DatasetIdResetter resetDatasetId) {
    ((ObjectNode) config).put(BigQueryConsts.CONFIG_PROJECT_ID, "fake");
    resetDatasetId.accept(config);

    // Assert that check throws exception. Later it will be handled by IntegrationRunner
    final ConfigErrorException ex = assertThrows(ConfigErrorException.class, () -> {
      new BigQueryDestination().check(config);
    });

    assertThat(ex.getMessage()).contains("Access Denied");
  }

  @ParameterizedTest
  @MethodSource("datasetIdResetterProvider")
  void testCheckFailureInsufficientPermissionForCreateDataset(final DatasetIdResetter resetDatasetId) throws IOException {

    if (!Files.exists(CREDENTIALS_WITH_MISSED_CREATE_DATASET_ROLE_PATH)) {
      throw new IllegalStateException("""
                                      Json config not found. Must provide path to a big query credentials file,
                                       please add file with creds to
                                      ../destination-bigquery/secrets/credentialsWithMissedDatasetCreationRole.json.""");
    }
    final String fullConfigAsString = Files.readString(CREDENTIALS_WITH_MISSED_CREATE_DATASET_ROLE_PATH);
    final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString).get(BigQueryConsts.BIGQUERY_BASIC_CONFIG);
    final String projectId = credentialsJson.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();
    final String datasetId = Strings.addRandomSuffix(DATASET_NAME_PREFIX, "_", 8);

    final JsonNode insufficientRoleConfig;

    insufficientRoleConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryConsts.CONFIG_CREDS, credentialsJson.toString())
        .put(BigQueryConsts.CONFIG_DATASET_ID, datasetId)
        .put(BigQueryConsts.CONFIG_DATASET_LOCATION, DATASET_LOCATION)
        .put(BIG_QUERY_CLIENT_CHUNK_SIZE, 10)
        .build());

    resetDatasetId.accept(insufficientRoleConfig);

    // Assert that check throws exception. Later it will be handled by IntegrationRunner
    final ConfigErrorException ex = assertThrows(ConfigErrorException.class, () -> {
      new BigQueryDestination().check(insufficientRoleConfig);
    });

    assertThat(ex.getMessage()).contains("User does not have bigquery.datasets.create permission");
  }

  @ParameterizedTest
  @MethodSource("datasetIdResetterProvider")
  void testCheckFailureNonBillableProject(final DatasetIdResetter resetDatasetId) throws IOException {

    if (!Files.exists(CREDENTIALS_NON_BILLABLE_PROJECT_PATH)) {
      throw new IllegalStateException("""
                                      Json config not found. Must provide path to a big query credentials file,
                                       please add file with creds to
                                      ../destination-bigquery/secrets/credentials-non-billable-project.json""");
    }
    final String fullConfigAsString = Files.readString(CREDENTIALS_NON_BILLABLE_PROJECT_PATH);

    final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString).get(BigQueryConsts.BIGQUERY_BASIC_CONFIG);
    final String projectId = credentialsJson.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();

    final JsonNode insufficientRoleConfig;

    insufficientRoleConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryConsts.CONFIG_CREDS, credentialsJson.toString())
        .put(BigQueryConsts.CONFIG_DATASET_ID, "testnobilling")
        .put(BigQueryConsts.CONFIG_DATASET_LOCATION, "US")
        .put(BIG_QUERY_CLIENT_CHUNK_SIZE, 10)
        .build());

    resetDatasetId.accept(insufficientRoleConfig);

    // Assert that check throws exception. Later it will be handled by IntegrationRunner
    final ConfigErrorException ex = assertThrows(ConfigErrorException.class, () -> {
      new BigQueryDestination().check(insufficientRoleConfig);
    });

    assertThat(ex.getMessage()).contains("Access Denied: BigQuery BigQuery: Streaming insert is not allowed in the free tier");
  }

  @ParameterizedTest
  @MethodSource("datasetIdResetterProvider")
  void testWriteSuccess(final DatasetIdResetter resetDatasetId) throws Exception {
    resetDatasetId.accept(config);
    final BigQueryDestination destination = new BigQueryDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

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

  @ParameterizedTest
  @MethodSource("datasetIdResetterProvider")
  void testWriteFailure(final DatasetIdResetter resetDatasetId) throws Exception {
    resetDatasetId.accept(config);
    // hack to force an exception to be thrown from within the consumer.
    final AirbyteMessage spiedMessage = spy(MESSAGE_USERS1);
    doThrow(new RuntimeException()).when(spiedMessage).getRecord();

    final AirbyteMessageConsumer consumer = spy(new BigQueryDestination().getConsumer(config, catalog, Destination::defaultOutputRecordCollector));

    consumer.start();
    assertThrows(RuntimeException.class, () -> consumer.accept(spiedMessage));
    consumer.accept(MESSAGE_USERS2);
    consumer.close();

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
    final QueryJobConfiguration queryConfig = QueryJobConfiguration
        .newBuilder(String.format("SELECT * FROM `%s.INFORMATION_SCHEMA.TABLES`;", dataset.getDatasetId().getDataset()))
        .setUseLegacySql(false)
        .build();

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
  @MethodSource("datasetIdResetterProvider")
  void testWritePartitionOverUnpartitioned(final DatasetIdResetter resetDatasetId) throws Exception {
    resetDatasetId.accept(config);
    final String raw_table_name = String.format("_airbyte_raw_%s", USERS_STREAM_NAME);
    createUnpartitionedTable(bigquery, dataset, raw_table_name);
    assertFalse(isTablePartitioned(bigquery, dataset, raw_table_name));
    final BigQueryDestination destination = new BigQueryDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

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

  protected static class DatasetIdResetter {

    private final Consumer<JsonNode> consumer;

    DatasetIdResetter(final Consumer<JsonNode> consumer) {
      this.consumer = consumer;
    }

    public void accept(final JsonNode config) {
      consumer.accept(config);
    }

  }

}
