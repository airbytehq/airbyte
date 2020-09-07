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
import io.dataline.api.model.ConnectionCreate;
import io.dataline.api.model.ConnectionIdRequestBody;
import io.dataline.api.model.ConnectionRead;
import io.dataline.api.model.ConnectionReadList;
import io.dataline.api.model.ConnectionSchedule;
import io.dataline.api.model.ConnectionStatus;
import io.dataline.api.model.ConnectionUpdate;
import io.dataline.api.model.SourceSchema;
import io.dataline.api.model.WorkspaceIdRequestBody;
import io.dataline.commons.enums.Enums;
import io.dataline.commons.json.Jsons;
import io.dataline.config.DataType;
import io.dataline.config.Schedule;
import io.dataline.config.Schema;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncSchedule;
import io.dataline.config.persistence.ConfigNotFoundException;
import io.dataline.config.persistence.ConfigRepository;
import io.dataline.config.persistence.JsonValidationException;
import io.dataline.server.helpers.ConnectionHelpers;
import io.dataline.server.helpers.SourceImplementationHelpers;
import java.io.IOException;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ConnectionsHandlerTest {

  private ConfigRepository configRepository;
  private Supplier<UUID> uuidGenerator;

  private StandardSync standardSync;
  private ConnectionsHandler connectionsHandler;
  private SourceConnectionImplementation sourceImplementation;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws IOException {
    configRepository = mock(ConfigRepository.class);
    uuidGenerator = mock(Supplier.class);

    sourceImplementation = SourceImplementationHelpers.generateSourceImplementation(UUID.randomUUID());
    standardSync = ConnectionHelpers.generateSync(sourceImplementation.getSourceImplementationId());

    connectionsHandler = new ConnectionsHandler(configRepository, uuidGenerator);
  }

  @Test
  void testCreateConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(uuidGenerator.get()).thenReturn(standardSync.getConnectionId());

    when(configRepository.getStandardSync(standardSync.getConnectionId()))
        .thenReturn(standardSync);

    final ConnectionCreate connectionCreate = new ConnectionCreate()
        .sourceImplementationId(standardSync.getSourceImplementationId())
        .destinationImplementationId(standardSync.getDestinationImplementationId())
        .name("presto to hudi")
        .status(ConnectionStatus.ACTIVE)
        .syncMode(ConnectionCreate.SyncModeEnum.APPEND)
        .schedule(ConnectionHelpers.generateBasicSchedule())
        .syncSchema(ConnectionHelpers.generateBasicApiSchema());

    final ConnectionRead actualConnectionRead = connectionsHandler.createConnection(connectionCreate);

    final ConnectionRead expectedConnectionRead =
        ConnectionHelpers.generateExpectedConnectionRead(
            standardSync.getConnectionId(),
            standardSync.getSourceImplementationId(),
            standardSync.getDestinationImplementationId());

    assertEquals(expectedConnectionRead, actualConnectionRead);

    verify(configRepository).writeStandardSync(standardSync);
  }

  @Test
  void testUpdateConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceSchema newApiSchema = ConnectionHelpers.generateBasicApiSchema();
    newApiSchema.getTables().get(0).setName("azkaban_users");

    final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
        .connectionId(standardSync.getConnectionId())
        .status(ConnectionStatus.INACTIVE)
        .schedule(null)
        .syncSchema(newApiSchema);

    final Schema newPersistenceSchema = ConnectionHelpers.generateBasicPersistenceSchema();
    newPersistenceSchema.getTables().get(0).withName("azkaban_users");

    final StandardSync updatedStandardSync = Jsons.clone(standardSync)
        .withStatus(StandardSync.Status.INACTIVE)
        .withSchema(newPersistenceSchema)
        .withSyncSchedule(new StandardSyncSchedule().withManual(true));

    when(configRepository.getStandardSync(standardSync.getConnectionId()))
        .thenReturn(standardSync)
        .thenReturn(updatedStandardSync);

    final ConnectionRead actualConnectionRead = connectionsHandler.updateConnection(connectionUpdate);

    final ConnectionRead expectedConnectionRead =
        ConnectionHelpers.generateExpectedConnectionRead(
            standardSync.getConnectionId(),
            standardSync.getSourceImplementationId(),
            standardSync.getDestinationImplementationId())
            .schedule(null)
            .syncSchema(newApiSchema)
            .status(ConnectionStatus.INACTIVE);

    assertEquals(expectedConnectionRead, actualConnectionRead);

    verify(configRepository).writeStandardSync(updatedStandardSync);
  }

  @Test
  void testGetConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.getStandardSync(standardSync.getConnectionId()))
        .thenReturn(standardSync);

    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody().connectionId(standardSync.getConnectionId());
    final ConnectionRead actualConnectionRead = connectionsHandler.getConnection(connectionIdRequestBody);

    assertEquals(ConnectionHelpers.generateExpectedConnectionRead(standardSync), actualConnectionRead);
  }

  @Test
  void testListConnectionsForWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.listStandardSyncs())
        .thenReturn(Lists.newArrayList(standardSync));
    when(configRepository.getSourceConnectionImplementation(sourceImplementation.getSourceImplementationId()))
        .thenReturn(sourceImplementation);
    when(configRepository.getStandardSync(standardSync.getConnectionId()))
        .thenReturn(standardSync);

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(sourceImplementation.getWorkspaceId());
    final ConnectionReadList actualConnectionReadList = connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody);

    assertEquals(
        ConnectionHelpers.generateExpectedConnectionRead(standardSync),
        actualConnectionReadList.getConnections().get(0));
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

}
