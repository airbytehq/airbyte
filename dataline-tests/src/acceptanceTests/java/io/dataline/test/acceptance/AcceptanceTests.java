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

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
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
import io.dataline.api.client.model.DestinationImplementationUpdate;
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
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

@SuppressWarnings("rawtypes")
public class AcceptanceTests {

  private static final Logger LOGGER = LoggerFactory.getLogger(AcceptanceTests.class);
  private PostgreSQLContainer sourcePsql;
  private PostgreSQLContainer targetPsql;

  private DatalineApiClient apiClient = new DatalineApiClient(
      new ApiClient().setScheme("http")
          .setHost("localhost")
          .setPort(8001)
          .setBasePath("/api"));

  private List<UUID> sourceImplIds = Lists.newArrayList();
  private List<UUID> destinationImplIds = Lists.newArrayList();
  private List<UUID> connectionIds = Lists.newArrayList();

  @BeforeEach
  public void init() throws IOException, InterruptedException {
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

    for (UUID connectionId : connectionIds){
      disableConnection(connectionId);
    }
  }

  @Test
  public void testCreateSourceImplementation() throws IOException, ApiException {
    String dbName = "acc-test-db";
    UUID postgresSourceSpecId = getPostgresSourceSpecId();
    UUID defaultWorkspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;
    Map<Object, Object> sourceDbConfig = getSourceDbConfig();
    SourceImplementationRead response = createSourceImplementation(
        dbName,
        postgresSourceSpecId,
        defaultWorkspaceId,
        sourceDbConfig
    );

    assertEquals(dbName, response.getName());
    assertEquals(defaultWorkspaceId, response.getWorkspaceId());
    assertEquals(postgresSourceSpecId, response.getSourceSpecificationId());
    assertEquals(Jsons.jsonNode(sourceDbConfig), response.getConnectionConfiguration());
  }

  @Test
  public void testSourceCheckConnection() throws IOException, ApiException {
    UUID sourceImplId = createPostgresSourceImpl().getSourceImplementationId();
    CheckConnectionRead checkConnectionRead = apiClient.getSourceImplementationApi()
        .checkConnectionToSourceImplementation(new SourceImplementationIdRequestBody().sourceImplementationId(sourceImplId));
    assertEquals(CheckConnectionRead.StatusEnum.SUCCESS, checkConnectionRead.getStatus());
  }

  @Test
  public void testSync() throws IOException, ApiException, SQLException, InterruptedException {
    UUID sourceImplId = createPostgresSourceImpl().getSourceImplementationId();
    UUID destinationImplId = testCreateDestinationImpl().getDestinationImplementationId();
    testCheckDestinationConnection(destinationImplId);

    SourceSchema schema = testDiscoverSourceSchema(sourceImplId);

    // select all columns
    schema.getTables().forEach(table -> table.getColumns().forEach(c -> c.setSelected(true)));

    ConnectionRead createdConnection = testCreateConnection(sourceImplId, destinationImplId, schema, 1L);

    testRunManualSync(createdConnection.getConnectionId());

    // TODO This is a bit of a hack to get around the fact that we don't have incremental behavior.
    // Ideally we wouldn't wipe the DB, but running a full_refresh replicate on the same target
    // db twice copies the data to new tables e.g: "students" becomes "students" and "students_123"
    // in the target db which is finicky to validate correctly in the test. Once we support incremental
    // sync, we shouldn't need to wipe the db.
    wipeTables(targetPsql);

    testScheduledSync(Duration.ofSeconds(90));
    assertSourceAndTargetDbInSync(sourcePsql, targetPsql);
  }

  private void testScheduledSync(Duration waitTime) throws InterruptedException, SQLException {
    Thread.sleep(waitTime.toMillis());
    assertSourceAndTargetDbInSync(sourcePsql, targetPsql);
  }

  private void wipeTables(PostgreSQLContainer db) throws SQLException {
    BasicDataSource connectionPool = getConnectionPool(db);
    Set<String> tableNames = listTables(connectionPool);
    for (String table : tableNames) {
      DatabaseHelper.query(
          connectionPool,
          ctx -> {
            ctx.execute("DROP TABLE " + table);
            return null;
          });
    }
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

  private SourceSchema testDiscoverSourceSchema(UUID sourceImplementationId) throws ApiException, IOException {
    SourceSchema actualSchema = apiClient.getSourceImplementationApi().discoverSchemaForSourceImplementation(
        new SourceImplementationIdRequestBody().sourceImplementationId(sourceImplementationId)).getSchema();

    SourceSchema expectedSchema = Jsons.deserialize(MoreResources.readResource("simple_postgres_source_schema.json"), SourceSchema.class);

    assertEquals(expectedSchema, actualSchema);
    return actualSchema;
  }

  private void testRunManualSync(UUID connectionId) throws ApiException {
    ConnectionSyncRead connectionSyncRead = apiClient.getConnectionApi().syncConnection(new ConnectionIdRequestBody().connectionId(connectionId));
    assertEquals(ConnectionSyncRead.StatusEnum.SUCCESS, connectionSyncRead.getStatus());
  }

  private void testCheckDestinationConnection(UUID destinationImplementationId) throws ApiException {
    CheckConnectionRead.StatusEnum checkOperationStatus = apiClient.getDestinationImplementationApi()
        .checkConnectionToDestinationImplementation(
            new DestinationImplementationIdRequestBody().destinationImplementationId(destinationImplementationId))
        .getStatus();

    assertEquals(CheckConnectionRead.StatusEnum.SUCCESS, checkOperationStatus);
  }

  private ConnectionRead testCreateConnection(UUID sourceImplId, UUID destinationImplId, SourceSchema schema, long syncIntervalMinutes)
      throws ApiException {
    ConnectionSchedule schedule = new ConnectionSchedule().timeUnit(ConnectionSchedule.TimeUnitEnum.MINUTES).units(syncIntervalMinutes);
    ConnectionCreate.SyncModeEnum syncMode = ConnectionCreate.SyncModeEnum.FULL_REFRESH;
    String name = "AccTest-PG2PG-" + UUID.randomUUID().toString();
    UUID createdConnectionId = apiClient.getConnectionApi().createConnection(
        new ConnectionCreate()
            .status(ConnectionStatus.ACTIVE)
            .sourceImplementationId(sourceImplId)
            .destinationImplementationId(destinationImplId)
            .syncMode(syncMode)
            .syncSchema(schema)
            .schedule(schedule)
            .name(name))
        .getConnectionId();

    ConnectionRead readConnection = apiClient.getConnectionApi().getConnection(
        new ConnectionIdRequestBody().connectionId(createdConnectionId));

    assertEquals(sourceImplId, readConnection.getSourceImplementationId());
    assertEquals(destinationImplId, readConnection.getDestinationImplementationId());
    assertEquals(ConnectionRead.SyncModeEnum.FULL_REFRESH, readConnection.getSyncMode());
    assertEquals(schema, readConnection.getSyncSchema());
    assertEquals(schedule, readConnection.getSchedule());
    assertEquals(name, readConnection.getName());

    return readConnection;
  }

  private DestinationImplementationRead testCreateDestinationImpl() throws ApiException {
    UUID postgresDestinationId = getPostgresDestinationId();
    UUID destinationSpecId =
        apiClient.getDestinationSpecificationApi()
            .getDestinationSpecification(new DestinationIdRequestBody().destinationId(postgresDestinationId))
            .getDestinationSpecificationId();

    JsonNode dbConfiguration = Jsons.jsonNode(ImmutableMap.builder()
        .put("postgres_host", targetPsql.getHost())
        .put("postgres_username", targetPsql.getUsername())
        .put("postgres_password", targetPsql.getPassword())
        .put("postgres_schema", "public")
        .put("postgres_port", targetPsql.getFirstMappedPort())
        .put("postgres_database", targetPsql.getDatabaseName())
        .build());

    UUID defaultWorkspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;

    DestinationImplementationCreate create = new DestinationImplementationCreate()
        .connectionConfiguration(dbConfiguration)
        .workspaceId(defaultWorkspaceId)
        .destinationSpecificationId(destinationSpecId);

    DestinationImplementationRead destinationImpl = apiClient.getDestinationImplementationApi().createDestinationImplementation(create);

    assertEquals(destinationSpecId, destinationImpl.getDestinationSpecificationId());
    assertEquals(defaultWorkspaceId, destinationImpl.getWorkspaceId());
    assertEquals(dbConfiguration, destinationImpl.getConnectionConfiguration());
    return destinationImpl;
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
    dbConfig.put("filter_dbs", sourcePsql.getDatabaseName());
    dbConfig.put("user", sourcePsql.getUsername());
    return dbConfig;
  }

  private SourceImplementationRead createPostgresSourceImpl() throws IOException, ApiException {
    return createSourceImplementation(
        "acceptanceTestDb-" + UUID.randomUUID().toString(),
        PersistenceConstants.DEFAULT_WORKSPACE_ID,
        getPostgresSourceSpecId(),
        getSourceDbConfig()
    );
  }

  private SourceImplementationRead createSourceImplementation(String dbName, UUID workspaceId, UUID sourceSpecId, Map<Object, Object> sourceConfig)
      throws ApiException {
    SourceImplementationRead sourceImplementation = apiClient.getSourceImplementationApi().createSourceImplementation(new SourceImplementationCreate()
        .name(dbName)
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

  private void deleteDestinationImpl(UUID destinationImplId){
    apiClient.getDestinationImplementationApi().updateDestinationImplementation(new DestinationImplementationUpdate().)
  }

  private void disableConnection(UUID connectionId) throws ApiException {
    apiClient.getConnectionApi().updateConnection(new ConnectionUpdate().status(ConnectionStatus.DEPRECATED));
  }
}
