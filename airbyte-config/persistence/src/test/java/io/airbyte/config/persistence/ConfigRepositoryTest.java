/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncState;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.State;
import io.airbyte.config.persistence.split_secrets.MemorySecretPersistence;
import io.airbyte.config.persistence.split_secrets.NoOpSecretsHydrator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

class ConfigRepositoryTest {

  private static final UUID WORKSPACE_ID = UUID.randomUUID();

  private ConfigPersistence configPersistence;
  private ConfigRepository configRepository;

  @BeforeEach
  void setup() {
    configPersistence = mock(ConfigPersistence.class);
    final var secretPersistence = new MemorySecretPersistence();
    configRepository =
        spy(new ConfigRepository(configPersistence, new NoOpSecretsHydrator(), Optional.of(secretPersistence), Optional.of(secretPersistence)));
  }

  @AfterEach
  void cleanUp() {
    reset(configPersistence);
  }

  @Test
  void testWorkspaceWithNullTombstone() throws ConfigNotFoundException, IOException, JsonValidationException {
    assertReturnsWorkspace(new StandardWorkspace().withWorkspaceId(WORKSPACE_ID));
  }

  @Test
  void testWorkspaceWithFalseTombstone() throws ConfigNotFoundException, IOException, JsonValidationException {
    assertReturnsWorkspace(new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withTombstone(false));
  }

  @Test
  void testWorkspaceWithTrueTombstone() throws ConfigNotFoundException, IOException, JsonValidationException {
    assertReturnsWorkspace(new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withTombstone(true));
  }

  void assertReturnsWorkspace(final StandardWorkspace workspace) throws ConfigNotFoundException, IOException, JsonValidationException {
    when(configPersistence.getConfig(ConfigSchema.STANDARD_WORKSPACE, WORKSPACE_ID.toString(), StandardWorkspace.class)).thenReturn(workspace);

    assertEquals(workspace, configRepository.getStandardWorkspace(WORKSPACE_ID, true));
  }

  @ParameterizedTest
  @ValueSource(booleans = {true, false})
  void testWorkspaceByConnectionId(final boolean isTombstone) throws ConfigNotFoundException, IOException, JsonValidationException {
    final StandardWorkspace workspace = new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withTombstone(isTombstone);

    final UUID connectionId = UUID.randomUUID();
    final UUID sourceId = UUID.randomUUID();
    final StandardSync mSync = new StandardSync()
        .withSourceId(sourceId);
    final SourceConnection mSourceConnection = new SourceConnection()
        .withWorkspaceId(WORKSPACE_ID);
    final StandardWorkspace mWorkflow = new StandardWorkspace()
        .withWorkspaceId(WORKSPACE_ID);

    doReturn(mSync)
        .when(configRepository)
        .getStandardSync(connectionId);
    doReturn(mSourceConnection)
        .when(configRepository)
        .getSourceConnection(sourceId);
    doReturn(mWorkflow)
        .when(configRepository)
        .getStandardWorkspace(WORKSPACE_ID, isTombstone);

    configRepository.getStandardWorkspaceFromConnection(connectionId, isTombstone);

    verify(configRepository).getStandardWorkspace(WORKSPACE_ID, isTombstone);
  }

  @Test
  void testGetConnectionState() throws Exception {
    final UUID connectionId = UUID.randomUUID();
    final State state = new State().withState(Jsons.deserialize("{ \"cursor\": 1000 }"));
    final StandardSyncState connectionState = new StandardSyncState().withConnectionId(connectionId).withState(state);

    when(configPersistence.getConfig(ConfigSchema.STANDARD_SYNC_STATE, connectionId.toString(), StandardSyncState.class))
        .thenThrow(new ConfigNotFoundException(ConfigSchema.STANDARD_SYNC_STATE, connectionId));
    assertEquals(Optional.empty(), configRepository.getConnectionState(connectionId));

    reset(configPersistence);
    when(configPersistence.getConfig(ConfigSchema.STANDARD_SYNC_STATE, connectionId.toString(), StandardSyncState.class))
        .thenReturn(connectionState);
    assertEquals(Optional.of(state), configRepository.getConnectionState(connectionId));
  }

  @Test
  void testUpdateConnectionState() throws Exception {
    final UUID connectionId = UUID.randomUUID();
    final State state1 = new State().withState(Jsons.deserialize("{ \"cursor\": 1 }"));
    final StandardSyncState connectionState1 = new StandardSyncState().withConnectionId(connectionId).withState(state1);
    final State state2 = new State().withState(Jsons.deserialize("{ \"cursor\": 2 }"));
    final StandardSyncState connectionState2 = new StandardSyncState().withConnectionId(connectionId).withState(state2);

    configRepository.updateConnectionState(connectionId, state1);
    verify(configPersistence, times(1)).writeConfig(ConfigSchema.STANDARD_SYNC_STATE, connectionId.toString(), connectionState1);
    configRepository.updateConnectionState(connectionId, state2);
    verify(configPersistence, times(1)).writeConfig(ConfigSchema.STANDARD_SYNC_STATE, connectionId.toString(), connectionState2);
  }

  @Test
  void testDeleteSourceDefinitionAndAssociations() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardSourceDefinition sourceDefToDelete = new StandardSourceDefinition().withSourceDefinitionId(UUID.randomUUID());
    final StandardSourceDefinition sourceDefToStay = new StandardSourceDefinition().withSourceDefinitionId(UUID.randomUUID());

    final SourceConnection sourceConnectionToDelete = new SourceConnection().withSourceId(UUID.randomUUID())
        .withSourceDefinitionId(sourceDefToDelete.getSourceDefinitionId());
    final SourceConnection sourceConnectionToStay = new SourceConnection().withSourceId(UUID.randomUUID())
        .withSourceDefinitionId(sourceDefToStay.getSourceDefinitionId());
    when(configPersistence.listConfigs(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class)).thenReturn(List.of(
        sourceConnectionToDelete,
        sourceConnectionToStay));
    when(configPersistence.listConfigs(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class)).thenReturn(List.of());

    final StandardSync syncToDelete = new StandardSync().withConnectionId(UUID.randomUUID()).withSourceId(sourceConnectionToDelete.getSourceId())
        .withDestinationId(UUID.randomUUID());
    final StandardSync syncToStay = new StandardSync().withConnectionId(UUID.randomUUID()).withSourceId(sourceConnectionToStay.getSourceId())
        .withDestinationId(UUID.randomUUID());

    when(configPersistence.listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class)).thenReturn(List.of(syncToDelete, syncToStay));

    configRepository.deleteSourceDefinitionAndAssociations(sourceDefToDelete.getSourceDefinitionId());

    // verify that all records associated with sourceDefToDelete were deleted
    verify(configPersistence, times(1)).deleteConfig(ConfigSchema.STANDARD_SYNC, syncToDelete.getConnectionId().toString());
    verify(configPersistence, times(1)).deleteConfig(ConfigSchema.SOURCE_CONNECTION, sourceConnectionToDelete.getSourceId().toString());
    verify(configPersistence, times(1)).deleteConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceDefToDelete.getSourceDefinitionId().toString());

    // verify that none of the records associated with sourceDefToStay were deleted
    verify(configPersistence, never()).deleteConfig(ConfigSchema.STANDARD_SYNC, syncToStay.getConnectionId().toString());
    verify(configPersistence, never()).deleteConfig(ConfigSchema.SOURCE_CONNECTION, sourceConnectionToStay.getSourceId().toString());
    verify(configPersistence, never()).deleteConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceDefToStay.getSourceDefinitionId().toString());
  }

  @Test
  void testDeleteDestinationDefinitionAndAssociations() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardDestinationDefinition destDefToDelete = new StandardDestinationDefinition().withDestinationDefinitionId(UUID.randomUUID());
    final StandardDestinationDefinition destDefToStay = new StandardDestinationDefinition().withDestinationDefinitionId(UUID.randomUUID());

    final DestinationConnection destConnectionToDelete = new DestinationConnection().withDestinationId(UUID.randomUUID())
        .withDestinationDefinitionId(destDefToDelete.getDestinationDefinitionId());
    final DestinationConnection destConnectionToStay = new DestinationConnection().withDestinationId(UUID.randomUUID())
        .withDestinationDefinitionId(destDefToStay.getDestinationDefinitionId());
    when(configPersistence.listConfigs(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class)).thenReturn(List.of(
        destConnectionToDelete,
        destConnectionToStay));
    when(configPersistence.listConfigs(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class)).thenReturn(List.of());

    final StandardSync syncToDelete = new StandardSync().withConnectionId(UUID.randomUUID())
        .withDestinationId(destConnectionToDelete.getDestinationId())
        .withSourceId(UUID.randomUUID());
    final StandardSync syncToStay = new StandardSync().withConnectionId(UUID.randomUUID()).withDestinationId(destConnectionToStay.getDestinationId())
        .withSourceId(UUID.randomUUID());

    when(configPersistence.listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class)).thenReturn(List.of(syncToDelete, syncToStay));

    configRepository.deleteDestinationDefinitionAndAssociations(destDefToDelete.getDestinationDefinitionId());

    // verify that all records associated with destDefToDelete were deleted
    verify(configPersistence, times(1)).deleteConfig(ConfigSchema.STANDARD_SYNC, syncToDelete.getConnectionId().toString());
    verify(configPersistence, times(1)).deleteConfig(ConfigSchema.DESTINATION_CONNECTION, destConnectionToDelete.getDestinationId().toString());
    verify(configPersistence, times(1)).deleteConfig(
        ConfigSchema.STANDARD_DESTINATION_DEFINITION,
        destDefToDelete.getDestinationDefinitionId().toString());

    // verify that none of the records associated with destDefToStay were deleted
    verify(configPersistence, never()).deleteConfig(ConfigSchema.STANDARD_SYNC, syncToStay.getConnectionId().toString());
    verify(configPersistence, never()).deleteConfig(ConfigSchema.DESTINATION_CONNECTION, destConnectionToStay.getDestinationId().toString());
    verify(configPersistence, never()).deleteConfig(
        ConfigSchema.STANDARD_DESTINATION_DEFINITION,
        destDefToStay.getDestinationDefinitionId().toString());
  }

  @Test
  public void testUpdateFeedback() throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardWorkspace workspace = new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withTombstone(false);
    doReturn(workspace)
        .when(configRepository)
        .getStandardWorkspace(WORKSPACE_ID, false);

    configRepository.setFeedback(WORKSPACE_ID);

    assertTrue(workspace.getFeedbackDone());
    verify(configPersistence).writeConfig(ConfigSchema.STANDARD_WORKSPACE, workspace.getWorkspaceId().toString(), workspace);
  }

}
