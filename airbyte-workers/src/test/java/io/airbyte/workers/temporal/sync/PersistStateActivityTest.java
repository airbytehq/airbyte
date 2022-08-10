/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.generated.ConnectionApi;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.ConnectionState;
import io.airbyte.api.client.model.generated.ConnectionStateCreateOrUpdate;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.helpers.StateConverter;
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
import java.util.Optional;
import java.util.UUID;
import org.elasticsearch.common.collect.Map;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
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

  @Mock
  AirbyteApiClient airbyteApiClient;

  @Mock
  ConnectionApi connectionApi;

  @Mock
  FeatureFlags featureFlags;

  @Mock
  StateWrapper mockStateWrapper;

  @Mock
  ConnectionState mockClientConnectionState;

  MockedStatic<StateMessageHelper> mockedStateMessageHelper;
  MockedStatic<StateConverter> mockedStateConverter;

  @InjectMocks
  PersistStateActivityImpl persistStateActivity;

  @BeforeEach
  public void beforeEach() {
    Mockito.lenient().when(airbyteApiClient.getConnectionApi()).thenReturn(connectionApi);

    mockedStateMessageHelper = Mockito.mockStatic(StateMessageHelper.class);
    mockedStateMessageHelper.when(() -> StateMessageHelper.getTypedState(any(JsonNode.class), anyBoolean()))
        .thenReturn(Optional.of(mockStateWrapper));

    mockedStateConverter = Mockito.mockStatic(StateConverter.class);
    mockedStateConverter.when(() -> StateConverter.toClient(eq(CONNECTION_ID), any(StateWrapper.class)))
        .thenReturn(mockClientConnectionState);
  }

  @AfterEach
  public void teardown() {
    mockedStateMessageHelper.close();
    mockedStateConverter.close();
  }

  @Test
  void testPersistEmpty() {
    persistStateActivity.persist(CONNECTION_ID, new StandardSyncOutput(), new ConfiguredAirbyteCatalog());

    Mockito.verifyNoInteractions(airbyteApiClient);
  }

  @Test
  void testPersist() throws ApiException {
    Mockito.when(featureFlags.useStreamCapableState()).thenReturn(true);

    final ConnectionState prevConnectionState = Mockito.mock(ConnectionState.class);
    Mockito.when(connectionApi.getState(eq(new ConnectionIdRequestBody().connectionId(CONNECTION_ID)))).thenReturn(prevConnectionState);

    final JsonNode jsonState = Jsons.jsonNode(Map.ofEntries(
        Map.entry("some", "state")));

    final State state = new State().withState(jsonState);

    persistStateActivity.persist(CONNECTION_ID, new StandardSyncOutput().withState(state), new ConfiguredAirbyteCatalog());

    verifyStateHelperCalls(state, true, CONNECTION_ID);
    verifyApiCalls(CONNECTION_ID);
  }

  @Nested
  @DisplayName("DuringMigration")
  class DuringMigration {

    @Mock
    ConnectionState previousState;

    @BeforeEach
    public void init() throws ApiException {
      Mockito.when(connectionApi.getState(any())).thenReturn(previousState);

      mockedStateMessageHelper.when(() -> StateMessageHelper.isMigration(any(), any())).thenReturn(true);
    }

    // For per-stream state, we expect there to be state for each stream within the configured catalog
    // input into a job
    // This test is to ensure that we correctly throw an error if not every stream in the configured
    // catalog has a state message when migrating from Legacy to Per-Stream
    @Test
    public void testPersistWithValidMissingState() throws ApiException {
      final ConfiguredAirbyteStream stream = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName("a").withNamespace("a1"));
      final ConfiguredAirbyteStream stream2 = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName("b"));

      final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(
              new AirbyteStreamState().withStreamDescriptor(CatalogHelpers.extractDescriptor(stream))
                  .withStreamState(Jsons.emptyObject()));
      final JsonNode jsonState = Jsons.jsonNode(List.of(stateMessage1));
      final State state = new State().withState(jsonState);

      final ConfiguredAirbyteCatalog migrationConfiguredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream, stream2));
      final StandardSyncOutput syncOutput = new StandardSyncOutput().withState(state);
      Mockito.when(featureFlags.useStreamCapableState()).thenReturn(true);

      persistStateActivity.persist(CONNECTION_ID, syncOutput, migrationConfiguredCatalog);

      verifyStateHelperCalls(state, true, CONNECTION_ID);
      verifyApiCalls(CONNECTION_ID);
    }

    @Test
    void testPersistWithValidState() throws ApiException {
      final ConfiguredAirbyteStream stream = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName("a").withNamespace("a1"));
      final ConfiguredAirbyteStream stream2 = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName("b"));
      final ConfiguredAirbyteStream stream3 =
          new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName("c")).withSyncMode(SyncMode.FULL_REFRESH);

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
      Mockito.when(featureFlags.useStreamCapableState()).thenReturn(true);

      persistStateActivity.persist(CONNECTION_ID, syncOutput, migrationConfiguredCatalog);

      verifyStateHelperCalls(state, true, CONNECTION_ID);
      verifyApiCalls(CONNECTION_ID);
    }

    // Global stream states do not need to be validated during the migration to per-stream state
    @Test
    void testPersistWithGlobalState() throws ApiException {
      final ConfiguredAirbyteStream stream = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName("a").withNamespace("a1"));
      final ConfiguredAirbyteStream stream2 = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName("b"));

      final AirbyteStateMessage stateMessage = new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL);
      final JsonNode jsonState = Jsons.jsonNode(List.of(stateMessage));
      final State state = new State().withState(jsonState);

      final ConfiguredAirbyteCatalog migrationConfiguredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream, stream2));
      final StandardSyncOutput syncOutput = new StandardSyncOutput().withState(state);
      Mockito.when(featureFlags.useStreamCapableState()).thenReturn(true);

      final PersistStateActivityImpl persistStateSpy = spy(persistStateActivity);
      persistStateActivity.persist(CONNECTION_ID, syncOutput, migrationConfiguredCatalog);

      Mockito.verify(persistStateSpy, times(0)).validateStreamStates(Mockito.any(), Mockito.any());
      verifyStateHelperCalls(state, true, CONNECTION_ID);
      verifyApiCalls(CONNECTION_ID);
    }
  }

  private void verifyStateHelperCalls(final State state, final Boolean useStreamCapableState, final UUID connectionId) {
    mockedStateMessageHelper.verify(() -> StateMessageHelper.getTypedState(state.getState(), useStreamCapableState), times(1));
    mockedStateConverter.verify(() -> StateConverter.toClient(connectionId, mockStateWrapper), times(1));
  }

  private void verifyApiCalls(final UUID connectionId) throws ApiException {
    final ConnectionIdRequestBody expectedGetStateBody = new ConnectionIdRequestBody().connectionId(connectionId);

    final ConnectionStateCreateOrUpdate expectedUpdateBody = new ConnectionStateCreateOrUpdate()
        .connectionId(connectionId)
        .connectionState(mockClientConnectionState);

    Mockito.verify(connectionApi, times(1)).getState(expectedGetStateBody);
    Mockito.verify(connectionApi).createOrUpdateState(expectedUpdateBody);
  }

}
