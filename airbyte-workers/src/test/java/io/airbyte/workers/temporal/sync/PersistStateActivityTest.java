/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.generated.StateApi;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.ConnectionState;
import io.airbyte.api.client.model.generated.ConnectionStateCreateOrUpdate;
import io.airbyte.api.client.model.generated.ConnectionStateType;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.config.StateType;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockedStatic;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class PersistStateActivityTest {

  private final static UUID CONNECTION_ID = UUID.randomUUID();
  private static final String STREAM_A = "a";
  private static final String STREAM_A_NAMESPACE = "a1";
  private static final String STREAM_B = "b";
  private static final String STREAM_C = "c";

  @Mock
  AirbyteApiClient airbyteApiClient;

  @Mock
  StateApi stateApi;

  @Mock
  FeatureFlags featureFlags;

  MockedStatic<StateMessageHelper> mockedStateMessageHelper;

  @InjectMocks
  PersistStateActivityImpl persistStateActivity;

  @BeforeEach
  void init() {
    Mockito.lenient().when(airbyteApiClient.getStateApi()).thenReturn(stateApi);

    mockedStateMessageHelper = Mockito.mockStatic(StateMessageHelper.class, Mockito.CALLS_REAL_METHODS);
  }

  @AfterEach
  public void teardown() {
    mockedStateMessageHelper.close();
  }

  @Test
  void testPersistEmpty() {
    persistStateActivity.persist(CONNECTION_ID, new StandardSyncOutput(), new ConfiguredAirbyteCatalog());

    Mockito.verifyNoInteractions(airbyteApiClient);
  }

  @Test
  void testPersist() throws ApiException {
    when(featureFlags.useStreamCapableState()).thenReturn(true);

    final JsonNode jsonState = Jsons.jsonNode(Map.ofEntries(
        Map.entry("some", "state")));

    final State state = new State().withState(jsonState);

    persistStateActivity.persist(CONNECTION_ID, new StandardSyncOutput().withState(state), new ConfiguredAirbyteCatalog());

    // The ser/der of the state into a state wrapper is tested in StateMessageHelperTest
    Mockito.verify(stateApi).createOrUpdateState(any(ConnectionStateCreateOrUpdate.class));
  }

  // For per-stream state, we expect there to be state for each stream within the configured catalog
  // input into a job
  // This test is to ensure that we correctly throw an error if not every stream in the configured
  // catalog has a state message when migrating from Legacy to Per-Stream
  @Test
  void testPersistWithValidMissingStateDuringMigration() throws ApiException {
    final ConfiguredAirbyteStream stream =
        new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_A).withNamespace(STREAM_A_NAMESPACE));
    final ConfiguredAirbyteStream stream2 = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_B));

    final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(CatalogHelpers.extractDescriptor(stream))
                .withStreamState(Jsons.emptyObject()));
    final JsonNode jsonState = Jsons.jsonNode(List.of(stateMessage1));
    final State state = new State().withState(jsonState);

    final ConfiguredAirbyteCatalog migrationConfiguredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream, stream2));
    final StandardSyncOutput syncOutput = new StandardSyncOutput().withState(state);
    when(featureFlags.useStreamCapableState()).thenReturn(true);

    mockedStateMessageHelper.when(() -> StateMessageHelper.isMigration(Mockito.eq(StateType.STREAM), any(StateType.class))).thenReturn(true);
    persistStateActivity.persist(CONNECTION_ID, syncOutput, migrationConfiguredCatalog);
    Mockito.verify(stateApi).createOrUpdateState(any(ConnectionStateCreateOrUpdate.class));
  }

  @Test
  void testPersistWithValidStateDuringMigration() throws ApiException {
    final ConfiguredAirbyteStream stream =
        new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_A).withNamespace(STREAM_A_NAMESPACE));
    final ConfiguredAirbyteStream stream2 = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_B));
    final ConfiguredAirbyteStream stream3 =
        new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_C)).withSyncMode(SyncMode.FULL_REFRESH);

    final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(CatalogHelpers.extractDescriptor(stream))
                .withStreamState(Jsons.emptyObject()));
    final AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(CatalogHelpers.extractDescriptor(stream2)));
    final JsonNode jsonState = Jsons.jsonNode(List.of(stateMessage1, stateMessage2));
    final State state = new State().withState(jsonState);

    final ConfiguredAirbyteCatalog migrationConfiguredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream, stream2, stream3));
    final StandardSyncOutput syncOutput = new StandardSyncOutput().withState(state);
    when(featureFlags.useStreamCapableState()).thenReturn(true);
    mockedStateMessageHelper.when(() -> StateMessageHelper.isMigration(Mockito.eq(StateType.STREAM), any(StateType.class))).thenReturn(true);
    persistStateActivity.persist(CONNECTION_ID, syncOutput, migrationConfiguredCatalog);
    Mockito.verify(stateApi).createOrUpdateState(any(ConnectionStateCreateOrUpdate.class));
  }

  // Global stream states do not need to be validated during the migration to per-stream state
  @Test
  void testPersistWithGlobalStateDuringMigration() throws ApiException {
    final ConfiguredAirbyteStream stream =
        new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_A).withNamespace(STREAM_A_NAMESPACE));
    final ConfiguredAirbyteStream stream2 = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_B));

    final AirbyteStateMessage stateMessage = new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL);
    final JsonNode jsonState = Jsons.jsonNode(List.of(stateMessage));
    final State state = new State().withState(jsonState);

    final ConfiguredAirbyteCatalog migrationConfiguredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream, stream2));
    final StandardSyncOutput syncOutput = new StandardSyncOutput().withState(state);
    when(featureFlags.useStreamCapableState()).thenReturn(true);
    mockedStateMessageHelper.when(() -> StateMessageHelper.isMigration(Mockito.eq(StateType.GLOBAL), any(StateType.class))).thenReturn(true);
    persistStateActivity.persist(CONNECTION_ID, syncOutput, migrationConfiguredCatalog);
    final PersistStateActivityImpl persistStateSpy = spy(persistStateActivity);
    Mockito.verify(persistStateSpy, Mockito.times(0)).validateStreamStates(any(), any());
    Mockito.verify(stateApi).createOrUpdateState(any(ConnectionStateCreateOrUpdate.class));
  }

  @Test
  void testPersistWithPerStreamStateDuringMigrationFromEmptyLegacyState() throws ApiException {
    /*
     * This test covers a scenario where a reset is executed before any successful syncs for a
     * connection. When this occurs, an empty, legacy state is stored for the connection.
     */
    final ConfiguredAirbyteStream stream =
        new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_A).withNamespace(STREAM_A_NAMESPACE));
    final ConfiguredAirbyteStream stream2 = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_B));
    final ConfiguredAirbyteStream stream3 =
        new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_C)).withSyncMode(SyncMode.FULL_REFRESH);

    final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(CatalogHelpers.extractDescriptor(stream))
                .withStreamState(Jsons.emptyObject()));
    final AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(CatalogHelpers.extractDescriptor(stream2)));
    final JsonNode jsonState = Jsons.jsonNode(List.of(stateMessage1, stateMessage2));
    final State state = new State().withState(jsonState);

    final AirbyteApiClient airbyteApiClient1 = mock(AirbyteApiClient.class);
    final StateApi stateApi1 = mock(StateApi.class);
    final ConnectionState connectionState = mock(ConnectionState.class);
    Mockito.lenient().when(connectionState.getStateType()).thenReturn(ConnectionStateType.LEGACY);
    Mockito.lenient().when(connectionState.getState()).thenReturn(Jsons.emptyObject());
    when(stateApi1.getState(any(ConnectionIdRequestBody.class))).thenReturn(connectionState);
    Mockito.lenient().when(airbyteApiClient1.getStateApi()).thenReturn(stateApi1);

    final ConfiguredAirbyteCatalog migrationConfiguredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream, stream2, stream3));
    final StandardSyncOutput syncOutput = new StandardSyncOutput().withState(state);
    when(featureFlags.useStreamCapableState()).thenReturn(true);

    final PersistStateActivityImpl persistStateActivity1 = new PersistStateActivityImpl(airbyteApiClient1, featureFlags);

    persistStateActivity1.persist(CONNECTION_ID, syncOutput, migrationConfiguredCatalog);

    Mockito.verify(stateApi1).createOrUpdateState(any(ConnectionStateCreateOrUpdate.class));
  }

  @Test
  void testPersistWithPerStreamStateDuringMigrationFromNullLegacyState() throws ApiException {
    final ConfiguredAirbyteStream stream =
        new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_A).withNamespace(STREAM_A_NAMESPACE));
    final ConfiguredAirbyteStream stream2 = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_B));
    final ConfiguredAirbyteStream stream3 =
        new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_C)).withSyncMode(SyncMode.FULL_REFRESH);

    final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(CatalogHelpers.extractDescriptor(stream))
                .withStreamState(Jsons.emptyObject()));
    final AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(CatalogHelpers.extractDescriptor(stream2)));
    final JsonNode jsonState = Jsons.jsonNode(List.of(stateMessage1, stateMessage2));
    final State state = new State().withState(jsonState);

    final AirbyteApiClient airbyteApiClient1 = mock(AirbyteApiClient.class);
    final StateApi stateApi1 = mock(StateApi.class);
    final ConnectionState connectionState = mock(ConnectionState.class);
    Mockito.lenient().when(connectionState.getStateType()).thenReturn(ConnectionStateType.LEGACY);
    Mockito.lenient().when(connectionState.getState()).thenReturn(null);
    when(stateApi1.getState(any(ConnectionIdRequestBody.class))).thenReturn(connectionState);
    Mockito.lenient().when(airbyteApiClient1.getStateApi()).thenReturn(stateApi1);

    final ConfiguredAirbyteCatalog migrationConfiguredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream, stream2, stream3));
    final StandardSyncOutput syncOutput = new StandardSyncOutput().withState(state);
    when(featureFlags.useStreamCapableState()).thenReturn(true);

    final PersistStateActivityImpl persistStateActivity1 = new PersistStateActivityImpl(airbyteApiClient1, featureFlags);

    persistStateActivity1.persist(CONNECTION_ID, syncOutput, migrationConfiguredCatalog);

    Mockito.verify(stateApi1).createOrUpdateState(any(ConnectionStateCreateOrUpdate.class));
  }

  @Test
  void testPersistWithPerStreamStateDuringMigrationWithNoPreviousState() throws ApiException {
    final ConfiguredAirbyteStream stream =
        new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_A).withNamespace(STREAM_A_NAMESPACE));
    final ConfiguredAirbyteStream stream2 = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_B));
    final ConfiguredAirbyteStream stream3 =
        new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName(STREAM_C)).withSyncMode(SyncMode.FULL_REFRESH);

    final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(CatalogHelpers.extractDescriptor(stream))
                .withStreamState(Jsons.emptyObject()));
    final AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(CatalogHelpers.extractDescriptor(stream2)));
    final JsonNode jsonState = Jsons.jsonNode(List.of(stateMessage1, stateMessage2));
    final State state = new State().withState(jsonState);

    final AirbyteApiClient airbyteApiClient1 = mock(AirbyteApiClient.class);
    final StateApi stateApi1 = mock(StateApi.class);
    when(stateApi1.getState(any(ConnectionIdRequestBody.class))).thenReturn(null);
    Mockito.lenient().when(airbyteApiClient1.getStateApi()).thenReturn(stateApi1);

    final ConfiguredAirbyteCatalog migrationConfiguredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream, stream2, stream3));
    final StandardSyncOutput syncOutput = new StandardSyncOutput().withState(state);
    when(featureFlags.useStreamCapableState()).thenReturn(true);

    final PersistStateActivityImpl persistStateActivity1 = new PersistStateActivityImpl(airbyteApiClient1, featureFlags);

    persistStateActivity1.persist(CONNECTION_ID, syncOutput, migrationConfiguredCatalog);

    Mockito.verify(stateApi1).createOrUpdateState(any(ConnectionStateCreateOrUpdate.class));
  }

}
