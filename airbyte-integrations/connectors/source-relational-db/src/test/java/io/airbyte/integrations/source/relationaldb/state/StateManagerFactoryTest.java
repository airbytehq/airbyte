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
  private static final String REPLICATION_SLOT = "replication_slot";
  private static final String PUBLICATION = "publication";
  private static final String REPLICATION_METHOD = "replication_method";

  private static final Supplier<Boolean> GLOBAL_STATE = () -> true;

  private static final Supplier<Boolean> NO_GLOBAL_STATE = () -> false;

  @Test
  void testNullOrEmptyState() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(null, catalog, NO_GLOBAL_STATE);
    });

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(List.of(), catalog, NO_GLOBAL_STATE);
    });
  }

  @Test
  void testLegacyStateManagerCreationFromAirbyteStateMessage() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = mock(AirbyteStateMessage.class);
    when(airbyteStateMessage.getData()).thenReturn(Jsons.jsonNode(new DbState()));

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, NO_GLOBAL_STATE);

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

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, GLOBAL_STATE);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(GlobalStateManager.class, stateManager.getClass());
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

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, GLOBAL_STATE);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(GlobalStateManager.class, stateManager.getClass());
  }

  @Test
  void testStreamStateManagerCreation() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage().withStateType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName(NAME).withNamespace(
            NAMESPACE)).withStreamState(Jsons.jsonNode(new DbStreamState())));

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, NO_GLOBAL_STATE);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(StreamStateManager.class, stateManager.getClass());
  }

  @Test
  void testStreamStateManagerCreationWithLegacyDataPresent() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage().withStateType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName(NAME).withNamespace(
            NAMESPACE)).withStreamState(Jsons.jsonNode(new DbStreamState())))
        .withData(Jsons.jsonNode(new DbState()));

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, NO_GLOBAL_STATE);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(StreamStateManager.class, stateManager.getClass());
  }

}
