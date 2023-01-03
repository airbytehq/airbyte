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
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.List;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link StateManagerFactory} class.
 */
public class StateManagerFactoryTest {

  private static final String NAMESPACE = "namespace";
  private static final String NAME = "name";

  @Test
  void testNullOrEmptyState() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(AirbyteStateType.GLOBAL, null, catalog);
    });

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(AirbyteStateType.GLOBAL, List.of(), catalog);
    });

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(AirbyteStateType.LEGACY, null, catalog);
    });

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(AirbyteStateType.LEGACY, List.of(), catalog);
    });

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(AirbyteStateType.STREAM, null, catalog);
    });

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(AirbyteStateType.STREAM, List.of(), catalog);
    });
  }

  @Test
  void testLegacyStateManagerCreationFromAirbyteStateMessage() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = mock(AirbyteStateMessage.class);
    when(airbyteStateMessage.getData()).thenReturn(Jsons.jsonNode(new DbState()));

    final StateManager stateManager = StateManagerFactory.createStateManager(AirbyteStateType.LEGACY, List.of(airbyteStateMessage), catalog);

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
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL).withGlobal(globalState);

    final StateManager stateManager = StateManagerFactory.createStateManager(AirbyteStateType.GLOBAL, List.of(airbyteStateMessage), catalog);

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
        new AirbyteStateMessage().withType(AirbyteStateType.LEGACY).withData(Jsons.jsonNode(dbState));

    final StateManager stateManager = StateManagerFactory.createStateManager(AirbyteStateType.GLOBAL, List.of(airbyteStateMessage), catalog);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(GlobalStateManager.class, stateManager.getClass());
  }

  @Test
  void testGlobalStateManagerCreationFromStreamState() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage().withType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName(NAME).withNamespace(
            NAMESPACE)).withStreamState(Jsons.jsonNode(new DbStreamState())));

    Assertions.assertThrows(IllegalArgumentException.class,
        () -> StateManagerFactory.createStateManager(AirbyteStateType.GLOBAL, List.of(airbyteStateMessage), catalog));
  }

  @Test
  void testGlobalStateManagerCreationWithLegacyDataPresent() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteGlobalState globalState =
        new AirbyteGlobalState().withSharedState(Jsons.jsonNode(new DbState().withCdcState(new CdcState().withState(Jsons.jsonNode(new DbState())))))
            .withStreamStates(List.of(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withNamespace(NAMESPACE).withName(NAME))
                .withStreamState(Jsons.jsonNode(new DbStreamState()))));
    final AirbyteStateMessage airbyteStateMessage =
        new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL).withGlobal(globalState).withData(Jsons.jsonNode(new DbState()));

    final StateManager stateManager = StateManagerFactory.createStateManager(AirbyteStateType.GLOBAL, List.of(airbyteStateMessage), catalog);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(GlobalStateManager.class, stateManager.getClass());
  }

  @Test
  void testStreamStateManagerCreation() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage().withType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName(NAME).withNamespace(
            NAMESPACE)).withStreamState(Jsons.jsonNode(new DbStreamState())));

    final StateManager stateManager = StateManagerFactory.createStateManager(AirbyteStateType.STREAM, List.of(airbyteStateMessage), catalog);

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
        new AirbyteStateMessage().withType(AirbyteStateType.LEGACY).withData(Jsons.jsonNode(dbState));

    final StateManager stateManager = StateManagerFactory.createStateManager(AirbyteStateType.STREAM, List.of(airbyteStateMessage), catalog);

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
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL).withGlobal(globalState);

    Assertions.assertThrows(IllegalArgumentException.class,
        () -> StateManagerFactory.createStateManager(AirbyteStateType.STREAM, List.of(airbyteStateMessage), catalog));
  }

  @Test
  void testStreamStateManagerCreationWithLegacyDataPresent() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage().withType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName(NAME).withNamespace(
            NAMESPACE)).withStreamState(Jsons.jsonNode(new DbStreamState())))
        .withData(Jsons.jsonNode(new DbState()));

    final StateManager stateManager = StateManagerFactory.createStateManager(AirbyteStateType.STREAM, List.of(airbyteStateMessage), catalog);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(StreamStateManager.class, stateManager.getClass());
  }

}
