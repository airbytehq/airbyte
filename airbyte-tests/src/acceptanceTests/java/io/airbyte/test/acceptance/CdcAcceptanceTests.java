/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.acceptance;

import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.COLUMN_ID;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.COLUMN_NAME;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.STREAM_NAME;
import static io.airbyte.test.utils.AirbyteAcceptanceTestHarness.waitForSuccessfulJob;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
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
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CdcAcceptanceTests {

  record DestinationCdcRecordMatcher(JsonNode sourceRecord, Instant minUpdatedAt, Optional<Instant> minDeletedAt) {}

  private static final Logger LOGGER = LoggerFactory.getLogger(BasicAcceptanceTests.class);

  private static final String POSTGRES_INIT_SQL_FILE = "postgres_init_cdc.sql";
  private static final String CDC_METHOD = "CDC";
  // must match replication slot name used in the above POSTGRES_INIT_SQL_FILE
  private static final String REPLICATION_SLOT = "airbyte_slot";
  // must match publication name used in the above POSTGRES_INIT_SQL_FILE
  private static final String PUBLICATION = "airbyte_publication";

  private static final String SOURCE_NAME = "CDC Source";
  private static final String CONNECTION_NAME = "test-connection";
  private static final String SCHEMA_NAME = "public";
  private static final String CDC_UPDATED_AT_COLUMN = "_ab_cdc_updated_at";
  private static final String CDC_DELETED_AT_COLUMN = "_ab_cdc_deleted_at";

  // version of the postgres destination connector that was built with the
  // old Airbyte protocol that does not contain any per-stream logic/fields
  private static final String POSTGRES_DESTINATION_LEGACY_CONNECTOR_VERSION = "0.3.19";

  private static AirbyteApiClient apiClient;
  private static UUID workspaceId;

  private AirbyteAcceptanceTestHarness testHarness;

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
  }

  @BeforeEach
  public void setup() throws URISyntaxException, IOException, InterruptedException, ApiException, SQLException {
    testHarness = new AirbyteAcceptanceTestHarness(apiClient, workspaceId, POSTGRES_INIT_SQL_FILE);
    testHarness.setup();
  }

  @AfterEach
  public void end() {
    testHarness.cleanup();
    testHarness.stopDbAndContainers();
  }

  @Test
  public void testIncrementalCdcSync() throws Exception {
    LOGGER.info("Starting incremental cdc sync test");

    final UUID connectionId = createCdcConnection();
    LOGGER.info("Starting incremental cdc sync 1");

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

    LOGGER.info("Inserting and updating source db records");
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

    LOGGER.info("Starting incremental cdc sync 2");
    final JobInfoRead connectionSyncRead2 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());
    LOGGER.info("state after sync 2: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    assertDestinationMatches(expectedDestRecordMatchers);

    // reset back to no data.

    LOGGER.info("Starting incremental cdc reset");
    final JobInfoRead jobInfoRead = apiClient.getConnectionApi().resetConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), jobInfoRead.getJob());

    LOGGER.info("state after reset: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    assertDestinationMatches(Collections.emptyList());

    // sync one more time. verify it is the equivalent of a full refresh.
    LOGGER.info("Starting incremental cdc sync 3");
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

  // tests that incremental syncs still work properly even when using a destination connector that was
  // built on the old protocol that did not have any per-stream state fields
  @Test
  public void testIncrementalCdcSyncWithLegacyDestinationConnector() throws Exception {
    LOGGER.info("Starting testIncrementalCdcSyncWithLegacyDestinationConnector()");
    final UUID postgresDestDefId = testHarness.getPostgresDestinationDefinitionId();
    // Fetch the current/most recent source definition version
    final DestinationDefinitionRead destinationDefinitionRead = apiClient.getDestinationDefinitionApi().getDestinationDefinition(
        new DestinationDefinitionIdRequestBody().destinationDefinitionId(postgresDestDefId));
    LOGGER.info("Current postgres destination definition version: {}", destinationDefinitionRead.getDockerImageTag());

    try {
      LOGGER.info("Setting postgres destination definition to version {}", POSTGRES_DESTINATION_LEGACY_CONNECTOR_VERSION);
      testHarness.updateDestinationDefinitionVersion(postgresDestDefId, POSTGRES_DESTINATION_LEGACY_CONNECTOR_VERSION);

      testIncrementalCdcSync();
    } finally {
      // set postgres destination definition back to latest version for other tests
      LOGGER.info("Setting postgres destination definition back to version {}", destinationDefinitionRead.getDockerImageTag());
      testHarness.updateDestinationDefinitionVersion(postgresDestDefId, destinationDefinitionRead.getDockerImageTag());
    }
  }

  @Test
  public void testDeleteRecordCdcSync() throws Exception {
    LOGGER.info("Starting delete record cdc sync test");

    final UUID connectionId = createCdcConnection();
    LOGGER.info("Starting delete record cdc sync 1");

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

    final Instant beforeDelete = Instant.now();

    LOGGER.info("Deleting record");
    // delete a record
    source.query(ctx -> ctx.execute("DELETE FROM id_and_name WHERE id=1"));

    Map<String, Object> deletedRecordMap = new HashMap<>();
    deletedRecordMap.put(COLUMN_ID, 1);
    deletedRecordMap.put(COLUMN_NAME, null);
    expectedDestRecordMatchers.add(new DestinationCdcRecordMatcher(
        Jsons.jsonNode(deletedRecordMap),
        beforeDelete,
        Optional.of(beforeDelete)));

    LOGGER.info("Starting delete record cdc sync 2");
    final JobInfoRead connectionSyncRead2 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());
    LOGGER.info("state after sync 2: {}", apiClient.getConnectionApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)));

    assertDestinationMatches(expectedDestRecordMatchers);
  }

  private UUID createCdcConnection() throws ApiException {
    final SourceRead sourceRead = createCdcSource();
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
        testHarness.createConnection(CONNECTION_NAME, sourceId, destinationId, List.of(operationId), catalog, null).getConnectionId();
    return connectionId;
  }

  private SourceRead createCdcSource() throws ApiException {
    final UUID postgresSourceDefinitionId = testHarness.getPostgresSourceDefinitionId();
    final JsonNode sourceDbConfig = testHarness.getSourceDbConfig();
    final Map<Object, Object> sourceDbConfigMap = Jsons.object(sourceDbConfig, Map.class);
    sourceDbConfigMap.put("replication_method", ImmutableMap.builder()
        .put("method", CDC_METHOD)
        .put("replication_slot", REPLICATION_SLOT)
        .put("publication", PUBLICATION)
        .build());
    LOGGER.info("final sourceDbConfigMap: {}", sourceDbConfigMap);

    return testHarness.createSource(
        SOURCE_NAME,
        workspaceId,
        postgresSourceDefinitionId,
        Jsons.jsonNode(sourceDbConfigMap));
  }

  private void assertDestinationMatches(List<DestinationCdcRecordMatcher> expectedDestRecordMatchers) throws Exception {
    final List<JsonNode> destRecords = testHarness.retrieveRawDestinationRecords(new SchemaTableNamePair(SCHEMA_NAME, STREAM_NAME));
    if (destRecords.size() != expectedDestRecordMatchers.size()) {
      final String errorMessage = String.format(
          "The number of destination records %d does not match the expected number %d",
          destRecords.size(),
          expectedDestRecordMatchers.size());
      LOGGER.error(errorMessage);
      LOGGER.error("Expected dest record matchers: {}\nActual destination records: {}", expectedDestRecordMatchers, destRecords);
      throw new IllegalStateException(errorMessage);
    }

    for (DestinationCdcRecordMatcher recordMatcher : expectedDestRecordMatchers) {
      final List<JsonNode> matchingDestRecords = destRecords.stream().filter(destRecord -> {
        Map<String, Object> sourceRecordMap = Jsons.object(recordMatcher.sourceRecord, Map.class);
        Map<String, Object> destRecordMap = Jsons.object(destRecord, Map.class);

        boolean sourceRecordValuesMatch = sourceRecordMap.keySet()
            .stream()
            .allMatch(column -> Objects.equals(sourceRecordMap.get(column), destRecordMap.get(column)));

        final Object cdcUpdatedAtValue = destRecordMap.get(CDC_UPDATED_AT_COLUMN);
        // use !isBefore instead of isAfter so that the match still succeeds if the timestamps are equal
        boolean cdcUpdatedAtMatches = cdcUpdatedAtValue != null
            && !Instant.parse(String.valueOf(cdcUpdatedAtValue)).isBefore(recordMatcher.minUpdatedAt);

        final Object cdcDeletedAtValue = destRecordMap.get(CDC_DELETED_AT_COLUMN);
        boolean cdcDeletedAtMatches;
        if (recordMatcher.minDeletedAt.isPresent()) {
          cdcDeletedAtMatches = cdcDeletedAtValue != null
              && !Instant.parse(String.valueOf(cdcDeletedAtValue)).isBefore(recordMatcher.minDeletedAt.get());
        } else {
          cdcDeletedAtMatches = cdcDeletedAtValue == null;
        }

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
