/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.test.acceptance;

import static io.airbyte.api.client.model.ConnectionSchedule.TimeUnitEnum.MINUTES;
import static java.time.temporal.ChronoUnit.SECONDS;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.io.Files;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.JobsApi;
import io.airbyte.api.client.invoker.ApiClient;
import io.airbyte.api.client.invoker.ApiException;
import io.airbyte.api.client.model.AirbyteCatalog;
import io.airbyte.api.client.model.AirbyteStream;
import io.airbyte.api.client.model.AirbyteStreamAndConfiguration;
import io.airbyte.api.client.model.AirbyteStreamConfiguration;
import io.airbyte.api.client.model.CheckConnectionRead;
import io.airbyte.api.client.model.ConnectionCreate;
import io.airbyte.api.client.model.ConnectionIdRequestBody;
import io.airbyte.api.client.model.ConnectionRead;
import io.airbyte.api.client.model.ConnectionSchedule;
import io.airbyte.api.client.model.ConnectionStatus;
import io.airbyte.api.client.model.ConnectionUpdate;
import io.airbyte.api.client.model.DataType;
import io.airbyte.api.client.model.DestinationCreate;
import io.airbyte.api.client.model.DestinationDefinitionIdRequestBody;
import io.airbyte.api.client.model.DestinationDefinitionSpecificationRead;
import io.airbyte.api.client.model.DestinationIdRequestBody;
import io.airbyte.api.client.model.DestinationRead;
import io.airbyte.api.client.model.DestinationSyncMode;
import io.airbyte.api.client.model.JobIdRequestBody;
import io.airbyte.api.client.model.JobInfoRead;
import io.airbyte.api.client.model.JobRead;
import io.airbyte.api.client.model.JobStatus;
import io.airbyte.api.client.model.LogType;
import io.airbyte.api.client.model.LogsRequestBody;
import io.airbyte.api.client.model.SourceCreate;
import io.airbyte.api.client.model.SourceDefinitionIdRequestBody;
import io.airbyte.api.client.model.SourceDefinitionSpecificationRead;
import io.airbyte.api.client.model.SourceIdRequestBody;
import io.airbyte.api.client.model.SourceRead;
import io.airbyte.api.client.model.SyncMode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.persistence.PersistenceConstants;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.io.IOException;
import java.net.Inet4Address;
import java.net.UnknownHostException;
import java.nio.charset.Charset;
import java.sql.SQLException;
import java.time.Duration;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.Result;
import org.junit.Assume;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

@SuppressWarnings("rawtypes")
// We order tests such that earlier tests test more basic behavior that is relied upon in later
// tests.
// e.g. We test that we can create a destination before we test whether we can sync data to it.
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class AcceptanceTests {

  // Skip networking related failures on kube using this flag
  private static final boolean IS_KUBE = System.getenv().containsKey("KUBE");

  private static final String OUTPUT_NAMESPACE = "output_";
  private static final String TABLE_NAME = "id_and_name";
  private static final String STREAM_NAME = "public." + TABLE_NAME;
  private static final String COLUMN_ID = "id";
  private static final String COLUMN_NAME = "name";
  private static final String COLUMN_NAME_DATA = "_airbyte_data";
  private static final String SOURCE_USERNAME = "sourceusername";
  private static final String SOURCE_PASSWORD = "hunter2";

  private static PostgreSQLContainer sourcePsql;
  private static PostgreSQLContainer destinationPsql;

  private final AirbyteApiClient apiClient = new AirbyteApiClient(
      new ApiClient().setScheme("http")
          .setHost("localhost")
          .setPort(8001)
          .setBasePath("/api"));

  private List<UUID> sourceIds;
  private List<UUID> connectionIds;
  private List<UUID> destinationIds;

  @BeforeAll
  public static void init() {
    sourcePsql = new PostgreSQLContainer("postgres:13-alpine")
        .withUsername(SOURCE_USERNAME)
        .withPassword(SOURCE_PASSWORD);
    sourcePsql.start();
    destinationPsql = new PostgreSQLContainer("postgres:13-alpine");
    destinationPsql.start();
  }

  @AfterAll
  public static void end() {
    sourcePsql.stop();
  }

  @BeforeEach
  public void setup() {
    sourceIds = Lists.newArrayList();
    connectionIds = Lists.newArrayList();
    destinationIds = Lists.newArrayList();

    // seed database.
    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("postgres_init.sql"), sourcePsql);
  }

  @AfterEach
  public void tearDown() throws ApiException, SQLException {
    clearDbData(sourcePsql);

    for (UUID sourceId : sourceIds) {
      deleteSource(sourceId);
    }

    for (UUID connectionId : connectionIds) {
      disableConnection(connectionId);
    }

    for (UUID destinationId : destinationIds) {
      deleteDestination(destinationId);
    }
  }

  @Test
  @Order(-1)
  public void testGetDestinationSpec() throws ApiException {
    final UUID destinationDefinitionId = getDestinationDefId();
    DestinationDefinitionSpecificationRead spec = apiClient.getDestinationDefinitionSpecificationApi()
        .getDestinationDefinitionSpecification(new DestinationDefinitionIdRequestBody().destinationDefinitionId(destinationDefinitionId));
    assertEquals(destinationDefinitionId, spec.getDestinationDefinitionId());
    assertNotNull(spec.getConnectionSpecification());
  }

  @Test
  @Order(0)
  public void testGetSourceSpec() throws ApiException {
    final UUID sourceDefId = getPostgresSourceDefinitionId();
    SourceDefinitionSpecificationRead spec = apiClient.getSourceDefinitionSpecificationApi()
        .getSourceDefinitionSpecification(new SourceDefinitionIdRequestBody().sourceDefinitionId(sourceDefId));
    assertEquals(sourceDefId, spec.getSourceDefinitionId());
    assertNotNull(spec.getConnectionSpecification());
  }

  @Test
  @Order(1)
  public void testCreateDestination() throws ApiException {
    final UUID destinationDefId = getDestinationDefId();
    final JsonNode destinationConfig = getDestinationDbConfig();
    final UUID workspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;
    final String name = "AccTestDestinationDb-" + UUID.randomUUID().toString();

    final DestinationRead createdDestination = createDestination(
        name,
        workspaceId,
        destinationDefId,
        destinationConfig);

    assertEquals(name, createdDestination.getName());
    assertEquals(destinationDefId, createdDestination.getDestinationDefinitionId());
    assertEquals(workspaceId, createdDestination.getWorkspaceId());
    assertEquals(getDestinationDbConfigWithHiddenPassword(), createdDestination.getConnectionConfiguration());
  }

  @Test
  @Order(2)
  public void testDestinationCheckConnection() throws ApiException {
    final UUID destinationId = createDestination().getDestinationId();

    final CheckConnectionRead.StatusEnum checkOperationStatus = apiClient.getDestinationApi()
        .checkConnectionToDestination(new DestinationIdRequestBody().destinationId(destinationId))
        .getStatus();

    assertEquals(CheckConnectionRead.StatusEnum.SUCCEEDED, checkOperationStatus);
  }

  @Test
  @Order(3)
  public void testCreateSource() throws ApiException, IOException {
    final String dbName = "acc-test-db";
    final UUID postgresSourceDefinitionId = getPostgresSourceDefinitionId();
    final UUID defaultWorkspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;
    final JsonNode sourceDbConfig = getSourceDbConfig();

    final SourceRead response = createSource(
        dbName,
        defaultWorkspaceId,
        postgresSourceDefinitionId,
        sourceDbConfig);

    final JsonNode expectedConfig = Jsons.jsonNode(sourceDbConfig);
    // expect replacement of secret with magic string.
    ((ObjectNode) expectedConfig).put("password", "**********");
    assertEquals(dbName, response.getName());
    assertEquals(defaultWorkspaceId, response.getWorkspaceId());
    assertEquals(postgresSourceDefinitionId, response.getSourceDefinitionId());
    assertEquals(expectedConfig, response.getConnectionConfiguration());
  }

  @Test
  @Order(4)
  public void testSourceCheckConnection() throws ApiException {
    final UUID sourceId = createPostgresSource().getSourceId();

    final CheckConnectionRead checkConnectionRead = apiClient.getSourceApi().checkConnectionToSource(new SourceIdRequestBody().sourceId(sourceId));

    assertEquals(
        CheckConnectionRead.StatusEnum.SUCCEEDED,
        checkConnectionRead.getStatus(),
        checkConnectionRead.getMessage());
  }

  @Test
  @Order(5)
  public void testDiscoverSourceSchema() throws ApiException {
    final UUID sourceId = createPostgresSource().getSourceId();

    final AirbyteCatalog actual = discoverSourceSchema(sourceId);

    final Map<String, Map<String, DataType>> fields = ImmutableMap.of(
        COLUMN_ID, ImmutableMap.of("type", DataType.NUMBER),
        COLUMN_NAME, ImmutableMap.of("type", DataType.STRING));
    final JsonNode jsonSchema = Jsons.jsonNode(ImmutableMap.builder()
        .put("type", "object")
        .put("properties", fields)
        .build());
    final AirbyteStream stream = new AirbyteStream()
        .name(STREAM_NAME)
        .jsonSchema(jsonSchema)
        .defaultCursorField(Collections.emptyList())
        .sourceDefinedPrimaryKey(Collections.emptyList())
        .supportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    final AirbyteStreamConfiguration streamConfig = new AirbyteStreamConfiguration()
        .syncMode(SyncMode.FULL_REFRESH)
        .cursorField(Collections.emptyList())
        .destinationSyncMode(DestinationSyncMode.APPEND)
        .primaryKey(Collections.emptyList())
        .aliasName(STREAM_NAME.replace(".", "_"))
        .selected(true);
    final AirbyteCatalog expected = new AirbyteCatalog()
        .streams(Lists.newArrayList(new AirbyteStreamAndConfiguration()
            .stream(stream)
            .config(streamConfig)));

    assertEquals(expected, actual);
  }

  @Test
  @Order(6)
  public void testCreateConnection() throws ApiException {
    final UUID sourceId = createPostgresSource().getSourceId();
    final AirbyteCatalog catalog = discoverSourceSchema(sourceId);
    final UUID destinationId = createDestination().getDestinationId();
    final String name = "test-connection-" + UUID.randomUUID().toString();
    final ConnectionSchedule schedule = new ConnectionSchedule().timeUnit(MINUTES).units(100L);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final ConnectionRead createdConnection = createConnection(name, sourceId, destinationId, catalog, schedule, syncMode);

    assertEquals(sourceId, createdConnection.getSourceId());
    assertEquals(destinationId, createdConnection.getDestinationId());
    assertEquals(catalog, createdConnection.getSyncCatalog());
    assertEquals(schedule, createdConnection.getSchedule());
    assertEquals(name, createdConnection.getName());
  }

  @Test
  @Order(7)
  public void testManualSync() throws Exception {
    final String connectionName = "test-connection";
    final UUID sourceId = createPostgresSource().getSourceId();
    final UUID destinationId = createDestination().getDestinationId();
    final AirbyteCatalog catalog = discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));
    final UUID connectionId = createConnection(connectionName, sourceId, destinationId, catalog, null, syncMode).getConnectionId();

    final JobInfoRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead.getJob());
    assertSourceAndTargetDbInSync(sourcePsql, false);
  }

  @Test
  @Order(8)
  public void testIncrementalSync() throws Exception {
    final String connectionName = "test-connection";
    final UUID sourceId = createPostgresSource().getSourceId();
    final UUID destinationId = createDestination().getDestinationId();
    final AirbyteCatalog catalog = discoverSourceSchema(sourceId);
    final AirbyteStream stream = catalog.getStreams().get(0).getStream();

    assertEquals(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL),
        stream.getSupportedSyncModes());
    // instead of assertFalse to avoid NPE from unboxed.
    assertNull(stream.getSourceDefinedCursor());
    assertTrue(stream.getDefaultCursorField().isEmpty());
    assertTrue(stream.getSourceDefinedPrimaryKey().isEmpty());

    final SyncMode syncMode = SyncMode.INCREMENTAL;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.APPEND;
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(syncMode)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(destinationSyncMode));
    final UUID connectionId = createConnection(connectionName, sourceId, destinationId, catalog, null, syncMode).getConnectionId();

    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());

    assertSourceAndTargetDbInSync(sourcePsql, false);

    // add new records and run again.
    final Database source = getDatabase(sourcePsql);
    // get contents of source before mutating records.
    final List<JsonNode> expectedRecords = retrieveSourceRecords(source, STREAM_NAME);
    expectedRecords.add(Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 6).put(COLUMN_NAME, "geralt").build()));
    // add a new record
    source.query(ctx -> ctx.execute("INSERT INTO id_and_name(id, name) VALUES(6, 'geralt')"));
    // mutate a record that was already synced with out updating its cursor value. if we are actually
    // full refreshing, this record will appear in the output and cause the test to fail. if we are,
    // correctly, doing incremental, we will not find this value in the destination.
    source.query(ctx -> ctx.execute("UPDATE id_and_name SET name='yennefer' WHERE id=2"));
    source.close();

    final JobInfoRead connectionSyncRead2 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());
    assertRawDestinationContains(expectedRecords, STREAM_NAME);

    // reset back to no data.
    final JobInfoRead jobInfoRead = apiClient.getConnectionApi().resetConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), jobInfoRead.getJob());
    assertRawDestinationContains(Collections.emptyList(), STREAM_NAME);

    // sync one more time. verify it is the equivalent of a full refresh.
    final JobInfoRead connectionSyncRead3 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead3.getJob());
    assertSourceAndTargetDbInSync(sourcePsql, false);
  }

  @Test
  @Order(9)
  public void testScheduledSync() throws Exception {
    // skip with Kube. HTTP client error with port forwarding
    Assume.assumeFalse(IS_KUBE);

    final String connectionName = "test-connection";
    final UUID sourceId = createPostgresSource().getSourceId();
    final UUID destinationId = createDestination().getDestinationId();
    final AirbyteCatalog catalog = discoverSourceSchema(sourceId);

    final ConnectionSchedule connectionSchedule = new ConnectionSchedule().units(1L).timeUnit(MINUTES);
    final SyncMode syncMode = SyncMode.FULL_REFRESH;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.OVERWRITE;
    catalog.getStreams().forEach(s -> s.getConfig().syncMode(syncMode).destinationSyncMode(destinationSyncMode));

    createConnection(connectionName, sourceId, destinationId, catalog, connectionSchedule, syncMode);

    // When a new connection is created, Airbyte might sync it immediately (before the sync interval).
    // Then it will wait the sync interval.
    Thread.sleep(Duration.of(30, SECONDS).toMillis());
    assertSourceAndTargetDbInSync(sourcePsql, false);
  }

  @Test
  @Order(10)
  public void testIncrementalDedupSync() throws Exception {
    final String connectionName = "test-connection";
    final UUID sourceId = createPostgresSource().getSourceId();
    final UUID destinationId = createDestination().getDestinationId();
    final AirbyteCatalog catalog = discoverSourceSchema(sourceId);
    final SyncMode syncMode = SyncMode.INCREMENTAL;
    final DestinationSyncMode destinationSyncMode = DestinationSyncMode.APPEND_DEDUP;
    catalog.getStreams().forEach(s -> s.getConfig()
        .syncMode(syncMode)
        .cursorField(List.of(COLUMN_ID))
        .destinationSyncMode(destinationSyncMode)
        .primaryKey(List.of(List.of(COLUMN_NAME))));
    final UUID connectionId = createConnection(connectionName, sourceId, destinationId, catalog, null, syncMode).getConnectionId();

    // sync from start
    final JobInfoRead connectionSyncRead1 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead1.getJob());

    assertSourceAndTargetDbInSync(sourcePsql, true);

    // add new records and run again.
    final Database source = getDatabase(sourcePsql);
    final List<JsonNode> expectedRawRecords = retrieveSourceRecords(source, STREAM_NAME);
    expectedRawRecords.add(Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 6).put(COLUMN_NAME, "sherif").build()));
    expectedRawRecords.add(Jsons.jsonNode(ImmutableMap.builder().put(COLUMN_ID, 7).put(COLUMN_NAME, "chris").build()));
    source.query(ctx -> ctx.execute("UPDATE id_and_name SET id=6 WHERE name='sherif'"));
    source.query(ctx -> ctx.execute("INSERT INTO id_and_name(id, name) VALUES(7, 'chris')"));
    // retrieve latest snapshot of source records after modifications; the deduplicated table in
    // destination should mirror this latest state of records
    final List<JsonNode> expectedNormalizedRecords = retrieveSourceRecords(source, STREAM_NAME);
    source.close();

    final JobInfoRead connectionSyncRead2 = apiClient.getConnectionApi()
        .syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    waitForSuccessfulJob(apiClient.getJobsApi(), connectionSyncRead2.getJob());

    assertRawDestinationContains(expectedRawRecords, STREAM_NAME);
    assertNormalizedDestinationContains(expectedNormalizedRecords);
  }

  @Test
  @Order(11)
  public void testRedactionOfSensitiveRequestBodies() throws Exception {
    // check that the source password is not present in the logs
    final List<String> serverLogLines = Files.readLines(
        apiClient.getLogsApi().getLogs(new LogsRequestBody().logType(LogType.SERVER)), Charset.defaultCharset());

    assertTrue(serverLogLines.size() > 0);

    boolean hasRedacted = false;

    for (String line : serverLogLines) {
      assertFalse(line.contains(SOURCE_PASSWORD));

      if (line.contains("REDACTED")) {
        hasRedacted = true;
      }
    }

    assertTrue(hasRedacted);
  }

  private AirbyteCatalog discoverSourceSchema(UUID sourceId) throws ApiException {
    return apiClient.getSourceApi().discoverSchemaForSource(new SourceIdRequestBody().sourceId(sourceId)).getCatalog();
  }

  private void assertSourceAndTargetDbInSync(PostgreSQLContainer sourceDb, boolean withScdTable) throws Exception {
    final Database source = getDatabase(sourceDb);

    final Set<String> sourceStreams = listStreams(source);
    final Set<String> sourceStreamsWithRawPrefix = sourceStreams.stream().flatMap(x -> {
      final String cleanedNameStream = x.replace(".", "_");
      if (withScdTable) {
        return List.of(
            String.format("_airbyte_raw_%s%s", OUTPUT_NAMESPACE, cleanedNameStream),
            String.format("%s%s_scd", OUTPUT_NAMESPACE, cleanedNameStream),
            String.format("%s%s", OUTPUT_NAMESPACE, cleanedNameStream)).stream();
      } else {
        return List.of(
            String.format("_airbyte_raw_%s%s", OUTPUT_NAMESPACE, cleanedNameStream),
            String.format("%s%s", OUTPUT_NAMESPACE, cleanedNameStream)).stream();
      }
    }).collect(Collectors.toSet());
    final Database destination = getDatabase(destinationPsql);
    final Set<String> destinationStreams = listDestinationStreams(destination);
    assertEquals(sourceStreamsWithRawPrefix, destinationStreams,
        String.format("streams did not match.\n source stream names: %s\n destination stream names: %s\n", sourceStreams, destinationStreams));

    for (String table : sourceStreams) {
      assertStreamsEquivalent(source, table);
    }
  }

  private Database getDatabase(PostgreSQLContainer db) {
    return Databases.createPostgresDatabase(db.getUsername(), db.getPassword(), db.getJdbcUrl());
  }

  private Set<String> listStreams(Database database) throws SQLException {
    return database.query(
        context -> {
          Result<Record> fetch =
              context.fetch(
                  "SELECT tablename, schemaname FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'");
          return fetch.stream()
              .map(record -> {
                final String schemaName = (String) record.get("schemaname");
                final String tableName = (String) record.get("tablename");
                return schemaName + "." + tableName;
              })
              .collect(Collectors.toSet());
        });
  }

  private Set<String> listDestinationStreams(Database destination) throws SQLException {
    return destination.query(ctx -> ctx.resultQuery("SELECT table_name\n" +
        "FROM information_schema.tables\n" +
        "WHERE table_schema = 'public'\n" +
        "ORDER BY table_name;"))
        .stream()
        .map(x -> x.get("table_name", String.class))
        .collect(Collectors.toSet());
  }

  private void assertRawDestinationContains(List<JsonNode> sourceRecords, String streamName) throws Exception {
    final Set<JsonNode> destinationRecords = new HashSet<>(retrieveDestinationRecords(streamName));

    assertEquals(sourceRecords.size(), destinationRecords.size(),
        String.format("destination contains: %s record. source contains: %s", sourceRecords.size(), destinationRecords.size()));

    for (JsonNode sourceStreamRecord : sourceRecords) {
      assertTrue(destinationRecords.contains(sourceStreamRecord),
          String.format("destination does not contain record:\n %s \n destination contains:\n %s\n", sourceStreamRecord, destinationRecords));
    }
  }

  private void assertNormalizedDestinationContains(final List<JsonNode> sourceRecords) throws Exception {
    final Database destination = getDatabase(destinationPsql);
    final String finalDestinationTable = String.format("%s%s", OUTPUT_NAMESPACE, STREAM_NAME.replace(".", "_"));
    final List<JsonNode> destinationRecords = retrieveSourceRecords(destination, finalDestinationTable);

    assertEquals(sourceRecords.size(), destinationRecords.size(),
        String.format("destination contains: %s record. source contains: %s", sourceRecords.size(), destinationRecords.size()));

    for (JsonNode sourceStreamRecord : sourceRecords) {
      assertTrue(
          destinationRecords.stream()
              .anyMatch(r -> r.get(COLUMN_NAME).asText().equals(sourceStreamRecord.get(COLUMN_NAME).asText())
                  && r.get(COLUMN_ID).asInt() == sourceStreamRecord.get(COLUMN_ID).asInt()),
          String.format("destination does not contain record:\n %s \n destination contains:\n %s\n", sourceStreamRecord, destinationRecords));
    }
  }

  private void assertStreamsEquivalent(Database source, String table) throws Exception {
    final List<JsonNode> sourceRecords = retrieveSourceRecords(source, table);
    assertRawDestinationContains(sourceRecords, table);
  }

  private ConnectionRead createConnection(String name,
                                          UUID sourceId,
                                          UUID destinationId,
                                          AirbyteCatalog catalog,
                                          ConnectionSchedule schedule,
                                          SyncMode syncMode)
      throws ApiException {
    final ConnectionRead connection = apiClient.getConnectionApi().createConnection(
        new ConnectionCreate()
            .status(ConnectionStatus.ACTIVE)
            .sourceId(sourceId)
            .destinationId(destinationId)
            .syncCatalog(catalog)
            .schedule(schedule)
            .name(name)
            .prefix(OUTPUT_NAMESPACE));
    connectionIds.add(connection.getConnectionId());
    return connection;
  }

  private DestinationRead createDestination() throws ApiException {
    return createDestination(
        "AccTestDestination-" + UUID.randomUUID().toString(),
        PersistenceConstants.DEFAULT_WORKSPACE_ID,
        getDestinationDefId(),
        getDestinationDbConfig());
  }

  private DestinationRead createDestination(String name, UUID workspaceId, UUID destinationId, JsonNode destinationConfig) throws ApiException {
    final DestinationRead destination =
        apiClient.getDestinationApi().createDestination(new DestinationCreate()
            .name(name)
            .connectionConfiguration(Jsons.jsonNode(destinationConfig))
            .workspaceId(workspaceId)
            .destinationDefinitionId(destinationId));
    destinationIds.add(destination.getDestinationId());
    return destination;
  }

  private UUID getDestinationDefId() throws ApiException {
    return apiClient.getDestinationDefinitionApi().listDestinationDefinitions().getDestinationDefinitions()
        .stream()
        .filter(dr -> dr.getName().toLowerCase().contains("postgres"))
        .findFirst()
        .orElseThrow()
        .getDestinationDefinitionId();
  }

  private List<JsonNode> retrieveSourceRecords(Database database, String table) throws SQLException {
    final String cleanedName = table.replace("public.", "");
    return database.query(context -> context.fetch(String.format("SELECT * FROM \"%s\";", cleanedName)))
        .stream()
        .map(Record::intoMap)
        .map(Jsons::jsonNode)
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveDestinationRecords(Database database, String table) throws SQLException {
    return database.query(context -> context.fetch(String.format("SELECT * FROM \"%s\";", table)))
        .stream()
        .map(Record::intoMap)
        .map(r -> r.get(COLUMN_NAME_DATA))
        .map(f -> (JSONB) f)
        .map(JSONB::data)
        .map(Jsons::deserialize)
        .map(Jsons::jsonNode)
        .collect(Collectors.toList());
  }

  private List<JsonNode> retrieveDestinationRecords(String streamName) throws Exception {
    Database destination = getDatabase(destinationPsql);
    Set<String> destinationStreams = listDestinationStreams(destination);
    final String rawStreamName = String.format("_airbyte_raw_%s%s", OUTPUT_NAMESPACE, streamName.replace(".", "_"));
    assertTrue(destinationStreams.contains(rawStreamName), "can't find a non-normalized version (raw) of " + streamName);

    return retrieveDestinationRecords(destination, rawStreamName);
  }

  private JsonNode getSourceDbConfig() {
    return getDbConfig(sourcePsql);
  }

  private JsonNode getDestinationDbConfig() {
    return getDbConfig(destinationPsql, false, true, true);
  }

  private JsonNode getDestinationDbConfigWithHiddenPassword() {
    return getDbConfig(destinationPsql, true, true, true);
  }

  private JsonNode getDbConfig(PostgreSQLContainer psql) {
    return getDbConfig(psql, false, false, false);
  }

  private JsonNode getDbConfig(PostgreSQLContainer psql, boolean hiddenPassword, boolean withSchema, boolean withNormalization) {
    try {
      final Map<Object, Object> dbConfig = new HashMap<>();

      // necessary for minikube tests on Github Actions instead of psql.getHost()
      dbConfig.put("host", Inet4Address.getLocalHost().getHostAddress());

      if (hiddenPassword) {
        dbConfig.put("password", "**********");
      } else {
        dbConfig.put("password", psql.getPassword());
      }

      dbConfig.put("port", psql.getFirstMappedPort());
      dbConfig.put("database", psql.getDatabaseName());
      dbConfig.put("username", psql.getUsername());

      if (withSchema) {
        dbConfig.put("schema", "public");
      }

      if (withNormalization) {
        dbConfig.put("basic_normalization", true);
      }

      return Jsons.jsonNode(dbConfig);
    } catch (UnknownHostException e) {
      throw new RuntimeException(e);
    }
  }

  private SourceRead createPostgresSource() throws ApiException {
    return createSource(
        "acceptanceTestDb-" + UUID.randomUUID().toString(),
        PersistenceConstants.DEFAULT_WORKSPACE_ID,
        getPostgresSourceDefinitionId(),
        getSourceDbConfig());
  }

  private SourceRead createSource(String name, UUID workspaceId, UUID sourceDefId, JsonNode sourceConfig) throws ApiException {
    final SourceRead source = apiClient.getSourceApi().createSource(new SourceCreate()
        .name(name)
        .sourceDefinitionId(sourceDefId)
        .workspaceId(workspaceId)
        .connectionConfiguration(sourceConfig));
    sourceIds.add(source.getSourceId());
    return source;
  }

  private UUID getPostgresSourceDefinitionId() throws ApiException {
    return apiClient.getSourceDefinitionApi().listSourceDefinitions().getSourceDefinitions()
        .stream()
        .filter(sourceRead -> sourceRead.getName().toLowerCase().equals("postgres"))
        .findFirst()
        .orElseThrow()
        .getSourceDefinitionId();
  }

  private void clearDbData(PostgreSQLContainer db) throws SQLException {
    final Database database = getDatabase(db);
    final Set<String> tableNames = listStreams(database);
    for (final String tableName : tableNames) {
      database.query(context -> context.execute(String.format("DELETE FROM %s", tableName)));
    }
  }

  private void deleteSource(UUID sourceId) throws ApiException {
    apiClient.getSourceApi().deleteSource(new SourceIdRequestBody().sourceId(sourceId));
  }

  private void disableConnection(UUID connectionId) throws ApiException {
    final ConnectionRead connection = apiClient.getConnectionApi().getConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    final ConnectionUpdate connectionUpdate =
        new ConnectionUpdate()
            .prefix(connection.getPrefix())
            .connectionId(connectionId)
            .status(ConnectionStatus.DEPRECATED)
            .schedule(connection.getSchedule())
            .syncCatalog(connection.getSyncCatalog());
    apiClient.getConnectionApi().updateConnection(connectionUpdate);
  }

  private void deleteDestination(UUID destinationId) throws ApiException {
    apiClient.getDestinationApi().deleteDestination(new DestinationIdRequestBody().destinationId(destinationId));
  }

  private static void waitForSuccessfulJob(JobsApi jobsApi, JobRead originalJob) throws InterruptedException, ApiException {
    JobRead job = originalJob;
    int count = 0;
    while (count < 60 && (job.getStatus() == JobStatus.PENDING || job.getStatus() == JobStatus.RUNNING)) {
      Thread.sleep(1000);
      count++;

      job = jobsApi.getJobInfo(new JobIdRequestBody().id(job.getId())).getJob();
    }
    assertEquals(JobStatus.SUCCEEDED, job.getStatus());
  }

}
