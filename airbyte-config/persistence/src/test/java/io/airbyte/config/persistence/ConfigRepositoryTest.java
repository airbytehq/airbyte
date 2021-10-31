/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardSyncState;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.State;
import io.airbyte.config.persistence.split_secrets.MemorySecretPersistence;
import io.airbyte.config.persistence.split_secrets.NoOpSecretsHydrator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ConfigRepositoryTest {

  private static final UUID WORKSPACE_ID = UUID.randomUUID();

  private ConfigPersistence configPersistence;
  private ConfigRepository configRepository;

  @BeforeEach
  void setup() {
    configPersistence = mock(ConfigPersistence.class);
    final var secretPersistence = new MemorySecretPersistence();
    configRepository =
        new ConfigRepository(configPersistence, new NoOpSecretsHydrator(), Optional.of(secretPersistence), Optional.of(secretPersistence));
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

}
