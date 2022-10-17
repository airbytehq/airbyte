/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.elasticsearch.common.collect.Map;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class PersistStateActivityTest {

  private final static UUID CONNECTION_ID = UUID.randomUUID();

  @Mock
  StatePersistence statePersistence;

  @Mock
  FeatureFlags featureFlags;

  @InjectMocks
  PersistStateActivityImpl persistStateActivity;

  @Test
  void testPersistEmpty() {
    persistStateActivity.persist(CONNECTION_ID, new StandardSyncOutput(), new ConfiguredAirbyteCatalog());

    Mockito.verifyNoInteractions(statePersistence);
  }

  @Test
  void testPersist() throws IOException {
    Mockito.when(featureFlags.useStreamCapableState()).thenReturn(true);

    final JsonNode jsonState = Jsons.jsonNode(Map.ofEntries(
        Map.entry("some", "state")));

    final State state = new State().withState(jsonState);

    persistStateActivity.persist(CONNECTION_ID, new StandardSyncOutput().withState(state), new ConfiguredAirbyteCatalog());

    // The ser/der of the state into a state wrapper is tested in StateMessageHelperTest
    Mockito.verify(statePersistence).updateOrCreateState(Mockito.eq(CONNECTION_ID), Mockito.any(StateWrapper.class));
  }

  // For per-stream state, we expect there to be state for each stream within the configured catalog
  // input into a job
  // This test is to ensure that we correctly throw an error if not every stream in the configured
  // catalog has a state message when migrating from Legacy to Per-Stream
  @Test
  void testPersistWithValidMissingStateDuringMigration() throws IOException {
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
    Mockito.when(statePersistence.isMigration(Mockito.eq(CONNECTION_ID), Mockito.eq(StateType.STREAM), Mockito.any(Optional.class))).thenReturn(true);
    persistStateActivity.persist(CONNECTION_ID, syncOutput, migrationConfiguredCatalog);
    Mockito.verify(statePersistence).updateOrCreateState(Mockito.eq(CONNECTION_ID), Mockito.any(StateWrapper.class));
  }

  @Test
  void testPersistWithValidStateDuringMigration() throws IOException {
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
    Mockito.when(statePersistence.isMigration(Mockito.eq(CONNECTION_ID), Mockito.eq(StateType.STREAM), Mockito.any(Optional.class))).thenReturn(true);
    persistStateActivity.persist(CONNECTION_ID, syncOutput, migrationConfiguredCatalog);
    Mockito.verify(statePersistence).updateOrCreateState(Mockito.eq(CONNECTION_ID), Mockito.any(StateWrapper.class));
  }

  // Global stream states do not need to be validated during the migration to per-stream state
  @Test
  void testPersistWithGlobalStateDuringMigration() throws IOException {
    final ConfiguredAirbyteStream stream = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName("a").withNamespace("a1"));
    final ConfiguredAirbyteStream stream2 = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName("b"));

    final AirbyteStateMessage stateMessage = new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL);
    final JsonNode jsonState = Jsons.jsonNode(List.of(stateMessage));
    final State state = new State().withState(jsonState);

    final ConfiguredAirbyteCatalog migrationConfiguredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream, stream2));
    final StandardSyncOutput syncOutput = new StandardSyncOutput().withState(state);
    Mockito.when(featureFlags.useStreamCapableState()).thenReturn(true);
    Mockito.when(statePersistence.isMigration(Mockito.eq(CONNECTION_ID), Mockito.eq(StateType.GLOBAL), Mockito.any(Optional.class))).thenReturn(true);
    persistStateActivity.persist(CONNECTION_ID, syncOutput, migrationConfiguredCatalog);
    final PersistStateActivityImpl persistStateSpy = spy(persistStateActivity);
    Mockito.verify(persistStateSpy, Mockito.times(0)).validateStreamStates(Mockito.any(), Mockito.any());
    Mockito.verify(statePersistence).updateOrCreateState(Mockito.eq(CONNECTION_ID), Mockito.any(StateWrapper.class));
  }

}
