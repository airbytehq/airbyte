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

package io.dataline.tests.acceptance;

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
import io.dataline.api.client.model.ConnectionSyncRead;
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
import java.io.IOException;
import java.sql.SQLException;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Condition;
import org.jooq.Field;
import org.jooq.Record;
import org.jooq.Result;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

public class AcceptanceTests {

  static final Logger LOGGER = LoggerFactory.getLogger(AcceptanceTests.class);

  static PostgreSQLContainer SOURCE_PSQL;
  static PostgreSQLContainer TARGET_PSQL;

  DatalineApiClient apiClient = new DatalineApiClient(
      new ApiClient().setScheme("http")
          .setHost("localhost")
          .setPort(8001)
          .setBasePath("/api"));

  @BeforeAll
  public static void init() throws IOException, InterruptedException {
    SOURCE_PSQL = new PostgreSQLContainer();
    TARGET_PSQL = new PostgreSQLContainer();
    SOURCE_PSQL.start();
    TARGET_PSQL.start();

    runSqlScript(MountableFile.forClasspathResource("simple_postgres_init.sql"), SOURCE_PSQL);
  }

  private static void runSqlScript(MountableFile file, PostgreSQLContainer db)
      throws IOException, InterruptedException {
    String scriptPath = "/etc/" + UUID.randomUUID().toString() + ".sql";
    db.copyFileToContainer(file, scriptPath);
    db.execInContainer(
        "psql", "-d", db.getDatabaseName(), "-U", db.getUsername(), "-a", "-f", scriptPath);
  }

  @Test
  public void fullTestRun() throws IOException, ApiException, SQLException {
    UUID createdSourceImplId = testCreateSourceImplementation().getSourceImplementationId();
    testCheckSourceConnection(createdSourceImplId);

    UUID createdDestinationImplId = testCreateDestinationImpl().getDestinationImplementationId();
    testCheckDestinationConnection(createdDestinationImplId);

    SourceSchema schema = testDiscoverSourceSchema(createdSourceImplId);

    // select all columns
    schema.getTables().forEach(table -> table.getColumns().forEach(c -> c.setSelected(true)));

    ConnectionRead createdConnection = testCreateConnection(createdSourceImplId, createdDestinationImplId, schema);

    testRunManualSync(createdConnection.getConnectionId());

    assertSourceAndTargetDbInSync(SOURCE_PSQL, TARGET_PSQL);

    // TODO test scheduled sync
  }

  private void assertSourceAndTargetDbInSync(PostgreSQLContainer sourceDb, PostgreSQLContainer targetDb) throws SQLException {
    BasicDataSource sourceDbPool =
        DatabaseHelper.getConnectionPool(
            sourceDb.getUsername(), sourceDb.getPassword(), sourceDb.getJdbcUrl());
    BasicDataSource targetDbPool =
        DatabaseHelper.getConnectionPool(
            targetDb.getUsername(), targetDb.getPassword(), targetDb.getJdbcUrl());

    Set<String> sourceTables = listTables(sourceDbPool);
    Set<String> targetTables = listTables(targetDbPool);
    assertEquals(sourceTables, targetTables);

    for (String table : sourceTables) {
      assertTablesEquivalent(sourceDbPool, targetDbPool, table);
    }
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

  private void testCheckSourceConnection(UUID sourceImplementationId) throws ApiException {
    try {
      CheckConnectionRead checkConnectionRead = apiClient.getSourceImplementationApi()
          .checkConnectionToSourceImplementation(new SourceImplementationIdRequestBody().sourceImplementationId(sourceImplementationId));
      assertEquals(CheckConnectionRead.StatusEnum.SUCCESS, checkConnectionRead.getStatus());
    } catch (ApiException e) {
      LOGGER.info("{}", e.getResponseBody());
      throw e;
    }
  }

  private ConnectionRead testCreateConnection(UUID sourceImplId, UUID destinationImplId, SourceSchema schema)
      throws ApiException {
    ConnectionSchedule schedule = new ConnectionSchedule().timeUnit(ConnectionSchedule.TimeUnitEnum.MINUTES).units(3L);
    ConnectionCreate.SyncModeEnum syncMode = ConnectionCreate.SyncModeEnum.FULL_REFRESH;
    String name = "AccTest-PG2PG-" + UUID.randomUUID().toString();
    UUID createdConnectionId = apiClient.getConnectionApi().createConnection(
        new ConnectionCreate()
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
        .put("postgres_host", TARGET_PSQL.getHost())
        .put("postgres_username", TARGET_PSQL.getUsername())
        .put("postgres_password", TARGET_PSQL.getPassword())
        .put("postgres_schema", "public")
        .put("postgres_port", TARGET_PSQL.getFirstMappedPort())
        .put("postgres_database", TARGET_PSQL.getDatabaseName())
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

  private SourceImplementationRead testCreateSourceImplementation() throws IOException, ApiException {
    UUID postgresSourceId = getPostgresSourceId();
    SourceSpecificationRead sourceSpecRead =
        apiClient.getSourceSpecificationApi().getSourceSpecification(new SourceIdRequestBody().sourceId(postgresSourceId));

    JsonNode dbConfiguration = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", SOURCE_PSQL.getHost())
        .put("password", SOURCE_PSQL.getPassword())
        .put("port", SOURCE_PSQL.getFirstMappedPort())
        .put("dbname", SOURCE_PSQL.getDatabaseName())
        .put("filter_dbs", SOURCE_PSQL.getDatabaseName())
        .put("user", SOURCE_PSQL.getUsername()).build());

    UUID defaultWorkspaceId = PersistenceConstants.DEFAULT_WORKSPACE_ID;
    UUID sourceSpecificationId = sourceSpecRead.getSourceSpecificationId();
    String sourceImplName = "dataline-db";

    SourceImplementationCreate sourceImplementationCreate = new SourceImplementationCreate()
        .name(sourceImplName)
        .sourceSpecificationId(sourceSpecificationId)
        .workspaceId(defaultWorkspaceId)
        .connectionConfiguration(dbConfiguration);

    SourceImplementationRead createResponse = apiClient.getSourceImplementationApi().createSourceImplementation(sourceImplementationCreate);

    assertEquals(sourceImplName, createResponse.getName());
    assertEquals(defaultWorkspaceId, createResponse.getWorkspaceId());
    assertEquals(sourceSpecificationId, createResponse.getSourceSpecificationId());
    assertEquals(dbConfiguration, Jsons.jsonNode(createResponse.getConnectionConfiguration()));
    return createResponse;
  }

  private UUID getPostgresSourceId() throws ApiException {
    return apiClient.getSourceApi().listSources().getSources()
        .stream()
        .filter(sourceRead -> sourceRead.getName().toLowerCase().equals("postgres"))
        .findFirst()
        .orElseThrow()
        .getSourceId();
  }

}
