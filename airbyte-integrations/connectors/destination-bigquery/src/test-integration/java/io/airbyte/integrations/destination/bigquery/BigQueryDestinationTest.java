/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import static java.util.stream.Collectors.toList;
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
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.NamingConventionTransformer;
import io.airbyte.integrations.destination.StandardNameTransformer;
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
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInfo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class BigQueryDestinationTest {

  private static final Path CREDENTIALS_PATH = Path.of("secrets/credentials.json");

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryDestinationTest.class);

  private static final String BIG_QUERY_CLIENT_CHUNK_SIZE = "big_query_client_buffer_size_mb";
  private static final Instant NOW = Instant.now();
  private static final String USERS_STREAM_NAME = "users";
  private static final String TASKS_STREAM_NAME = "tasks";
  private static final AirbyteMessage MESSAGE_USERS1 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "john").put("id", "10").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_USERS2 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(USERS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("name", "susan").put("id", "30").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_TASKS1 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(TASKS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("goal", "announce the game.").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_TASKS2 = new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withStream(TASKS_STREAM_NAME)
          .withData(Jsons.jsonNode(ImmutableMap.builder().put("goal", "ship some code.").build()))
          .withEmittedAt(NOW.toEpochMilli()));
  private static final AirbyteMessage MESSAGE_STATE = new AirbyteMessage().withType(AirbyteMessage.Type.STATE)
      .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.builder().put("checkpoint", "now!").build())));

  private static final NamingConventionTransformer NAMING_RESOLVER = new StandardNameTransformer();

  private JsonNode config;

  private BigQuery bigquery;
  private Dataset dataset;
  private ConfiguredAirbyteCatalog catalog;

  private boolean tornDown = true;

  @BeforeEach
  void setup(final TestInfo info) throws IOException {
    if (info.getDisplayName().equals("testSpec()")) {
      return;
    }

    if (!Files.exists(CREDENTIALS_PATH)) {
      throw new IllegalStateException(
          "Must provide path to a big query credentials file. By default {module-root}/config/credentials.json. Override by setting setting path with the CREDENTIALS_PATH constant.");
    }
    final String fullConfigAsString = new String(Files.readAllBytes(CREDENTIALS_PATH));
    final JsonNode credentialsJson = Jsons.deserialize(fullConfigAsString).get(BigQueryConsts.BIGQUERY_BASIC_CONFIG);

    final String projectId = credentialsJson.get(BigQueryConsts.CONFIG_PROJECT_ID).asText();

    final ServiceAccountCredentials credentials = ServiceAccountCredentials
        .fromStream(new ByteArrayInputStream(credentialsJson.toString().getBytes()));
    bigquery = BigQueryOptions.newBuilder()
        .setProjectId(projectId)
        .setCredentials(credentials)
        .build()
        .getService();

    final String datasetId = Strings.addRandomSuffix("111airbyte_tests", "_", 8);
    final String datasetLocation = "EU";
    MESSAGE_USERS1.getRecord().setNamespace(datasetId);
    MESSAGE_USERS2.getRecord().setNamespace(datasetId);
    MESSAGE_TASKS1.getRecord().setNamespace(datasetId);
    MESSAGE_TASKS2.getRecord().setNamespace(datasetId);

    catalog = new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        CatalogHelpers.createConfiguredAirbyteStream(USERS_STREAM_NAME, datasetId,
            io.airbyte.protocol.models.Field.of("name", JsonSchemaPrimitive.STRING),
            io.airbyte.protocol.models.Field
                .of("id", JsonSchemaPrimitive.STRING))
            .withDestinationSyncMode(DestinationSyncMode.APPEND),
        CatalogHelpers.createConfiguredAirbyteStream(TASKS_STREAM_NAME, datasetId, Field.of("goal", JsonSchemaPrimitive.STRING))));

    final DatasetInfo datasetInfo = DatasetInfo.newBuilder(datasetId).setLocation(datasetLocation).build();
    dataset = bigquery.create(datasetInfo);

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put(BigQueryConsts.CONFIG_PROJECT_ID, projectId)
        .put(BigQueryConsts.CONFIG_CREDS, credentialsJson.toString())
        .put(BigQueryConsts.CONFIG_DATASET_ID, datasetId)
        .put(BigQueryConsts.CONFIG_DATASET_LOCATION, datasetLocation)
        .put(BIG_QUERY_CLIENT_CHUNK_SIZE, 10)
        .build());

    tornDown = false;
    Runtime.getRuntime()
        .addShutdownHook(
            new Thread(
                () -> {
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

  private void tearDownBigQuery() {
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

  @Test
  void testCheckSuccess() {
    final AirbyteConnectionStatus actual = new BigQueryDestination().check(config);
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    assertEquals(expected, actual);
  }

  @Test
  void testCheckFailure() {
    ((ObjectNode) config).put(BigQueryConsts.CONFIG_PROJECT_ID, "fake");
    final AirbyteConnectionStatus actual = new BigQueryDestination().check(config);
    final String actualMessage = actual.getMessage();
    LOGGER.info("Checking expected failure message:" + actualMessage);
    assertTrue(actualMessage.contains("Access Denied:"));
    final AirbyteConnectionStatus expected = new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage("");
    assertEquals(expected, actual.withMessage(""));
  }

  @Test
  void testWriteSuccess() throws Exception {
    final BigQueryDestination destination = new BigQueryDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

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
  void testWriteFailure() throws Exception {
    // hack to force an exception to be thrown from within the consumer.
    final AirbyteMessage spiedMessage = spy(MESSAGE_USERS1);
    doThrow(new RuntimeException()).when(spiedMessage).getRecord();

    final AirbyteMessageConsumer consumer = spy(new BigQueryDestination().getConsumer(config, catalog, Destination::defaultOutputRecordCollector));

    assertThrows(RuntimeException.class, () -> consumer.accept(spiedMessage));
    consumer.accept(MESSAGE_USERS2);
    consumer.close();

    final List<String> tableNames = catalog.getStreams()
        .stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        .collect(toList());
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

  @Test
  void testWritePartitionOverUnpartitioned() throws Exception {
    final String raw_table_name = String.format("_airbyte_raw_%s", USERS_STREAM_NAME);
    createUnpartitionedTable(bigquery, dataset, raw_table_name);
    assertFalse(isTablePartitioned(bigquery, dataset, raw_table_name));
    final BigQueryDestination destination = new BigQueryDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

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
