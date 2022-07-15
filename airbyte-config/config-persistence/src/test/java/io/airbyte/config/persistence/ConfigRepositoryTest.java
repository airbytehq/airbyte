/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
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
import io.airbyte.db.Database;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.jooq.Result;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

@SuppressWarnings({"PMD.LongVariable", "PMD.AvoidInstantiatingObjectsInLoops"})
class ConfigRepositoryTest {

  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID = UUID.randomUUID();
  private static final UUID DESTINATION_DEFINITION_ID = UUID.randomUUID();

  private ConfigPersistence configPersistence;
  private ConfigRepository configRepository;
  private Database database;

  @BeforeEach
  void setup() {
    configPersistence = mock(ConfigPersistence.class);
    database = mock(Database.class);
    configRepository = spy(new ConfigRepository(configPersistence, database));
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
  void testSourceDefinitionWithNullTombstone() throws JsonValidationException, ConfigNotFoundException, IOException {
    assertReturnsSourceDefinition(new StandardSourceDefinition().withSourceDefinitionId(SOURCE_DEFINITION_ID));
  }

  @Test
  void testSourceDefinitionWithTrueTombstone() throws JsonValidationException, ConfigNotFoundException, IOException {
    assertReturnsSourceDefinition(new StandardSourceDefinition().withSourceDefinitionId(SOURCE_DEFINITION_ID).withTombstone(true));
  }

  @Test
  void testSourceDefinitionWithFalseTombstone() throws JsonValidationException, ConfigNotFoundException, IOException {
    assertReturnsSourceDefinition(new StandardSourceDefinition().withSourceDefinitionId(SOURCE_DEFINITION_ID).withTombstone(false));
  }

  void assertReturnsSourceDefinition(final StandardSourceDefinition sourceDefinition)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    when(configPersistence.getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, SOURCE_DEFINITION_ID.toString(), StandardSourceDefinition.class))
        .thenReturn(sourceDefinition);

    assertEquals(sourceDefinition, configRepository.getStandardSourceDefinition(SOURCE_DEFINITION_ID));
  }

  @Test
  void testSourceDefinitionFromSource() throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID sourceId = UUID.randomUUID();

    final SourceConnection source = new SourceConnection()
        .withSourceId(sourceId)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID);

    doReturn(source)
        .when(configRepository)
        .getSourceConnection(sourceId);

    configRepository.getSourceDefinitionFromSource(sourceId);
    verify(configRepository).getStandardSourceDefinition(SOURCE_DEFINITION_ID);
  }

  @Test
  void testSourceDefinitionsFromConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID sourceId = UUID.randomUUID();
    final UUID connectionId = UUID.randomUUID();

    final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
        .withSourceDefinitionId(SOURCE_DEFINITION_ID);

    final SourceConnection source = new SourceConnection()
        .withSourceId(sourceId)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID);

    final StandardSync connection = new StandardSync()
        .withSourceId(sourceId)
        .withConnectionId(connectionId);

    doReturn(sourceDefinition)
        .when(configRepository)
        .getStandardSourceDefinition(SOURCE_DEFINITION_ID);
    doReturn(source)
        .when(configRepository)
        .getSourceConnection(sourceId);
    doReturn(connection)
        .when(configRepository)
        .getStandardSync(connectionId);

    configRepository.getSourceDefinitionFromSource(sourceId);

    verify(configRepository).getStandardSourceDefinition(SOURCE_DEFINITION_ID);
  }

  @ParameterizedTest
  @ValueSource(ints = {0, 1, 2, 10})
  void testListStandardSourceDefinitionsHandlesTombstoneSourceDefinitions(final int numSourceDefinitions)
      throws JsonValidationException, IOException {
    final List<StandardSourceDefinition> allSourceDefinitions = new ArrayList<>();
    final List<StandardSourceDefinition> notTombstoneSourceDefinitions = new ArrayList<>();
    for (int i = 0; i < numSourceDefinitions; i++) {
      final boolean isTombstone = i % 2 == 0; // every other is tombstone
      final StandardSourceDefinition sourceDefinition =
          new StandardSourceDefinition().withSourceDefinitionId(UUID.randomUUID()).withTombstone(isTombstone);
      allSourceDefinitions.add(sourceDefinition);
      if (!isTombstone) {
        notTombstoneSourceDefinitions.add(sourceDefinition);
      }
    }
    when(configPersistence.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class))
        .thenReturn(allSourceDefinitions);

    final List<StandardSourceDefinition> returnedSourceDefinitionsWithoutTombstone = configRepository.listStandardSourceDefinitions(false);
    assertEquals(notTombstoneSourceDefinitions, returnedSourceDefinitionsWithoutTombstone);

    final List<StandardSourceDefinition> returnedSourceDefinitionsWithTombstone = configRepository.listStandardSourceDefinitions(true);
    assertEquals(allSourceDefinitions, returnedSourceDefinitionsWithTombstone);
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
  void testDestinationDefinitionWithNullTombstone() throws JsonValidationException, ConfigNotFoundException, IOException {
    assertReturnsDestinationDefinition(new StandardDestinationDefinition().withDestinationDefinitionId(DESTINATION_DEFINITION_ID));
  }

  @Test
  void testDestinationDefinitionWithTrueTombstone() throws JsonValidationException, ConfigNotFoundException, IOException {
    assertReturnsDestinationDefinition(
        new StandardDestinationDefinition().withDestinationDefinitionId(DESTINATION_DEFINITION_ID).withTombstone(true));
  }

  @Test
  void testDestinationDefinitionWithFalseTombstone() throws JsonValidationException, ConfigNotFoundException, IOException {
    assertReturnsDestinationDefinition(
        new StandardDestinationDefinition().withDestinationDefinitionId(DESTINATION_DEFINITION_ID).withTombstone(false));
  }

  void assertReturnsDestinationDefinition(final StandardDestinationDefinition destinationDefinition)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    when(configPersistence.getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, DESTINATION_DEFINITION_ID.toString(),
        StandardDestinationDefinition.class))
            .thenReturn(destinationDefinition);

    assertEquals(destinationDefinition, configRepository.getStandardDestinationDefinition(DESTINATION_DEFINITION_ID));
  }

  @Test
  void testDestinationDefinitionFromDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID destinationId = UUID.randomUUID();

    final DestinationConnection destination = new DestinationConnection()
        .withDestinationId(destinationId)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID);

    doReturn(destination)
        .when(configRepository)
        .getDestinationConnection(destinationId);

    configRepository.getDestinationDefinitionFromDestination(destinationId);
    verify(configRepository).getStandardDestinationDefinition(DESTINATION_DEFINITION_ID);
  }

  @Test
  void testDestinationDefinitionsFromConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID destinationId = UUID.randomUUID();
    final UUID connectionId = UUID.randomUUID();

    final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID);

    final DestinationConnection destination = new DestinationConnection()
        .withDestinationId(destinationId)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID);

    final StandardSync connection = new StandardSync()
        .withDestinationId(destinationId)
        .withConnectionId(connectionId);

    doReturn(destinationDefinition)
        .when(configRepository)
        .getStandardDestinationDefinition(DESTINATION_DEFINITION_ID);
    doReturn(destination)
        .when(configRepository)
        .getDestinationConnection(destinationId);
    doReturn(connection)
        .when(configRepository)
        .getStandardSync(connectionId);

    configRepository.getDestinationDefinitionFromDestination(destinationId);

    verify(configRepository).getStandardDestinationDefinition(DESTINATION_DEFINITION_ID);
  }

  @ParameterizedTest
  @ValueSource(ints = {0, 1, 2, 10})
  void testListStandardDestinationDefinitionsHandlesTombstoneDestinationDefinitions(final int numDestinationDefinitions)
      throws JsonValidationException, IOException {
    final List<StandardDestinationDefinition> allDestinationDefinitions = new ArrayList<>();
    final List<StandardDestinationDefinition> notTombstoneDestinationDefinitions = new ArrayList<>();
    for (int i = 0; i < numDestinationDefinitions; i++) {
      final boolean isTombstone = i % 2 == 0; // every other is tombstone
      final StandardDestinationDefinition destinationDefinition =
          new StandardDestinationDefinition().withDestinationDefinitionId(UUID.randomUUID()).withTombstone(isTombstone);
      allDestinationDefinitions.add(destinationDefinition);
      if (!isTombstone) {
        notTombstoneDestinationDefinitions.add(destinationDefinition);
      }
    }
    when(configPersistence.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
        .thenReturn(allDestinationDefinitions);

    final List<StandardDestinationDefinition> returnedDestinationDefinitionsWithoutTombstone =
        configRepository.listStandardDestinationDefinitions(false);
    assertEquals(notTombstoneDestinationDefinitions, returnedDestinationDefinitionsWithoutTombstone);

    final List<StandardDestinationDefinition> returnedDestinationDefinitionsWithTombstone = configRepository.listStandardDestinationDefinitions(true);
    assertEquals(allDestinationDefinitions, returnedDestinationDefinitionsWithTombstone);
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
  void testDeleteStandardSync() throws IOException, ConfigNotFoundException {
    final UUID connectionId = UUID.randomUUID();
    configRepository.deleteStandardSyncDefinition(connectionId);

    verify(configPersistence).deleteConfig(ConfigSchema.STANDARD_SYNC, connectionId.toString());
  }

  @Test
  void testUpdateFeedback() throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardWorkspace workspace = new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withTombstone(false);
    doReturn(workspace)
        .when(configRepository)
        .getStandardWorkspace(WORKSPACE_ID, false);

    configRepository.setFeedback(WORKSPACE_ID);

    assertTrue(workspace.getFeedbackDone());
    verify(configPersistence).writeConfig(ConfigSchema.STANDARD_WORKSPACE, workspace.getWorkspaceId().toString(), workspace);
  }

  @Test
  void testHealthCheckSuccess() throws SQLException {
    final var mResult = mock(Result.class);
    when(database.query(any())).thenReturn(mResult);

    final var check = configRepository.healthCheck();
    assertTrue(check);
  }

  @Test
  void testHealthCheckFailure() throws SQLException {
    when(database.query(any())).thenThrow(RuntimeException.class);

    final var check = configRepository.healthCheck();
    assertFalse(check);
  }

  @Test
  void testGetAllStreamsForConnection() throws Exception {
    final UUID connectionId = UUID.randomUUID();
    final AirbyteStream airbyteStream = new AirbyteStream().withName("stream1").withNamespace("namespace1");
    final ConfiguredAirbyteStream configuredStream = new ConfiguredAirbyteStream().withStream(airbyteStream);
    final AirbyteStream airbyteStream2 = new AirbyteStream().withName("stream2");
    final ConfiguredAirbyteStream configuredStream2 = new ConfiguredAirbyteStream().withStream(airbyteStream2);
    final ConfiguredAirbyteCatalog configuredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(configuredStream, configuredStream2));

    final StandardSync sync = new StandardSync()
        .withCatalog(configuredCatalog);
    doReturn(sync)
        .when(configRepository)
        .getStandardSync(connectionId);

    final List<StreamDescriptor> result = configRepository.getAllStreamsForConnection(connectionId);
    assertEquals(2, result.size());

    assertTrue(
        result.stream().anyMatch(
            streamDescriptor -> streamDescriptor.getName().equals("stream1") && streamDescriptor.getNamespace().equals("namespace1")));
    assertTrue(
        result.stream().anyMatch(
            streamDescriptor -> streamDescriptor.getName().equals("stream2") && streamDescriptor.getNamespace() == null));

  }

}
