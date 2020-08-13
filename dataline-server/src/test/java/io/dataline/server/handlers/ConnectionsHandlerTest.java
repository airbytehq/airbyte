package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.collect.Lists;
import io.dataline.api.model.*;
import io.dataline.config.*;
import io.dataline.config.persistence.ConfigPersistenceImpl;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.helpers.SourceImplementationHelpers;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ConnectionsHandlerTest {

  private ConfigPersistenceImpl configPersistence;
  private StandardSync standardSync;
  private StandardSyncSchedule standardSyncSchedule;
  private ConnectionsHandler connectionsHandler;
  private SourceConnectionImplementation sourceImplementation;

  @BeforeEach
  void setUp() {
    configPersistence = ConfigPersistenceImpl.getTest();

    sourceImplementation =
        SourceImplementationHelpers.generateSourceImplementationMock(
            configPersistence, UUID.randomUUID());
    standardSync = createSyncMock(sourceImplementation.getSourceImplementationId());
    standardSyncSchedule = creatScheduleMock(standardSync.getConnectionId());

    connectionsHandler = new ConnectionsHandler(configPersistence);
  }

  @AfterEach
  void tearDown() {
    configPersistence.deleteAll();
  }

  private StandardSync createSyncMock(UUID sourceImplementationId) {
    final UUID connectionId = UUID.randomUUID();

    final Column column = new Column();
    column.setDataType(Column.DataType.STRING);
    column.setName("id");

    final Table table = new Table();
    table.setName("users");
    table.setColumns(Lists.newArrayList(column));

    final Schema schema = new Schema();
    schema.setTables(Lists.newArrayList(table));

    final StandardSync standardSync = new StandardSync();
    standardSync.setConnectionId(connectionId);
    standardSync.setName("presto to hudi");
    standardSync.setStatus(StandardSync.Status.ACTIVE);
    standardSync.setSchema(schema);
    standardSync.setSourceImplementationId(sourceImplementationId);
    standardSync.setDestinationImplementationId(UUID.randomUUID());
    standardSync.setSyncMode(StandardSync.SyncMode.APPEND);

    configPersistence.writeConfig(
        PersistenceConfigType.STANDARD_SYNC, connectionId.toString(), standardSync);

    return standardSync;
  }

  private SourceSchema getBasicSchema() {
    final SourceSchemaColumn column = new SourceSchemaColumn();
    column.setDataType(SourceSchemaColumn.DataTypeEnum.STRING);
    column.setName("id");

    final SourceSchemaTable table = new SourceSchemaTable();
    table.setName("users");
    table.setColumns(Lists.newArrayList(column));

    final SourceSchema schema = new SourceSchema();
    schema.setTables(Lists.newArrayList(table));

    return schema;
  }

  private ConnectionSchedule getBasicSchedule() {
    final ConnectionSchedule connectionSchedule = new ConnectionSchedule();
    connectionSchedule.setTimeUnit(ConnectionSchedule.TimeUnitEnum.DAYS);
    connectionSchedule.setUnits(1);

    return connectionSchedule;
  }

  private ConnectionRead getExpectedConnectionRead(
      UUID connectionId, UUID sourceImplementationId, UUID destinationImplementationId) {
    final ConnectionRead expectedConnectionRead = new ConnectionRead();
    expectedConnectionRead.setConnectionId(connectionId);
    expectedConnectionRead.setSourceImplementationId(sourceImplementationId);
    expectedConnectionRead.setDestinationImplementationId(destinationImplementationId);
    expectedConnectionRead.setName("presto to hudi");
    expectedConnectionRead.setStatus(ConnectionStatus.ACTIVE);
    expectedConnectionRead.setSyncMode(ConnectionRead.SyncModeEnum.APPEND);
    expectedConnectionRead.setSchedule(getBasicSchedule());
    expectedConnectionRead.setSyncSchema(getBasicSchema());

    return expectedConnectionRead;
  }

  private ConnectionRead getExpectedConnectionRead() {
    return getExpectedConnectionRead(
        standardSync.getConnectionId(),
        standardSync.getSourceImplementationId(),
        standardSync.getDestinationImplementationId());
  }

  private StandardSyncSchedule creatScheduleMock(UUID connectionId) {
    final Schedule schedule = new Schedule();
    schedule.setTimeUnit(Schedule.TimeUnit.DAYS);
    schedule.setUnits(1);

    final StandardSyncSchedule standardSchedule = new StandardSyncSchedule();
    standardSchedule.setConnectionId(connectionId);
    standardSchedule.setSchedule(schedule);
    standardSchedule.setManual(false);

    configPersistence.writeConfig(
        PersistenceConfigType.STANDARD_SYNC_SCHEDULE, connectionId.toString(), standardSchedule);

    return standardSchedule;
  }

  @Test
  void createConnection() {
    final ConnectionCreate connectionCreate = new ConnectionCreate();
    connectionCreate.setSourceImplementationId(standardSync.getSourceImplementationId());
    connectionCreate.setDestinationImplementationId(standardSync.getDestinationImplementationId());
    connectionCreate.setName("presto to hudi");
    connectionCreate.setStatus(ConnectionStatus.ACTIVE);
    // todo (cgardens) - the codegen auto-nests enums as subclasses. this won't work. we expect
    // these
    //   enums to be reusable in create, update, read.
    connectionCreate.setSyncMode(ConnectionCreate.SyncModeEnum.APPEND);
    connectionCreate.setSchedule(getBasicSchedule());
    connectionCreate.setSyncSchema(getBasicSchema());

    final ConnectionRead connection = connectionsHandler.createConnection(connectionCreate);

    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody();
    connectionIdRequestBody.setConnectionId(connection.getConnectionId());
    final ConnectionRead actualConnectionRead =
        connectionsHandler.getConnection(connectionIdRequestBody);

    final ConnectionRead expectedConnectionRead =
        getExpectedConnectionRead(
            connection.getConnectionId(),
            standardSync.getSourceImplementationId(),
            standardSync.getDestinationImplementationId());

    assertEquals(expectedConnectionRead, actualConnectionRead);
  }

  @Test
  void updateConnection() {
    final SourceSchema newSchema = getBasicSchema();
    newSchema.getTables().get(0).setName("azkaban_users");

    final ConnectionUpdate connectionUpdate = new ConnectionUpdate();
    connectionUpdate.setConnectionId(standardSync.getConnectionId());
    connectionUpdate.setStatus(ConnectionStatus.INACTIVE);
    connectionUpdate.setSchedule(null);
    connectionUpdate.setSyncSchema(newSchema);

    connectionsHandler.updateConnection(connectionUpdate);

    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody();
    connectionIdRequestBody.setConnectionId(standardSync.getConnectionId());
    final ConnectionRead actualConnectionRead =
        connectionsHandler.getConnection(connectionIdRequestBody);

    final ConnectionRead expectedConnectionRead =
        getExpectedConnectionRead(
            standardSync.getConnectionId(),
            standardSync.getSourceImplementationId(),
            standardSync.getDestinationImplementationId());

    expectedConnectionRead.setSchedule(null);
    expectedConnectionRead.setSyncSchema(newSchema);
    expectedConnectionRead.setStatus(ConnectionStatus.INACTIVE);

    assertEquals(expectedConnectionRead, actualConnectionRead);
  }

  @Test
  void getConnection() {
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody();
    connectionIdRequestBody.setConnectionId(standardSync.getConnectionId());
    final ConnectionRead actualConnectionRead =
        connectionsHandler.getConnection(connectionIdRequestBody);

    assertEquals(getExpectedConnectionRead(), actualConnectionRead);
  }

  @Test
  void listConnectionsForWorkspace() {
    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody();
    workspaceIdRequestBody.setWorkspaceId(sourceImplementation.getWorkspaceId());
    final ConnectionReadList actualConnectionReadList =
        connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody);

    assertEquals(getExpectedConnectionRead(), actualConnectionReadList.getConnections().get(0));
  }
}
