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

package io.dataline.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.dataline.api.model.ConnectionCreate;
import io.dataline.api.model.ConnectionIdRequestBody;
import io.dataline.api.model.ConnectionRead;
import io.dataline.api.model.ConnectionReadList;
import io.dataline.api.model.ConnectionSchedule;
import io.dataline.api.model.ConnectionStatus;
import io.dataline.api.model.ConnectionUpdate;
import io.dataline.api.model.SourceSchema;
import io.dataline.api.model.SourceSchemaColumn;
import io.dataline.api.model.SourceSchemaTable;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.commons.enums.Enums;
import io.dataline.config.Column;
import io.dataline.config.DataType;
import io.dataline.config.Schedule;
import io.dataline.config.Schema;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncSchedule;
import io.dataline.config.Table;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.config.persistence.PersistenceConfigType;
import io.dataline.server.helpers.SourceImplementationHelpers;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ConnectionsHandlerTest {

  private ConfigPersistence configPersistence;
  private Supplier<UUID> uuidGenerator;

  private StandardSync standardSync;
  private StandardSyncSchedule standardSyncSchedule;
  private ConnectionsHandler connectionsHandler;
  private SourceConnectionImplementation sourceImplementation;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() {
    configPersistence = mock(ConfigPersistence.class);
    uuidGenerator = mock(Supplier.class);

    sourceImplementation =
        SourceImplementationHelpers.generateSourceImplementationMock(UUID.randomUUID());
    standardSync = generateSync(sourceImplementation.getSourceImplementationId());
    standardSyncSchedule = generateSchedule(standardSync.getConnectionId());

    connectionsHandler = new ConnectionsHandler(configPersistence, uuidGenerator);
  }

  @Test
  void testCreateConnection() throws JsonValidationException, ConfigNotFoundException {
    when(uuidGenerator.get()).thenReturn(standardSync.getConnectionId());

    when(configPersistence.getConfig(
            PersistenceConfigType.STANDARD_SYNC,
            standardSync.getConnectionId().toString(),
            StandardSync.class))
        .thenReturn(standardSync);

    when(configPersistence.getConfig(
            PersistenceConfigType.STANDARD_SYNC_SCHEDULE,
            standardSyncSchedule.getConnectionId().toString(),
            StandardSyncSchedule.class))
        .thenReturn(standardSyncSchedule);

    final ConnectionCreate connectionCreate = new ConnectionCreate();
    connectionCreate.setSourceImplementationId(standardSync.getSourceImplementationId());
    connectionCreate.setDestinationImplementationId(standardSync.getDestinationImplementationId());
    connectionCreate.setName("presto to hudi");
    connectionCreate.setStatus(ConnectionStatus.ACTIVE);
    // todo (cgardens) - the codegen auto-nests enums as subclasses. this won't work. we expect
    //   these enums to be reusable in create, update, read.
    connectionCreate.setSyncMode(ConnectionCreate.SyncModeEnum.APPEND);
    connectionCreate.setSchedule(generateBasicSchedule());
    connectionCreate.setSyncSchema(generateBasicApiSchema());

    final ConnectionRead actualConnectionRead =
        connectionsHandler.createConnection(connectionCreate);

    final ConnectionRead expectedConnectionRead =
        generateExpectedConnectionRead(
            standardSync.getConnectionId(),
            standardSync.getSourceImplementationId(),
            standardSync.getDestinationImplementationId());

    assertEquals(expectedConnectionRead, actualConnectionRead);

    verify(configPersistence)
        .writeConfig(
            PersistenceConfigType.STANDARD_SYNC,
            standardSync.getConnectionId().toString(),
            standardSync);

    verify(configPersistence)
        .writeConfig(
            PersistenceConfigType.STANDARD_SYNC_SCHEDULE,
            standardSyncSchedule.getConnectionId().toString(),
            standardSyncSchedule);
  }

  @Test
  void testUpdateConnection() throws JsonValidationException, ConfigNotFoundException {
    final SourceSchema newApiSchema = generateBasicApiSchema();
    newApiSchema.getTables().get(0).setName("azkaban_users");

    final ConnectionUpdate connectionUpdate = new ConnectionUpdate();
    connectionUpdate.setConnectionId(standardSync.getConnectionId());
    connectionUpdate.setStatus(ConnectionStatus.INACTIVE);
    connectionUpdate.setSchedule(null);
    connectionUpdate.setSyncSchema(newApiSchema);

    final Schema newPersistenceSchema = generateBasicPersistenceSchema();
    newPersistenceSchema.getTables().get(0).setName("azkaban_users");

    final StandardSync updatedStandardSync = new StandardSync();
    updatedStandardSync.setConnectionId(standardSync.getConnectionId());
    updatedStandardSync.setName("presto to hudi");
    updatedStandardSync.setSourceImplementationId(standardSync.getSourceImplementationId());
    updatedStandardSync.setDestinationImplementationId(
        standardSync.getDestinationImplementationId());
    updatedStandardSync.setSyncMode(standardSync.getSyncMode());
    updatedStandardSync.setStatus(StandardSync.Status.INACTIVE);
    updatedStandardSync.setSchema(newPersistenceSchema);

    final StandardSyncSchedule updatedPersistenceSchedule = new StandardSyncSchedule();
    updatedPersistenceSchedule.setConnectionId(standardSyncSchedule.getConnectionId());
    updatedPersistenceSchedule.setManual(true);

    when(configPersistence.getConfig(
            PersistenceConfigType.STANDARD_SYNC,
            standardSync.getConnectionId().toString(),
            StandardSync.class))
        .thenReturn(standardSync)
        .thenReturn(updatedStandardSync);

    when(configPersistence.getConfig(
            PersistenceConfigType.STANDARD_SYNC_SCHEDULE,
            standardSyncSchedule.getConnectionId().toString(),
            StandardSyncSchedule.class))
        .thenReturn(standardSyncSchedule)
        .thenReturn(updatedPersistenceSchedule);

    final ConnectionRead actualConnectionRead =
        connectionsHandler.updateConnection(connectionUpdate);

    final ConnectionRead expectedConnectionRead =
        generateExpectedConnectionRead(
            standardSync.getConnectionId(),
            standardSync.getSourceImplementationId(),
            standardSync.getDestinationImplementationId());

    expectedConnectionRead.setSchedule(null);
    expectedConnectionRead.setSyncSchema(newApiSchema);
    expectedConnectionRead.setStatus(ConnectionStatus.INACTIVE);

    assertEquals(expectedConnectionRead, actualConnectionRead);

    verify(configPersistence)
        .writeConfig(
            PersistenceConfigType.STANDARD_SYNC,
            standardSync.getConnectionId().toString(),
            updatedStandardSync);

    verify(configPersistence)
        .writeConfig(
            PersistenceConfigType.STANDARD_SYNC_SCHEDULE,
            standardSyncSchedule.getConnectionId().toString(),
            updatedPersistenceSchedule);
  }

  @Test
  void testGetConnection() throws JsonValidationException, ConfigNotFoundException {
    when(configPersistence.getConfig(
            PersistenceConfigType.STANDARD_SYNC,
            standardSync.getConnectionId().toString(),
            StandardSync.class))
        .thenReturn(standardSync);

    when(configPersistence.getConfig(
            PersistenceConfigType.STANDARD_SYNC_SCHEDULE,
            standardSync.getConnectionId().toString(),
            StandardSyncSchedule.class))
        .thenReturn(standardSyncSchedule);

    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody();
    connectionIdRequestBody.setConnectionId(standardSync.getConnectionId());
    final ConnectionRead actualConnectionRead =
        connectionsHandler.getConnection(connectionIdRequestBody);

    assertEquals(generateExpectedConnectionRead(), actualConnectionRead);
  }

  @Test
  void testListConnectionsForWorkspace() throws JsonValidationException, ConfigNotFoundException {
    // mock list off all syncs
    when(configPersistence.getConfigs(PersistenceConfigType.STANDARD_SYNC, StandardSync.class))
        .thenReturn(Sets.newHashSet(standardSync));

    // mock get source connection impl (used to check that connection is associated with given
    // workspace)
    when(configPersistence.getConfig(
            PersistenceConfigType.SOURCE_CONNECTION_IMPLEMENTATION,
            sourceImplementation.getSourceImplementationId().toString(),
            SourceConnectionImplementation.class))
        .thenReturn(sourceImplementation);

    // mock get schedule for the now verified connection
    when(configPersistence.getConfig(
            PersistenceConfigType.STANDARD_SYNC_SCHEDULE,
            standardSync.getConnectionId().toString(),
            StandardSyncSchedule.class))
        .thenReturn(standardSyncSchedule);

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody();
    workspaceIdRequestBody.setWorkspaceId(sourceImplementation.getWorkspaceId());
    final ConnectionReadList actualConnectionReadList =
        connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody);

    assertEquals(
        generateExpectedConnectionRead(), actualConnectionReadList.getConnections().get(0));
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(ConnectionStatus.class, StandardSync.Status.class));
    assertTrue(Enums.isCompatible(StandardSync.SyncMode.class, ConnectionRead.SyncModeEnum.class));
    assertTrue(Enums.isCompatible(StandardSync.Status.class, ConnectionStatus.class));
    assertTrue(Enums.isCompatible(ConnectionSchedule.TimeUnitEnum.class, Schedule.TimeUnit.class));
    assertTrue(Enums.isCompatible(io.dataline.api.model.DataType.class, DataType.class));
    assertTrue(Enums.isCompatible(DataType.class, io.dataline.api.model.DataType.class));
  }

  private StandardSync generateSync(UUID sourceImplementationId) {
    final UUID connectionId = UUID.randomUUID();

    final StandardSync standardSync = new StandardSync();
    standardSync.setConnectionId(connectionId);
    standardSync.setName("presto to hudi");
    standardSync.setStatus(StandardSync.Status.ACTIVE);
    standardSync.setSchema(generateBasicPersistenceSchema());
    standardSync.setSourceImplementationId(sourceImplementationId);
    standardSync.setDestinationImplementationId(UUID.randomUUID());
    standardSync.setSyncMode(StandardSync.SyncMode.APPEND);

    return standardSync;
  }

  private Schema generateBasicPersistenceSchema() {
    final Column column = new Column();
    column.setDataType(DataType.STRING);
    column.setName("id");

    final Table table = new Table();
    table.setName("users");
    table.setColumns(Lists.newArrayList(column));

    final Schema schema = new Schema();
    schema.setTables(Lists.newArrayList(table));

    return schema;
  }

  private SourceSchema generateBasicApiSchema() {
    final SourceSchemaColumn column = new SourceSchemaColumn();
    column.setDataType(io.dataline.api.model.DataType.STRING);
    column.setName("id");

    final SourceSchemaTable table = new SourceSchemaTable();
    table.setName("users");
    table.setColumns(Lists.newArrayList(column));

    final SourceSchema schema = new SourceSchema();
    schema.setTables(Lists.newArrayList(table));

    return schema;
  }

  private ConnectionSchedule generateBasicSchedule() {
    final ConnectionSchedule connectionSchedule = new ConnectionSchedule();
    connectionSchedule.setTimeUnit(ConnectionSchedule.TimeUnitEnum.DAYS);
    connectionSchedule.setUnits(1);

    return connectionSchedule;
  }

  private ConnectionRead generateExpectedConnectionRead(
      UUID connectionId, UUID sourceImplementationId, UUID destinationImplementationId) {
    final ConnectionRead expectedConnectionRead = new ConnectionRead();
    expectedConnectionRead.setConnectionId(connectionId);
    expectedConnectionRead.setSourceImplementationId(sourceImplementationId);
    expectedConnectionRead.setDestinationImplementationId(destinationImplementationId);
    expectedConnectionRead.setName("presto to hudi");
    expectedConnectionRead.setStatus(ConnectionStatus.ACTIVE);
    expectedConnectionRead.setSyncMode(ConnectionRead.SyncModeEnum.APPEND);
    expectedConnectionRead.setSchedule(generateBasicSchedule());
    expectedConnectionRead.setSyncSchema(generateBasicApiSchema());

    return expectedConnectionRead;
  }

  private ConnectionRead generateExpectedConnectionRead() {
    return generateExpectedConnectionRead(
        standardSync.getConnectionId(),
        standardSync.getSourceImplementationId(),
        standardSync.getDestinationImplementationId());
  }

  private StandardSyncSchedule generateSchedule(UUID connectionId) {
    final Schedule schedule = new Schedule();
    schedule.setTimeUnit(Schedule.TimeUnit.DAYS);
    schedule.setUnits(1);

    final StandardSyncSchedule standardSchedule = new StandardSyncSchedule();
    standardSchedule.setConnectionId(connectionId);
    standardSchedule.setSchedule(schedule);
    standardSchedule.setManual(false);

    return standardSchedule;
  }
}
