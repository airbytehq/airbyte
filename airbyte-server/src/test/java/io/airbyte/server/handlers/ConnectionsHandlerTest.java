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

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.api.model.AirbyteCatalog;
import io.airbyte.api.model.ConnectionCreate;
import io.airbyte.api.model.ConnectionIdRequestBody;
import io.airbyte.api.model.ConnectionRead;
import io.airbyte.api.model.ConnectionReadList;
import io.airbyte.api.model.ConnectionSchedule;
import io.airbyte.api.model.ConnectionStatus;
import io.airbyte.api.model.ConnectionUpdate;
import io.airbyte.api.model.NamespaceDefinitionType;
import io.airbyte.api.model.SyncMode;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DataType;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.Schedule;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.WorkerUtils;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.Assert;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ConnectionsHandlerTest {

  private ConfigRepository configRepository;
  private Supplier<UUID> uuidGenerator;

  private ConnectionsHandler connectionsHandler;
  private UUID workspaceId;
  private UUID sourceDefinitionId;
  private UUID sourceId;
  private UUID destinationDefinitionId;
  private UUID destinationId;

  private SourceConnection source;
  private DestinationConnection destination;
  private StandardSync standardSync;
  private UUID connectionId;
  private UUID operationId;
  private StandardSyncOperation standardSyncOperation;
  private WorkspaceHelper workspaceHelper;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws IOException, JsonValidationException, ConfigNotFoundException {
    workspaceId = UUID.randomUUID();
    sourceDefinitionId = UUID.randomUUID();
    sourceId = UUID.randomUUID();
    destinationDefinitionId = UUID.randomUUID();
    destinationId = UUID.randomUUID();
    connectionId = UUID.randomUUID();
    operationId = UUID.randomUUID();
    source = new SourceConnection()
        .withSourceId(sourceId)
        .withWorkspaceId(workspaceId);
    destination = new DestinationConnection()
        .withDestinationId(destinationId)
        .withWorkspaceId(workspaceId);
    standardSync = new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi")
        .withNamespaceDefinition(JobSyncConfig.NamespaceDefinitionType.SOURCE)
        .withNamespaceFormat(null)
        .withPrefix("presto_to_hudi")
        .withStatus(StandardSync.Status.ACTIVE)
        .withCatalog(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog())
        .withSourceId(sourceId)
        .withDestinationId(destinationId)
        .withOperationIds(List.of(operationId))
        .withManual(false)
        .withSchedule(ConnectionHelpers.generateBasicSchedule())
        .withResourceRequirements(WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS);

    standardSyncOperation = new StandardSyncOperation()
        .withOperationId(operationId)
        .withWorkspaceId(workspaceId);

    configRepository = mock(ConfigRepository.class);
    uuidGenerator = mock(Supplier.class);
    workspaceHelper = mock(WorkspaceHelper.class);
    connectionsHandler = new ConnectionsHandler(configRepository, uuidGenerator, workspaceHelper);

    when(workspaceHelper.getWorkspaceForSourceIdIgnoreExceptions(sourceId)).thenReturn(workspaceId);
    when(workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(destinationId)).thenReturn(workspaceId);
    when(workspaceHelper.getWorkspaceForOperationIdIgnoreExceptions(operationId)).thenReturn(workspaceId);
  }

  @Test
  void testCreateConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(uuidGenerator.get()).thenReturn(standardSync.getConnectionId());
    final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
        .withName("source-test")
        .withSourceDefinitionId(UUID.randomUUID());
    final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
        .withName("destination-test")
        .withDestinationDefinitionId(UUID.randomUUID());
    when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);
    when(configRepository.getSourceDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(sourceDefinition);
    when(configRepository.getDestinationDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(destinationDefinition);

    final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();

    final ConnectionCreate connectionCreate = new ConnectionCreate()
        .sourceId(standardSync.getSourceId())
        .destinationId(standardSync.getDestinationId())
        .operationIds(standardSync.getOperationIds())
        .name("presto to hudi")
        .namespaceDefinition(NamespaceDefinitionType.SOURCE)
        .namespaceFormat(null)
        .prefix("presto_to_hudi")
        .status(ConnectionStatus.ACTIVE)
        .schedule(ConnectionHelpers.generateBasicConnectionSchedule())
        .syncCatalog(catalog)
        .resourceRequirements(new io.airbyte.api.model.ResourceRequirements()
            .cpuRequest(standardSync.getResourceRequirements().getCpuRequest())
            .cpuLimit(standardSync.getResourceRequirements().getCpuLimit())
            .memoryRequest(standardSync.getResourceRequirements().getMemoryRequest())
            .memoryLimit(standardSync.getResourceRequirements().getMemoryLimit()));

    final ConnectionRead actualConnectionRead = connectionsHandler.createConnection(connectionCreate);

    final ConnectionRead expectedConnectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);

    assertEquals(expectedConnectionRead, actualConnectionRead);

    verify(configRepository).writeStandardSync(standardSync);
  }

  @Test
  void testValidateConnectionCreateSourceAndDestinationInDifferenceWorkspace() {
    when(workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(destinationId)).thenReturn(UUID.randomUUID());

    final ConnectionCreate connectionCreate = new ConnectionCreate()
        .sourceId(standardSync.getSourceId())
        .destinationId(standardSync.getDestinationId());

    assertThrows(IllegalArgumentException.class, () -> connectionsHandler.createConnection(connectionCreate));
  }

  @Test
  void testValidateConnectionCreateOperationInDifferentWorkspace() {
    when(workspaceHelper.getWorkspaceForOperationIdIgnoreExceptions(operationId)).thenReturn(UUID.randomUUID());

    final ConnectionCreate connectionCreate = new ConnectionCreate()
        .sourceId(standardSync.getSourceId())
        .destinationId(standardSync.getDestinationId())
        .operationIds(Collections.singletonList(operationId));

    assertThrows(IllegalArgumentException.class, () -> connectionsHandler.createConnection(connectionCreate));
  }

  @Test
  void testCreateConnectionWithBadDefinitionIds() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(uuidGenerator.get()).thenReturn(standardSync.getConnectionId());
    UUID sourceIdBad = UUID.randomUUID();
    UUID destinationIdBad = UUID.randomUUID();

    final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
        .withName("source-test")
        .withSourceDefinitionId(UUID.randomUUID());
    final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
        .withName("destination-test")
        .withDestinationDefinitionId(UUID.randomUUID());
    when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);
    when(configRepository.getSourceDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(sourceDefinition);
    when(configRepository.getDestinationDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(destinationDefinition);

    when(configRepository.getSourceConnection(sourceIdBad))
        .thenThrow(new ConfigNotFoundException(ConfigSchema.SOURCE_CONNECTION, sourceIdBad));
    when(configRepository.getDestinationConnection(destinationIdBad))
        .thenThrow(new ConfigNotFoundException(ConfigSchema.DESTINATION_CONNECTION, destinationIdBad));

    final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();

    final ConnectionCreate connectionCreateBadSource = new ConnectionCreate()
        .sourceId(sourceIdBad)
        .destinationId(standardSync.getDestinationId())
        .operationIds(standardSync.getOperationIds())
        .name("presto to hudi")
        .namespaceDefinition(NamespaceDefinitionType.SOURCE)
        .namespaceFormat(null)
        .prefix("presto_to_hudi")
        .status(ConnectionStatus.ACTIVE)
        .schedule(ConnectionHelpers.generateBasicConnectionSchedule())
        .syncCatalog(catalog);

    assertThrows(ConfigNotFoundException.class, () -> connectionsHandler.createConnection(connectionCreateBadSource));

    final ConnectionCreate connectionCreateBadDestination = new ConnectionCreate()
        .sourceId(standardSync.getSourceId())
        .destinationId(destinationIdBad)
        .operationIds(standardSync.getOperationIds())
        .name("presto to hudi")
        .namespaceDefinition(NamespaceDefinitionType.SOURCE)
        .namespaceFormat(null)
        .prefix("presto_to_hudi")
        .status(ConnectionStatus.ACTIVE)
        .schedule(ConnectionHelpers.generateBasicConnectionSchedule())
        .syncCatalog(catalog);

    assertThrows(ConfigNotFoundException.class, () -> connectionsHandler.createConnection(connectionCreateBadDestination));

  }

  @Test
  void testUpdateConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();
    catalog.getStreams().get(0).getStream().setName("azkaban_users");
    catalog.getStreams().get(0).getConfig().setAliasName("azkaban_users");

    final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
        .namespaceDefinition(Enums.convertTo(standardSync.getNamespaceDefinition(), NamespaceDefinitionType.class))
        .namespaceFormat(standardSync.getNamespaceFormat())
        .prefix(standardSync.getPrefix())
        .connectionId(standardSync.getConnectionId())
        .operationIds(standardSync.getOperationIds())
        .status(ConnectionStatus.INACTIVE)
        .schedule(null)
        .syncCatalog(catalog);

    final ConfiguredAirbyteCatalog configuredCatalog = ConnectionHelpers.generateBasicConfiguredAirbyteCatalog();
    configuredCatalog.getStreams().get(0).getStream().withName("azkaban_users");

    final StandardSync updatedStandardSync = new StandardSync()
        .withConnectionId(standardSync.getConnectionId())
        .withName("presto to hudi")
        .withNamespaceDefinition(io.airbyte.config.JobSyncConfig.NamespaceDefinitionType.SOURCE)
        .withNamespaceFormat(standardSync.getNamespaceFormat())
        .withPrefix("presto_to_hudi")
        .withSourceId(standardSync.getSourceId())
        .withDestinationId(standardSync.getDestinationId())
        .withOperationIds(standardSync.getOperationIds())
        .withStatus(StandardSync.Status.INACTIVE)
        .withCatalog(configuredCatalog)
        .withManual(true)
        .withResourceRequirements(WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS);

    when(configRepository.getStandardSync(standardSync.getConnectionId()))
        .thenReturn(standardSync)
        .thenReturn(updatedStandardSync);

    final ConnectionRead actualConnectionRead = connectionsHandler.updateConnection(connectionUpdate);

    final ConnectionRead expectedConnectionRead = ConnectionHelpers.generateExpectedConnectionRead(
        standardSync.getConnectionId(),
        standardSync.getSourceId(),
        standardSync.getDestinationId(),
        standardSync.getOperationIds())
        .schedule(null)
        .syncCatalog(catalog)
        .status(ConnectionStatus.INACTIVE);

    assertEquals(expectedConnectionRead, actualConnectionRead);

    verify(configRepository).writeStandardSync(updatedStandardSync);
  }

  @Test
  void testValidateConnectionUpdateOperationInDifferentWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(workspaceHelper.getWorkspaceForOperationIdIgnoreExceptions(operationId)).thenReturn(UUID.randomUUID());
    when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);

    final ConnectionUpdate connectionUpdate = new ConnectionUpdate()
        .connectionId(standardSync.getConnectionId())
        .operationIds(Collections.singletonList(operationId));

    assertThrows(IllegalArgumentException.class, () -> connectionsHandler.updateConnection(connectionUpdate));
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
    when(configRepository.getSourceConnection(source.getSourceId()))
        .thenReturn(source);
    when(configRepository.getStandardSync(standardSync.getConnectionId()))
        .thenReturn(standardSync);

    final WorkspaceIdRequestBody workspaceIdRequestBody = new WorkspaceIdRequestBody().workspaceId(source.getWorkspaceId());
    final ConnectionReadList actualConnectionReadList = connectionsHandler.listConnectionsForWorkspace(workspaceIdRequestBody);

    assertEquals(
        ConnectionHelpers.generateExpectedConnectionRead(standardSync),
        actualConnectionReadList.getConnections().get(0));
  }

  @Test
  void testDeleteConnection() throws JsonValidationException, IOException, ConfigNotFoundException {
    final ConnectionIdRequestBody connectionIdRequestBody = new ConnectionIdRequestBody().connectionId(standardSync.getConnectionId());

    final ConnectionRead connectionRead = ConnectionHelpers.generateExpectedConnectionRead(
        standardSync.getConnectionId(),
        standardSync.getSourceId(),
        standardSync.getDestinationId(),
        standardSync.getOperationIds());

    final ConnectionUpdate expectedConnectionUpdate = new ConnectionUpdate()
        .namespaceDefinition(connectionRead.getNamespaceDefinition())
        .namespaceFormat(connectionRead.getNamespaceFormat())
        .prefix(connectionRead.getPrefix())
        .connectionId(connectionRead.getConnectionId())
        .operationIds(connectionRead.getOperationIds())
        .status(ConnectionStatus.DEPRECATED)
        .syncCatalog(connectionRead.getSyncCatalog())
        .schedule(connectionRead.getSchedule())
        .resourceRequirements(connectionRead.getResourceRequirements());

    final ConnectionsHandler spiedConnectionsHandler = spy(connectionsHandler);
    doReturn(connectionRead).when(spiedConnectionsHandler).getConnection(connectionIdRequestBody);
    doReturn(null).when(spiedConnectionsHandler).updateConnection(expectedConnectionUpdate);

    spiedConnectionsHandler.deleteConnection(connectionIdRequestBody);

    verify(spiedConnectionsHandler).getConnection(connectionIdRequestBody);
    verify(spiedConnectionsHandler).updateConnection(expectedConnectionUpdate);
  }

  @Test
  void failOnUnmatchedWorkspacesInCreate() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(workspaceHelper.getWorkspaceForSourceIdIgnoreExceptions(standardSync.getSourceId())).thenReturn(UUID.randomUUID());
    when(workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(standardSync.getDestinationId())).thenReturn(UUID.randomUUID());

    when(uuidGenerator.get()).thenReturn(standardSync.getConnectionId());
    final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
        .withName("source-test")
        .withSourceDefinitionId(UUID.randomUUID());
    final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
        .withName("destination-test")
        .withDestinationDefinitionId(UUID.randomUUID());
    when(configRepository.getStandardSync(standardSync.getConnectionId())).thenReturn(standardSync);
    when(configRepository.getSourceDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(sourceDefinition);
    when(configRepository.getDestinationDefinitionFromConnection(standardSync.getConnectionId())).thenReturn(destinationDefinition);

    final AirbyteCatalog catalog = ConnectionHelpers.generateBasicApiCatalog();

    final ConnectionCreate connectionCreate = new ConnectionCreate()
        .sourceId(standardSync.getSourceId())
        .destinationId(standardSync.getDestinationId())
        .operationIds(standardSync.getOperationIds())
        .name("presto to hudi")
        .namespaceDefinition(NamespaceDefinitionType.SOURCE)
        .namespaceFormat(null)
        .prefix("presto_to_hudi")
        .status(ConnectionStatus.ACTIVE)
        .schedule(ConnectionHelpers.generateBasicConnectionSchedule())
        .syncCatalog(catalog)
        .resourceRequirements(new io.airbyte.api.model.ResourceRequirements()
            .cpuRequest(standardSync.getResourceRequirements().getCpuRequest())
            .cpuLimit(standardSync.getResourceRequirements().getCpuLimit())
            .memoryRequest(standardSync.getResourceRequirements().getMemoryRequest())
            .memoryLimit(standardSync.getResourceRequirements().getMemoryLimit()));

    Assert.assertThrows(IllegalArgumentException.class, () -> {
      connectionsHandler.createConnection(connectionCreate);
    });
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(ConnectionStatus.class, StandardSync.Status.class));
    assertTrue(Enums.isCompatible(io.airbyte.config.SyncMode.class, SyncMode.class));
    assertTrue(Enums.isCompatible(StandardSync.Status.class, ConnectionStatus.class));
    assertTrue(Enums.isCompatible(ConnectionSchedule.TimeUnitEnum.class, Schedule.TimeUnit.class));
    assertTrue(Enums.isCompatible(io.airbyte.api.model.DataType.class, DataType.class));
    assertTrue(Enums.isCompatible(DataType.class, io.airbyte.api.model.DataType.class));
    assertTrue(Enums.isCompatible(NamespaceDefinitionType.class, io.airbyte.config.JobSyncConfig.NamespaceDefinitionType.class));
  }

}
