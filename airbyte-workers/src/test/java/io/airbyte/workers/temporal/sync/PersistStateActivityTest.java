/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

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
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.StreamDescriptor;
import java.io.IOException;
import java.util.List;
import java.util.UUID;
import org.elasticsearch.common.collect.Map;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
public class PersistStateActivityTest {

  private final static UUID CONNECTION_ID = UUID.randomUUID();

  @Mock
  StatePersistence statePersistence;

  @Mock
  FeatureFlags featureFlags;

  @InjectMocks
  PersistStateActivityImpl persistStateActivity;

  @Test
  public void testPersistEmpty() {
    persistStateActivity.persist(CONNECTION_ID, new StandardSyncOutput());

    Mockito.verifyNoInteractions(statePersistence);
  }

  @Test
  public void testPersist() throws IOException {
    Mockito.when(featureFlags.useStreamCapableState()).thenReturn(true);

    final JsonNode jsonState = Jsons.jsonNode(Map.ofEntries(
        Map.entry("some", "state")));

    final State state = new State().withState(jsonState);

    persistStateActivity.persist(CONNECTION_ID, new StandardSyncOutput().withState(state));

    // The ser/der of the state into a state wrapper is tested in StateMessageHelperTest
    Mockito.verify(statePersistence).updateOrCreateState(Mockito.eq(CONNECTION_ID), Mockito.any(StateWrapper.class));
  }

  @Test
  public void testPersistWithInvalidStateDuringMigration() throws IOException {
    final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a").withNamespace("a1"))
                .withStreamState(Jsons.emptyObject()));
    final JsonNode jsonState = Jsons.jsonNode(List.of(stateMessage1));
    final State state = new State().withState(jsonState);

    final ConfiguredAirbyteStream stream = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName("a").withNamespace("a1"));
    final ConfiguredAirbyteStream stream2 = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName("b"));
    final ConfiguredAirbyteCatalog migrationConfiguredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream, stream2));
    final StandardSyncOutput syncOutput = new StandardSyncOutput().withState(state).withOutputCatalog(migrationConfiguredCatalog);
    Mockito.when(featureFlags.useStreamCapableState()).thenReturn(true);
    Mockito.when(statePersistence.isMigration(CONNECTION_ID, StateType.STREAM)).thenReturn(true);
    Assertions.assertThrows(IllegalStateException.class, () -> persistStateActivity.persist(CONNECTION_ID, syncOutput));
  }

  @Test
  public void testPersistWithValidStateDuringMigration() throws IOException {
    final AirbyteStateMessage stateMessage1 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("a").withNamespace("a1"))
                .withStreamState(Jsons.emptyObject()));
    final AirbyteStateMessage stateMessage2 = new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName("b")).withStreamState(Jsons.emptyObject()));
    final JsonNode jsonState = Jsons.jsonNode(List.of(stateMessage1, stateMessage2));
    final State state = new State().withState(jsonState);

    final ConfiguredAirbyteStream stream = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName("a").withNamespace("a1"));
    final ConfiguredAirbyteStream stream2 = new ConfiguredAirbyteStream().withStream(new AirbyteStream().withName("b"));
    final ConfiguredAirbyteCatalog migrationConfiguredCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream, stream2));
    final StandardSyncOutput syncOutput = new StandardSyncOutput().withState(state).withOutputCatalog(migrationConfiguredCatalog);
    Mockito.when(featureFlags.useStreamCapableState()).thenReturn(true);
    Mockito.when(statePersistence.isMigration(CONNECTION_ID, StateType.STREAM)).thenReturn(true);
    persistStateActivity.persist(CONNECTION_ID, syncOutput);
  }

}
