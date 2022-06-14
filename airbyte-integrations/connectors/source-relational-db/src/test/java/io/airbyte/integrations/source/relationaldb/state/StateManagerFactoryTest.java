/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.List;
import java.util.function.Supplier;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link StateManagerFactory} class.
 */
public class StateManagerFactoryTest {

  private static final String NAMESPACE = "namespace";
  private static final String NAME = "name";

  private static final Supplier<AirbyteStateType> GLOBAL_STATE_TYPE = () -> AirbyteStateType.GLOBAL;

  private static final Supplier<AirbyteStateType> LEGACY_STATE_TYPE = () -> AirbyteStateType.LEGACY;

  private static final Supplier<AirbyteStateType> STREAM_STATE_TYPE = () -> AirbyteStateType.STREAM;

  @Test
  void testNullOrEmptyState() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(null, catalog, GLOBAL_STATE_TYPE);
    });

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(List.of(), catalog, GLOBAL_STATE_TYPE);
    });

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(null, catalog, LEGACY_STATE_TYPE);
    });

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(List.of(), catalog, LEGACY_STATE_TYPE);
    });

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(null, catalog, STREAM_STATE_TYPE);
    });

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(List.of(), catalog, STREAM_STATE_TYPE);
    });
  }

  @Test
  void testLegacyStateManagerCreationFromAirbyteStateMessage() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = mock(AirbyteStateMessage.class);
    when(airbyteStateMessage.getData()).thenReturn(Jsons.jsonNode(new DbState()));

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, LEGACY_STATE_TYPE);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(LegacyStateManager.class, stateManager.getClass());
  }

  @Test
  void testGlobalStateManagerCreation() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteGlobalState globalState =
        new AirbyteGlobalState().withSharedState(Jsons.jsonNode(new DbState().withCdcState(new CdcState().withState(Jsons.jsonNode(new DbState())))))
            .withStreamStates(List.of(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withNamespace(NAMESPACE).withName(NAME))
                .withStreamState(Jsons.jsonNode(new DbStreamState()))));
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage().withStateType(AirbyteStateType.GLOBAL).withGlobal(globalState);

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, GLOBAL_STATE_TYPE);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(GlobalStateManager.class, stateManager.getClass());
  }

  @Test
  void testGlobalStateManagerCreationFromLegacyState() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final CdcState cdcState = new CdcState();
    final DbState dbState = new DbState()
        .withCdcState(cdcState)
        .withStreams(List.of(new DbStreamState().withStreamName(NAME).withStreamNamespace(NAMESPACE)));
    final AirbyteStateMessage airbyteStateMessage =
        new AirbyteStateMessage().withStateType(AirbyteStateType.LEGACY).withData(Jsons.jsonNode(dbState));

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, GLOBAL_STATE_TYPE);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(GlobalStateManager.class, stateManager.getClass());
  }

  @Test
  void testGlobalStateManagerCreationFromStreamState() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage().withStateType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName(NAME).withNamespace(
            NAMESPACE)).withStreamState(Jsons.jsonNode(new DbStreamState())));

    Assertions.assertThrows(IllegalArgumentException.class,
        () -> StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, GLOBAL_STATE_TYPE));
  }

  @Test
  void testGlobalStateManagerCreationWithLegacyDataPresent() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteGlobalState globalState =
        new AirbyteGlobalState().withSharedState(Jsons.jsonNode(new DbState().withCdcState(new CdcState().withState(Jsons.jsonNode(new DbState())))))
            .withStreamStates(List.of(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withNamespace(NAMESPACE).withName(NAME))
                .withStreamState(Jsons.jsonNode(new DbStreamState()))));
    final AirbyteStateMessage airbyteStateMessage =
        new AirbyteStateMessage().withStateType(AirbyteStateType.GLOBAL).withGlobal(globalState).withData(Jsons.jsonNode(new DbState()));

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, GLOBAL_STATE_TYPE);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(GlobalStateManager.class, stateManager.getClass());
  }

  @Test
  void testStreamStateManagerCreation() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage().withStateType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName(NAME).withNamespace(
            NAMESPACE)).withStreamState(Jsons.jsonNode(new DbStreamState())));

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, STREAM_STATE_TYPE);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(StreamStateManager.class, stateManager.getClass());
  }

  @Test
  void testStreamStateManagerCreationFromLegacy() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final CdcState cdcState = new CdcState();
    final DbState dbState = new DbState()
        .withCdcState(cdcState)
        .withStreams(List.of(new DbStreamState().withStreamName(NAME).withStreamNamespace(NAMESPACE)));
    final AirbyteStateMessage airbyteStateMessage =
        new AirbyteStateMessage().withStateType(AirbyteStateType.LEGACY).withData(Jsons.jsonNode(dbState));

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, STREAM_STATE_TYPE);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(StreamStateManager.class, stateManager.getClass());
  }

  @Test
  void testStreamStateManagerCreationFromGlobal() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteGlobalState globalState =
        new AirbyteGlobalState().withSharedState(Jsons.jsonNode(new DbState().withCdcState(new CdcState().withState(Jsons.jsonNode(new DbState())))))
            .withStreamStates(List.of(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withNamespace(NAMESPACE).withName(NAME))
                .withStreamState(Jsons.jsonNode(new DbStreamState()))));
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage().withStateType(AirbyteStateType.GLOBAL).withGlobal(globalState);

    Assertions.assertThrows(IllegalArgumentException.class, () ->  StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, STREAM_STATE_TYPE));
  }

  @Test
  void testStreamStateManagerCreationWithLegacyDataPresent() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage().withStateType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName(NAME).withNamespace(
            NAMESPACE)).withStreamState(Jsons.jsonNode(new DbStreamState())))
        .withData(Jsons.jsonNode(new DbState()));

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, STREAM_STATE_TYPE);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(StreamStateManager.class, stateManager.getClass());
  }

}
