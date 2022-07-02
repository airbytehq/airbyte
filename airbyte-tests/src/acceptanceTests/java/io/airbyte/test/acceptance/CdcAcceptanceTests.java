/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.acceptance;

import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.COLUMN_ID;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.COLUMN_NAME;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.STREAM_NAME;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.waitForSuccessfulJob;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.waitWhileJobHasStatus;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.generated.ApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.AirbyteCatalog;
import io.airbyte.api.client.model.generated.AirbyteStream;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.DestinationDefinitionRead;
import io.airbyte.api.client.model.generated.DestinationSyncMode;
import io.airbyte.api.client.model.generated.JobInfoRead;
import io.airbyte.api.client.model.generated.JobStatus;
import io.airbyte.api.client.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.client.model.generated.SourceDefinitionRead;
import io.airbyte.api.client.model.generated.SourceRead;
import io.airbyte.api.client.model.generated.SyncMode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.test.utils.AirbyteAcceptanceTestHarness;
import io.airbyte.test.utils.SchemaTableNamePair;
import java.io.IOException;
import java.net.URISyntaxException;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;

public class CdcAcceptanceTests {

  record DestinationCdcRecordMatcher(JsonNode sourceRecord, Instant minUpdatedAt, Optional<Instant> minDeletedAt) {}

  private static final Logger LOGGER = LoggerFactory.getLogger(BasicAcceptanceTests.class);

  private static final String POSTGRES_INIT_SQL_FILE = "postgres_init_cdc.sql";
  // must match replication slot name used in the above POSTGRES_INIT_SQL_FILE
  private static final String REPLICATION_SLOT = "airbyte_slot";
  // must match publication name used in the above POSTGRES_INIT_SQL_FILE
  private static final String PUBLICATION = "airbyte_publication";

  private static final String SCHEMA_NAME = "public";
  private static final String CDC_UPDATED_AT_COLUMN = "_ab_cdc_updated_at";
  private static final String CDC_DELETED_AT_COLUMN = "_ab_cdc_deleted_at";

  private static AirbyteAcceptanceTestHarness testHarness;
  private static AirbyteApiClient apiClient;
  private static UUID workspaceId;
  private static PostgreSQLContainer sourcePsql;

  @BeforeAll
  public static void init() throws URISyntaxException, IOException, InterruptedException, ApiException {
    apiClient = new AirbyteApiClient(
        new ApiClient().setScheme("http")
            .setHost("localhost")
            .setPort(8001)
            .setBasePath("/api"));
    // work in whatever default workspace is present.
    workspaceId = apiClient.getWorkspaceApi().listWorkspaces().getWorkspaces().get(0).getWorkspaceId();
    LOGGER.info("workspaceId = " + workspaceId);

    // log which connectors are being used.
    final SourceDefinitionRead sourceDef = apiClient.getSourceDefinitionApi()
        .getSourceDefinition(new SourceDefinitionIdRequestBody()
            .sourceDefinitionId(UUID.fromString("decd338e-5647-4c0b-adf4-da0e75f5a750")));
    final DestinationDefinitionRead destinationDef = apiClient.getDestinationDefinitionApi()
        .getDestinationDefinition(new DestinationDefinitionIdRequestBody()
            .destinationDefinitionId(UUID.fromString("25c5221d-dce2-4163-ade9-739ef790f503")));
    LOGGER.info("pg source definition: {}", sourceDef.getDockerImageTag());
    LOGGER.info("pg destination definition: {}", destinationDef.getDockerImageTag());

    testHarness = new AirbyteAcceptanceTestHarness(apiClient, workspaceId, POSTGRES_INIT_SQL_FILE);
    sourcePsql = testHarness.getSourcePsql();
  }

  @AfterAll
  public static void end() {
    testHarness.stopDbAndContainers();
  }

  @BeforeEach
  public void setup() throws SQLException, URISyntaxException, IOException {
    testHarness.setup();
  }

  @AfterEach
  public void tearDown() {
    testHarness.cleanup();
  }

  @Test
  @Order(12)
  public void testIncrementalSync() throws Exception {
    LOGGER.info("Starting testIncrementalSync()");
    final String connectionName = "test-connection";

    final String sourceName = "CDC Source DB";
    final UUID postgresSourceDefinitionId = testHarness.getPostgresSourceDefinitionId();
    JsonNode sourceDbConfig = testHarness.getSourceDbConfig();
    final Map<Object, Object> sourceDbConfigMap = Jsons.object(sourceDbConfig, Map.class);
    sourceDbConfigMap.put("replication_method", ImmutableMap.builder()
        .put("method", "CDC")
        .put("replication_slot", REPLICATION_SLOT)
        .put("publication", PUBLICATION)
        .build());
    sourceDbConfig = Jsons.jsonNode(sourceDbConfigMap);
    LOGGER.info("final sourceDbConfig: {}", sourceDbConfigMap);

    final SourceRead sourceRead = testHarness.createSource(
        sourceName,
        workspaceId,
        postgresSourceDefinitionId,
        sourceDbConfig);

    final UUID sourceId = sourceRead.getSourceId();
    final UUID destinationId = testHarness.createDestination().getDestinationId();
    final UUID operationId = testHarness.createOperation().getOperationId();
    final AirbyteCatalog catalog = testHarness.discoverSourceSchema(sourceId);
    final AirbyteStream stream = catalog.getStreams().get(0).getStream();
    LOGGER.info("stream: {}", stream);

    assertEquals(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL), stream.getSupportedSyncModes());
    assertTrue(stream.getSourceDefinedCursor());
    assertTrue(stream.getDefaultCursorField().isEmpty());
    assertEquals(List.of(List.of("id")), stream.getSourceDefinedPrimaryKey());

    final SyncMode syncMode = SyncMode.INCREMENTAL;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.APPEND;
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(syncMode)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(destinationSyncMode));
    final UUID connectionId =
        testHarness.createConnection(connectionName, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();
    LOGGER.info("Beginning testIncrementalSync() sync 1");

    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());
    LOGGER.info("state after sync 1: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    final Database source = testHarness.getSourceDatabase();
    List<JsonNode> sourceRecords = testHarness.retrieveSourceRecords(source, STREAM_NAME);
    List<DestinationCdcRecordMatcher> expectedDestRecordMatchers = new ArrayList<>(sourceRecords
        .stream()
        .map(sourceRecord -> new DestinationCdcRecordMatcher(sourceRecord, Instant.EPOCH, Optional.empty()))
        .toList());

    assertDestinationMatches(expectedDestRecordMatchers);

    final Instant beforeFirstUpdate = Instant.now();

    // add new records and run again.
    // add a new record
    source.query(ctx -> ctx.execute("INSERT INTO id_and_name(id, name) VALUES(6, 'geralt')"));
    // mutate a record that was already synced with out updating its cursor value.
    // since this is a CDC connection, the destination should contain a record with this
    // new value and an updated_at time corresponding to this update query
    source.query(ctx -> ctx.execute("UPDATE id_and_name SET name='yennefer' WHERE id=2"));

    expectedDestRecordMatchers.add(new DestinationCdcRecordMatcher(
        Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 6).put(COLUMN_NAME, "geralt").build()),
        beforeFirstUpdate,
        Optional.empty()));

    expectedDestRecordMatchers.add(new DestinationCdcRecordMatcher(
        Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 2).put(COLUMN_NAME, "yennefer").build()),
        beforeFirstUpdate,
        Optional.empty()));

    LOGGER.info("Starting testIncrementalSync() sync 2");
    final JobInfoRead connectionSyncRead2 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());
    LOGGER.info("state after sync 2: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    assertDestinationMatches(expectedDestRecordMatchers);

    // reset back to no data.

    LOGGER.info("Starting testIncrementalSync() reset");
    final JobInfoRead jobInfoRead = apiClient.getConnectionApi().resetConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitWhileJobHasStatus(apiClient.getJobsApi(), jobInfoRead.getJob(),
        Sets.newHashSet(JobStatus.PENDING, JobStatus.RUNNING, JobStatus.INCOMPLETE, JobStatus.FAILED));

    LOGGER.info("state after reset: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    assertDestinationMatches(Collections.emptyList());

    // sync one more time. verify it is the equivalent of a full refresh.
    LOGGER.info("Starting testIncrementalSync() sync 3");
    final JobInfoRead connectionSyncRead3 =
        apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead3.getJob());
    LOGGER.info("state after sync 3: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    sourceRecords = testHarness.retrieveSourceRecords(source, STREAM_NAME);
    expectedDestRecordMatchers = sourceRecords
        .stream()
        .map(sourceRecord -> new DestinationCdcRecordMatcher(sourceRecord, Instant.EPOCH, Optional.empty()))
        .toList();

    assertDestinationMatches(expectedDestRecordMatchers);
  }

  private void assertDestinationMatches(List<DestinationCdcRecordMatcher> expectedDestRecordMatchers) throws Exception {
    final List<JsonNode> destRecords = testHarness.retrieveRawDestinationRecords(new SchemaTableNamePair(SCHEMA_NAME, STREAM_NAME));
    if (destRecords.size() != expectedDestRecordMatchers.size()) {
      throw new IllegalStateException(String.format(
          "The number of destination records %d does not match the expected number %d", destRecords.size(), expectedDestRecordMatchers.size()));
    }

    for (DestinationCdcRecordMatcher recordMatcher : expectedDestRecordMatchers) {
      final List<JsonNode> matchingDestRecords = destRecords.stream().filter(destRecord -> {
        Map<String, Object> sourceRecordMap = Jsons.object(recordMatcher.sourceRecord, Map.class);
        Map<String, Object> destRecordMap = Jsons.object(destRecord, Map.class);

        boolean sourceRecordValuesMatch = sourceRecordMap.keySet()
            .stream()
            .allMatch(column -> sourceRecordMap.get(column).equals(destRecordMap.get(column)));
        boolean cdcUpdatedAtMatches = Instant.parse(String.valueOf(destRecordMap.get(CDC_UPDATED_AT_COLUMN))).isAfter(recordMatcher.minUpdatedAt);
        boolean cdcDeletedAtMatches = recordMatcher.minDeletedAt.isPresent()
            ? Instant.parse(String.valueOf(destRecordMap.get(CDC_DELETED_AT_COLUMN))).isAfter(recordMatcher.minDeletedAt.get())
            : destRecordMap.get(CDC_DELETED_AT_COLUMN) == null;

        return sourceRecordValuesMatch && cdcUpdatedAtMatches && cdcDeletedAtMatches;
      }).toList();

      if (matchingDestRecords.size() == 0) {
        throw new IllegalStateException(String.format(
            "Could not find a matching CDC destination record for record matcher %s. Destination records: %s", recordMatcher, destRecords));
      }
      if (matchingDestRecords.size() > 1) {
        throw new IllegalStateException(String.format(
            "Expected only one matching CDC destination record for record matcher %s, but found multiple: %s", recordMatcher, matchingDestRecords));
      }
    }
  }

}
