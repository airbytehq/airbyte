/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.test.acceptance;

import static io.dataline.api.client.model.ConnectionSchedule.TimeUnitEnum.MINUTES;
import static java.time.temporal.ChronoUnit.SECONDS;
import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.collect.ImmutableMap;
import io.dataline.api.client.DatalineApiClient;
import io.dataline.api.client.invoker.ApiClient;
import io.dataline.api.client.invoker.ApiException;
import io.dataline.api.client.model.CheckConnectionRead;
import io.dataline.api.client.model.ConnectionCreate;
import io.dataline.api.client.model.ConnectionIdRequestBody;
import io.dataline.api.client.model.ConnectionRead;
import io.dataline.api.client.model.ConnectionSchedule;
import io.dataline.api.client.model.ConnectionStatus;
import io.dataline.api.client.model.ConnectionSyncRead;
import io.dataline.api.client.model.ConnectionUpdate;
import io.dataline.api.client.model.DestinationIdRequestBody;
import io.dataline.api.client.model.DestinationImplementationCreate;
import io.dataline.api.client.model.DestinationImplementationIdRequestBody;
import io.dataline.api.client.model.DestinationImplementationRead;
import io.dataline.api.client.model.SourceIdRequestBody;
import io.dataline.api.client.model.SourceImplementationCreate;
import io.dataline.api.client.model.SourceImplementationIdRequestBody;
import io.dataline.api.client.model.SourceImplementationRead;
import io.dataline.api.client.model.SourceSchema;
import io.dataline.api.client.model.SourceSpecificationRead;
import io.dataline.commons.json.Jsons;
import io.dataline.commons.resources.MoreResources;
import io.dataline.config.persistence.PersistenceConstants;
import io.dataline.db.DatabaseHelper;
import io.dataline.test.utils.PostgreSQLContainerHelper;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Duration;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.apache.commons.compress.utils.Lists;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Condition;
import org.jooq.Field;
import org.jooq.Record;
import org.jooq.Result;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

@SuppressWarnings("rawtypes")
// We order tests so that independent operations are first and operations dependent on them come
// last
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
public class AcceptanceTests {

  private static final Logger LOGGER = LoggerFactory.getLogger(AcceptanceTests.class);
  private PostgreSQLContainer sourcePsql;
  private PostgreSQLContainer targetPsql;

  private DatalineApiClient apiClient = new DatalineApiClient(
      new ApiClient().setScheme("http")
          .setHost("localhost")
          .setPort(8001)
          .setBasePath("/api"));

  private List<UUID> sourceImplIds;
  private List<UUID> connectionIds;

  @BeforeEach
  public void init() throws IOException, InterruptedException {
    sourceImplIds = Lists.newArrayList();
    connectionIds = Lists.newArrayList();

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

    // TODO disable destination once the API exposes the functionality.
  }

  @Test
  @Order(1)
  public void testCreateDestinationImpl() throws ApiException {
    Map<Object, Object> destinationDbConfig = getDestinationDbConfig();
    UUID postgresDestinationSpecId = getPostgresDestinationSpecId();
    UUID workspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;
    String name = "AccTestDestinationDb-" + UUID.randomUUID().toString();

    DestinationImplementationRead destinationImpl = createDestinationImplementation(
        name,
        workspaceId,
        postgresDestinationSpecId,
        getDestinationDbConfig());

    assertEquals(name, destinationImpl.getName());
    assertEquals(postgresDestinationSpecId, destinationImpl.getDestinationSpecificationId());
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

    assertEquals(CheckConnectionRead.StatusEnum.SUCCESS, checkOperationStatus);
  }

  @Test
  @Order(3)
  public void testCreateSourceImplementation() throws ApiException {
    String dbName = "acc-test-db";
    UUID postgresSourceSpecId = getPostgresSourceSpecId();
    UUID defaultWorkspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;
    Map<Object, Object> sourceDbConfig = getSourceDbConfig();

    SourceImplementationRead response = createSourceImplementation(
        dbName,
        defaultWorkspaceId,
        postgresSourceSpecId,
        sourceDbConfig);

    assertEquals(dbName, response.getName());
    assertEquals(defaultWorkspaceId, response.getWorkspaceId());
    assertEquals(postgresSourceSpecId, response.getSourceSpecificationId());
    assertEquals(Jsons.jsonNode(sourceDbConfig), response.getConnectionConfiguration());
  }

  @Test
  @Order(4)
  public void testSourceCheckConnection() throws ApiException {
    UUID sourceImplId = createPostgresSourceImpl().getSourceImplementationId();
    CheckConnectionRead checkConnectionRead = apiClient.getSourceImplementationApi()
        .checkConnectionToSourceImplementation(new SourceImplementationIdRequestBody().sourceImplementationId(sourceImplId));
    assertEquals(CheckConnectionRead.StatusEnum.SUCCESS, checkConnectionRead.getStatus());
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
  public void testManualSync() throws IOException, ApiException, SQLException, InterruptedException {
    String connectionName = "test-connection";
    UUID sourceImplId = createPostgresSourceImpl().getSourceImplementationId();
    UUID destinationImplId = createPostgresDestinationImpl().getDestinationImplementationId();
    SourceSchema schema = discoverSourceSchema(sourceImplId);
    schema.getTables().forEach(table -> table.getColumns().forEach(c -> c.setSelected(true))); // select all columns
    ConnectionSchedule connectionSchedule = new ConnectionSchedule().units(100L).timeUnit(MINUTES);
    ConnectionCreate.SyncModeEnum syncMode = ConnectionCreate.SyncModeEnum.FULL_REFRESH;
    ConnectionRead createdConnection = createConnection(connectionName, sourceImplId, destinationImplId, schema, connectionSchedule, syncMode);

    ConnectionSyncRead connectionSyncRead =
        apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(createdConnection.getConnectionId()));
    assertEquals(ConnectionSyncRead.StatusEnum.SUCCESS, connectionSyncRead.getStatus());
    assertSourceAndTargetDbInSync(sourcePsql, targetPsql);
  }

  @Test
  @Order(8)
  public void testScheduledSync() throws InterruptedException, SQLException, ApiException {
    String connectionName = "test-connection";
    UUID sourceImplId = createPostgresSourceImpl().getSourceImplementationId();
    UUID destinationImplId = createPostgresDestinationImpl().getDestinationImplementationId();
    SourceSchema schema = discoverSourceSchema(sourceImplId);
    schema.getTables().forEach(table -> table.getColumns().forEach(c -> c.setSelected(true))); // select all columns
    ConnectionSchedule connectionSchedule = new ConnectionSchedule().units(1L).timeUnit(MINUTES);
    ConnectionCreate.SyncModeEnum syncMode = ConnectionCreate.SyncModeEnum.FULL_REFRESH;

    createConnection(connectionName, sourceImplId, destinationImplId, schema, connectionSchedule, syncMode);

    // When a new connection is created, Dataline might sync it immediately (before the sync interval). Then it will wait the sync interval.
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

    Set<String> sourceTables = listTables(sourceDbPool);
    Set<String> targetTables = listTables(targetDbPool);
    assertEquals(sourceTables, targetTables);

    for (String table : sourceTables) {
      assertTablesEquivalent(sourceDbPool, targetDbPool, table);
    }
  }

  private BasicDataSource getConnectionPool(PostgreSQLContainer db) {
    return DatabaseHelper.getConnectionPool(
        db.getUsername(), db.getPassword(), db.getJdbcUrl());
  }

  private Set<String> listTables(BasicDataSource connectionPool) throws SQLException {
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

  private void assertTablesEquivalent(
      BasicDataSource sourceDbPool,
      BasicDataSource targetDbPool,
      String table)
      throws SQLException {
    long sourceTableCount = getTableCount(sourceDbPool, table);
    long targetTableCount = getTableCount(targetDbPool, table);
    assertEquals(sourceTableCount, targetTableCount);
    Result<Record> allRecords =
        DatabaseHelper.query(
            sourceDbPool, context -> context.fetch(String.format("SELECT * FROM %s;", table)));
    for (Record sourceTableRecord : allRecords) {
      assertRecordInTable(sourceTableRecord, targetDbPool, table);
    }
  }

  /**
   * Verifies that a record in the target table and database exists with the same (and potentially
   * more) fields.
   */
  @SuppressWarnings("unchecked")
  private void assertRecordInTable(Record record, BasicDataSource connectionPool, String tableName)
      throws SQLException {

    Set<Condition> conditions = new HashSet<>();
    for (Field<?> field : record.fields()) {
      Object fieldValue = record.get(field);
      Condition eq = ((Field) field).equal(fieldValue);
      conditions.add(eq);
    }

    Result<Record> presentRecords =
        DatabaseHelper.query(
            connectionPool, context -> context.select().from(tableName).where(conditions).fetch());

    // TODO validate that the correct number of records exists? currently if the same record exists
    // multiple times in the source but once in destination, this returns true.
    assertEquals(1, presentRecords.size());
  }

  private long getTableCount(BasicDataSource connectionPool, String tableName) throws SQLException {
    return DatabaseHelper.query(
        connectionPool,
        context -> {
          Result<Record> record =
              context.fetch(String.format("SELECT COUNT(*) FROM %s;", tableName));
          return (long) record.stream().findFirst().get().get(0);
        });
  }

  private void testRunManualSync(UUID connectionId) throws ApiException {

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
        getPostgresDestinationSpecId(),
        getDestinationDbConfig());
  }

  private Map<Object, Object> getDestinationDbConfig() {
    return ImmutableMap.builder()
        .put("postgres_host", targetPsql.getHost())
        .put("postgres_username", targetPsql.getUsername())
        .put("postgres_password", targetPsql.getPassword())
        .put("postgres_schema", "public")
        .put("postgres_port", targetPsql.getFirstMappedPort())
        .put("postgres_database", targetPsql.getDatabaseName())
        .build();
  }

  private DestinationImplementationRead createDestinationImplementation(String name,
                                                                        UUID workspaceId,
                                                                        UUID destinationSpecId,
                                                                        Map<Object, Object> destinationConfig)
      throws ApiException {
    DestinationImplementationRead destinationImplementation =
        apiClient.getDestinationImplementationApi().createDestinationImplementation(new DestinationImplementationCreate()
            .name(name)
            .connectionConfiguration(Jsons.jsonNode(destinationConfig))
            .workspaceId(workspaceId)
            .destinationSpecificationId(destinationSpecId));

    return destinationImplementation;
  }

  private UUID getPostgresDestinationSpecId() throws ApiException {
    UUID destinationId = apiClient.getDestinationApi().listDestinations().getDestinations()
        .stream()
        .filter(dr -> dr.getName().toLowerCase().equals("postgres"))
        .findFirst()
        .orElseThrow()
        .getDestinationId();
    return apiClient.getDestinationSpecificationApi()
        .getDestinationSpecification(new DestinationIdRequestBody().destinationId(destinationId))
        .getDestinationSpecificationId();
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
        getPostgresSourceSpecId(),
        getSourceDbConfig());
  }

  private SourceImplementationRead createSourceImplementation(String name, UUID workspaceId, UUID sourceSpecId, Map<Object, Object> sourceConfig)
      throws ApiException {
    SourceImplementationRead sourceImplementation = apiClient.getSourceImplementationApi().createSourceImplementation(new SourceImplementationCreate()
        .name(name)
        .sourceSpecificationId(sourceSpecId)
        .workspaceId(workspaceId)
        .connectionConfiguration(Jsons.jsonNode(sourceConfig)));
    sourceImplIds.add(sourceImplementation.getSourceImplementationId());
    return sourceImplementation;
  }

  private UUID getPostgresSourceSpecId() throws ApiException {
    UUID postgresSourceId = apiClient.getSourceApi().listSources().getSources()
        .stream()
        .filter(sourceRead -> sourceRead.getName().toLowerCase().equals("postgres"))
        .findFirst()
        .orElseThrow()
        .getSourceId();

    SourceSpecificationRead sourceSpecRead =
        apiClient.getSourceSpecificationApi().getSourceSpecification(new SourceIdRequestBody().sourceId(postgresSourceId));
    return sourceSpecRead.getSourceSpecificationId();
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

}
