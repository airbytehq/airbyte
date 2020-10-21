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
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.ApiClient;
import io.airbyte.api.client.invoker.ApiException;
import io.airbyte.api.client.model.CheckConnectionRead;
import io.airbyte.api.client.model.CheckConnectionRead.StatusEnum;
import io.airbyte.api.client.model.ConnectionCreate;
import io.airbyte.api.client.model.ConnectionIdRequestBody;
import io.airbyte.api.client.model.ConnectionRead;
import io.airbyte.api.client.model.ConnectionSchedule;
import io.airbyte.api.client.model.ConnectionStatus;
import io.airbyte.api.client.model.ConnectionSyncRead;
import io.airbyte.api.client.model.ConnectionUpdate;
import io.airbyte.api.client.model.DestinationImplementationCreate;
import io.airbyte.api.client.model.DestinationImplementationIdRequestBody;
import io.airbyte.api.client.model.DestinationImplementationRead;
import io.airbyte.api.client.model.SourceImplementationCreate;
import io.airbyte.api.client.model.SourceImplementationIdRequestBody;
import io.airbyte.api.client.model.SourceImplementationRead;
import io.airbyte.api.client.model.SourceSchema;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.persistence.PersistenceConstants;
import io.airbyte.db.DatabaseHelper;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Duration;
import java.util.AbstractMap;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.apache.commons.compress.utils.Lists;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;
import org.jooq.Result;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

@SuppressWarnings("rawtypes")
// We order tests so that independent operations are first and operations dependent on them come
// last
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class AcceptanceTests {

  private PostgreSQLContainer sourcePsql;
  private PostgreSQLContainer targetPsql;

  private final AirbyteApiClient apiClient = new AirbyteApiClient(
      new ApiClient().setScheme("http")
          .setHost("localhost")
          .setPort(8001)
          .setBasePath("/api"));

  private List<UUID> sourceImplIds;
  private List<UUID> connectionIds;
  private List<UUID> destinationImplIds;

  @BeforeEach
  public void init() {
    sourceImplIds = Lists.newArrayList();
    connectionIds = Lists.newArrayList();
    destinationImplIds = Lists.newArrayList();

    sourcePsql = new PostgreSQLContainer();
    targetPsql = new PostgreSQLContainer();
    sourcePsql.start();
    targetPsql.start();

    PostgreSQLContainerHelper.runSqlScript(MountableFile.forClasspathResource("simple_postgres_init.sql"), sourcePsql);
  }

  @AfterEach
  public void tearDown() throws ApiException {
    sourcePsql.stop();
    targetPsql.stop();

    for (UUID sourceImplId : sourceImplIds) {
      deleteSourceImpl(sourceImplId);
    }

    for (UUID connectionId : connectionIds) {
      disableConnection(connectionId);
    }

    for (UUID destinationImplId : destinationImplIds) {
      deleteDestinationImpl(destinationImplId);
    }
  }

  @Test
  @Order(1)
  public void testCreateDestinationImpl() throws ApiException {
    Map<Object, Object> destinationDbConfig = getDestinationDbConfig();
    UUID postgresDestinationSpecId = getPostgresDestinationId();
    UUID workspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;
    String name = "AccTestDestinationDb-" + UUID.randomUUID().toString();

    DestinationImplementationRead destinationImpl = createDestinationImplementation(
        name,
        workspaceId,
        postgresDestinationSpecId,
        getDestinationDbConfig());

    assertEquals(name, destinationImpl.getName());
    assertEquals(postgresDestinationSpecId, destinationImpl.getDestinationId());
    assertEquals(workspaceId, destinationImpl.getWorkspaceId());
    assertEquals(Jsons.jsonNode(destinationDbConfig), destinationImpl.getConnectionConfiguration());
  }

  @Test
  @Order(2)
  public void testDestinationCheckConnection() throws ApiException {
    UUID destinationImplId = createPostgresDestinationImpl().getDestinationImplementationId();

    CheckConnectionRead.StatusEnum checkOperationStatus = apiClient.getDestinationImplementationApi()
        .checkConnectionToDestinationImplementation(
            new DestinationImplementationIdRequestBody().destinationImplementationId(destinationImplId))
        .getStatus();

    assertEquals(StatusEnum.SUCCEEDED, checkOperationStatus);
  }

  @Test
  @Order(3)
  public void testCreateSourceImplementation() throws ApiException {
    String dbName = "acc-test-db";
    UUID postgresSourceId = getPostgresSourceId();
    UUID defaultWorkspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;
    Map<Object, Object> sourceDbConfig = getSourceDbConfig();

    SourceImplementationRead response = createSourceImplementation(
        dbName,
        defaultWorkspaceId,
        postgresSourceId,
        sourceDbConfig);

    assertEquals(dbName, response.getName());
    assertEquals(defaultWorkspaceId, response.getWorkspaceId());
    assertEquals(postgresSourceId, response.getSourceId());
    assertEquals(Jsons.jsonNode(sourceDbConfig), response.getConnectionConfiguration());
  }

  @Test
  @Order(4)
  public void testSourceCheckConnection() throws ApiException {
    UUID sourceImplId = createPostgresSourceImpl().getSourceImplementationId();

    CheckConnectionRead checkConnectionRead = apiClient.getSourceImplementationApi()
        .checkConnectionToSourceImplementation(new SourceImplementationIdRequestBody().sourceImplementationId(sourceImplId));

    assertEquals(StatusEnum.SUCCEEDED, checkConnectionRead.getStatus());
  }

  @Test
  @Order(5)
  public void testDiscoverSourceSchema() throws ApiException, IOException {
    UUID sourceImplementationId = createPostgresSourceImpl().getSourceImplementationId();

    SourceSchema actualSchema = discoverSourceSchema(sourceImplementationId);

    SourceSchema expectedSchema = Jsons.deserialize(MoreResources.readResource("simple_postgres_source_schema.json"), SourceSchema.class);
    assertEquals(expectedSchema, actualSchema);
  }

  @Test
  @Order(6)
  public void testCreateConnection() throws ApiException {
    UUID sourceImplId = createPostgresSourceImpl().getSourceImplementationId();
    SourceSchema schema = discoverSourceSchema(sourceImplId);
    UUID destinationImplId = createPostgresDestinationImpl().getDestinationImplementationId();
    String name = "test-connection-" + UUID.randomUUID().toString();
    ConnectionSchedule schedule = new ConnectionSchedule().timeUnit(MINUTES).units(100L);
    ConnectionCreate.SyncModeEnum syncMode = ConnectionCreate.SyncModeEnum.FULL_REFRESH;

    ConnectionRead createdConnection = createConnection(name, sourceImplId, destinationImplId, schema, schedule, syncMode);

    assertEquals(sourceImplId, createdConnection.getSourceImplementationId());
    assertEquals(destinationImplId, createdConnection.getDestinationImplementationId());
    assertEquals(ConnectionRead.SyncModeEnum.FULL_REFRESH, createdConnection.getSyncMode());
    assertEquals(schema, createdConnection.getSyncSchema());
    assertEquals(schedule, createdConnection.getSchedule());
    assertEquals(name, createdConnection.getName());
  }

  @Test
  @Order(7)
  public void testManualSync() throws ApiException, SQLException {
    String connectionName = "test-connection";
    UUID sourceImplId = createPostgresSourceImpl().getSourceImplementationId();
    UUID destinationImplId = createPostgresDestinationImpl().getDestinationImplementationId();
    SourceSchema schema = discoverSourceSchema(sourceImplId);
    schema.getStreams().forEach(table -> table.getFields().forEach(c -> c.setSelected(true))); // select all fields
    ConnectionSchedule connectionSchedule = new ConnectionSchedule().units(100L).timeUnit(MINUTES);
    ConnectionCreate.SyncModeEnum syncMode = ConnectionCreate.SyncModeEnum.FULL_REFRESH;

    ConnectionRead createdConnection = createConnection(connectionName, sourceImplId, destinationImplId, schema, connectionSchedule, syncMode);

    ConnectionSyncRead connectionSyncRead =
        apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(createdConnection.getConnectionId()));
    assertEquals(ConnectionSyncRead.StatusEnum.SUCCEEDED, connectionSyncRead.getStatus());
    assertSourceAndTargetDbInSync(sourcePsql, targetPsql);
  }

  @Test
  @Order(8)
  public void testScheduledSync() throws InterruptedException, SQLException, ApiException {
    String connectionName = "test-connection";
    UUID sourceImplId = createPostgresSourceImpl().getSourceImplementationId();
    UUID destinationImplId = createPostgresDestinationImpl().getDestinationImplementationId();
    SourceSchema schema = discoverSourceSchema(sourceImplId);
    schema.getStreams().forEach(table -> table.getFields().forEach(c -> c.setSelected(true))); // select all fields
    ConnectionSchedule connectionSchedule = new ConnectionSchedule().units(1L).timeUnit(MINUTES);
    ConnectionCreate.SyncModeEnum syncMode = ConnectionCreate.SyncModeEnum.FULL_REFRESH;

    createConnection(connectionName, sourceImplId, destinationImplId, schema, connectionSchedule, syncMode);

    // When a new connection is created, Airbyte might sync it immediately (before the sync interval).
    // Then it will wait the sync interval.
    Thread.sleep(Duration.of(30, SECONDS).toMillis());
    assertSourceAndTargetDbInSync(sourcePsql, targetPsql);
  }

  private SourceSchema discoverSourceSchema(UUID sourceImplementationId) throws ApiException {
    return apiClient.getSourceImplementationApi().discoverSchemaForSourceImplementation(
        new SourceImplementationIdRequestBody().sourceImplementationId(sourceImplementationId)).getSchema();
  }

  private void assertSourceAndTargetDbInSync(PostgreSQLContainer sourceDb, PostgreSQLContainer targetDb) throws SQLException {
    BasicDataSource sourceDbPool = getConnectionPool(sourceDb);
    BasicDataSource targetDbPool = getConnectionPool(targetDb);

    Set<String> sourceStreams = listStreams(sourceDbPool);
    Set<String> targetStreams = listStreams(targetDbPool);
    assertEquals(sourceStreams, targetStreams);

    for (String table : sourceStreams) {
      assertStreamsEquivalent(sourceDbPool, targetDbPool, table);
    }
  }

  private BasicDataSource getConnectionPool(PostgreSQLContainer db) {
    return DatabaseHelper.getConnectionPool(
        db.getUsername(), db.getPassword(), db.getJdbcUrl());
  }

  private Set<String> listStreams(BasicDataSource connectionPool) throws SQLException {
    return DatabaseHelper.query(
        connectionPool,
        context -> {
          Result<Record> fetch =
              context.fetch(
                  "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'");
          return fetch.stream()
              .map(record -> (String) record.get("tablename"))
              .collect(Collectors.toSet());
        });
  }

  private void assertStreamsEquivalent(
                                       BasicDataSource sourceDbPool,
                                       BasicDataSource targetDbPool,
                                       String table)
      throws SQLException {
    long sourceStreamCount = getStreamCount(sourceDbPool, table);
    long targetStreamCount = getStreamCount(targetDbPool, table);
    assertEquals(sourceStreamCount, targetStreamCount);
    Result<Record> allRecords =
        DatabaseHelper.query(
            sourceDbPool, context -> context.fetch(String.format("SELECT * FROM %s;", table)));
    for (Record sourceStreamRecord : allRecords) {
      assertRecordInStream(sourceStreamRecord, targetDbPool, table);
    }
  }

  /**
   * Verifies that a record in the target table and database exists with the same (and potentially
   * more) fields.
   */
  @SuppressWarnings("unchecked")
  private void assertRecordInStream(Record record, BasicDataSource connectionPool, String tableName)
      throws SQLException {

    Result<Record> presentRecords =
        DatabaseHelper.query(
            connectionPool, context -> context.select().from(tableName).fetch());

    // TODO validate that the correct number of records exists? currently if the same record exists
    // multiple times in the source but once in destination, this returns true.
    final List<JsonNode> matchingRecords = presentRecords
        .stream()
        .map(Record::intoMap)
        .map(r -> r.entrySet().stream().map(e -> {
          if (e.getValue().getClass().equals(org.jooq.JSONB.class)) {
            // jooq needs more configuration to handle jsonb natively. coerce it to a string for now and handle
            // deserializing later.
            return new AbstractMap.SimpleImmutableEntry<>(e.getKey(), e.getValue().toString());
          }
          return e;
        }).collect(Collectors.toMap(Entry::getKey, Entry::getValue)))
        .map(r -> ((String) r.get("data")))
        .map(Jsons::deserialize)
        .collect(Collectors.toList());

    assertTrue(matchingRecords.size() > 0);

    final JsonNode expectedValues = Jsons.jsonNode(record.intoMap());
    assertTrue(matchingRecords.contains(expectedValues));
  }

  @SuppressWarnings("OptionalGetWithoutIsPresent")
  private long getStreamCount(BasicDataSource connectionPool, String tableName) throws SQLException {
    return DatabaseHelper.query(
        connectionPool,
        context -> {
          Result<Record> record =
              context.fetch(String.format("SELECT COUNT(*) FROM %s;", tableName));
          return (long) record.stream().findFirst().get().get(0);
        });
  }

  private ConnectionRead createConnection(String name,
                                          UUID sourceImplId,
                                          UUID destinationImplId,
                                          SourceSchema schema,
                                          ConnectionSchedule schedule,
                                          ConnectionCreate.SyncModeEnum syncMode)
      throws ApiException {
    ConnectionRead connection = apiClient.getConnectionApi().createConnection(
        new ConnectionCreate()
            .status(ConnectionStatus.ACTIVE)
            .sourceImplementationId(sourceImplId)
            .destinationImplementationId(destinationImplId)
            .syncMode(syncMode)
            .syncSchema(schema)
            .schedule(schedule)
            .name(name));
    connectionIds.add(connection.getConnectionId());
    return connection;
  }

  private DestinationImplementationRead createPostgresDestinationImpl() throws ApiException {
    return createDestinationImplementation(
        "AccTestDestination-" + UUID.randomUUID().toString(),
        PersistenceConstants.DEFAULT_WORKSPACE_ID,
        getPostgresDestinationId(),
        getDestinationDbConfig());
  }

  private Map<Object, Object> getDestinationDbConfig() {
    return ImmutableMap.builder()
        .put("host", targetPsql.getHost())
        .put("username", targetPsql.getUsername())
        .put("password", targetPsql.getPassword())
        .put("schema", "public")
        .put("port", targetPsql.getFirstMappedPort())
        .put("database", targetPsql.getDatabaseName())
        .build();
  }

  private DestinationImplementationRead createDestinationImplementation(String name,
                                                                        UUID workspaceId,
                                                                        UUID destinationId,
                                                                        Map<Object, Object> destinationConfig)
      throws ApiException {
    DestinationImplementationRead destinationImplementation =
        apiClient.getDestinationImplementationApi().createDestinationImplementation(new DestinationImplementationCreate()
            .name(name)
            .connectionConfiguration(Jsons.jsonNode(destinationConfig))
            .workspaceId(workspaceId)
            .destinationId(destinationId));
    destinationImplIds.add(destinationImplementation.getDestinationImplementationId());
    return destinationImplementation;
  }

  private UUID getPostgresDestinationId() throws ApiException {
    return apiClient.getDestinationApi().listDestinations().getDestinations()
        .stream()
        .filter(dr -> dr.getName().toLowerCase().equals("postgres"))
        .findFirst()
        .orElseThrow()
        .getDestinationId();
  }

  private Map<Object, Object> getSourceDbConfig() {
    Map<Object, Object> dbConfig = new HashMap<>();
    dbConfig.put("host", sourcePsql.getHost());
    dbConfig.put("password", sourcePsql.getPassword());
    dbConfig.put("port", sourcePsql.getFirstMappedPort());
    dbConfig.put("dbname", sourcePsql.getDatabaseName());
    dbConfig.put("user", sourcePsql.getUsername());
    return dbConfig;
  }

  private SourceImplementationRead createPostgresSourceImpl() throws ApiException {
    return createSourceImplementation(
        "acceptanceTestDb-" + UUID.randomUUID().toString(),
        PersistenceConstants.DEFAULT_WORKSPACE_ID,
        getPostgresSourceId(),
        getSourceDbConfig());
  }

  private SourceImplementationRead createSourceImplementation(String name, UUID workspaceId, UUID sourceId, Map<Object, Object> sourceConfig)
      throws ApiException {
    SourceImplementationRead sourceImplementation = apiClient.getSourceImplementationApi().createSourceImplementation(new SourceImplementationCreate()
        .name(name)
        .sourceId(sourceId)
        .workspaceId(workspaceId)
        .connectionConfiguration(Jsons.jsonNode(sourceConfig)));
    sourceImplIds.add(sourceImplementation.getSourceImplementationId());
    return sourceImplementation;
  }

  private UUID getPostgresSourceId() throws ApiException {
    return apiClient.getSourceApi().listSources().getSources()
        .stream()
        .filter(sourceRead -> sourceRead.getName().toLowerCase().equals("postgres"))
        .findFirst()
        .orElseThrow()
        .getSourceId();
  }

  private void deleteSourceImpl(UUID sourceImplId) throws ApiException {
    apiClient.getSourceImplementationApi().deleteSourceImplementation(new SourceImplementationIdRequestBody().sourceImplementationId(sourceImplId));
  }

  private void disableConnection(UUID connectionId) throws ApiException {
    ConnectionRead connection = apiClient.getConnectionApi().getConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    ConnectionUpdate connectionUpdate =
        new ConnectionUpdate()
            .connectionId(connectionId)
            .status(ConnectionStatus.DEPRECATED)
            .schedule(connection.getSchedule())
            .syncSchema(connection.getSyncSchema());
    apiClient.getConnectionApi().updateConnection(connectionUpdate);
  }

  private void deleteDestinationImpl(UUID destinationImplId) throws ApiException {
    apiClient.getDestinationImplementationApi()
        .deleteDestinationImplementation(new DestinationImplementationIdRequestBody().destinationImplementationId(destinationImplId));
  }

}
