/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
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

  @Test
  void testNullOrEmptyState() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final JsonNode config = mock(JsonNode.class);

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(null, catalog, config);
    });

    Assertions.assertThrows(IllegalArgumentException.class, () -> {
      StateManagerFactory.createStateManager(List.of(), catalog, config);
    });
  }

  @Test
  void testLegacyStateManagerCreationFromAirbyteStateMessage() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = mock(AirbyteStateMessage.class);
    final JsonNode config = mock(JsonNode.class);
    when(airbyteStateMessage.getData()).thenReturn(Jsons.jsonNode(new DbState()));

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, config);

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
    final JsonNode config = mock(JsonNode.class);
    final JsonNode replicationConfig = mock(JsonNode.class);

    when(replicationConfig.hasNonNull(REPLICATION_SLOT)).thenReturn(true);
    when(replicationConfig.hasNonNull(PUBLICATION)).thenReturn(true);

    when(config.hasNonNull(REPLICATION_METHOD)).thenReturn(true);
    when(config.get(REPLICATION_METHOD)).thenReturn(replicationConfig);

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, config);

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
    final JsonNode config = mock(JsonNode.class);
    final JsonNode replicationConfig = mock(JsonNode.class);

    when(replicationConfig.hasNonNull(REPLICATION_SLOT)).thenReturn(true);
    when(replicationConfig.hasNonNull(PUBLICATION)).thenReturn(true);

    when(config.hasNonNull(REPLICATION_METHOD)).thenReturn(true);
    when(config.get(REPLICATION_METHOD)).thenReturn(replicationConfig);

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, config);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(GlobalStateManager.class, stateManager.getClass());
  }

  @Test
  void testStreamStateManagerCreation() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = new AirbyteStateMessage().withStateType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName(NAME).withNamespace(
            NAMESPACE)).withStreamState(Jsons.jsonNode(new DbStreamState())));
    final JsonNode config = mock(JsonNode.class);

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, config);

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
    final JsonNode config = mock(JsonNode.class);

    final StateManager stateManager = StateManagerFactory.createStateManager(List.of(airbyteStateMessage), catalog, config);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(StreamStateManager.class, stateManager.getClass());
  }

  @Test
  void testCdcDetectionLogic() {
    final JsonNode config = mock(JsonNode.class);
    final JsonNode replicationConfig = mock(JsonNode.class);

    when(replicationConfig.hasNonNull(REPLICATION_SLOT)).thenReturn(true);
    when(replicationConfig.hasNonNull(PUBLICATION)).thenReturn(true);
    when(config.hasNonNull(REPLICATION_METHOD)).thenReturn(true);
    when(config.get(REPLICATION_METHOD)).thenReturn(replicationConfig);
    assertTrue(StateManagerFactory.isCdc(config));

    when(replicationConfig.hasNonNull(REPLICATION_SLOT)).thenReturn(false);
    assertFalse(StateManagerFactory.isCdc(config));

    when(replicationConfig.hasNonNull(REPLICATION_SLOT)).thenReturn(true);
    when(replicationConfig.hasNonNull(PUBLICATION)).thenReturn(false);
    assertFalse(StateManagerFactory.isCdc(config));

    when(replicationConfig.hasNonNull(REPLICATION_SLOT)).thenReturn(true);
    when(replicationConfig.hasNonNull(PUBLICATION)).thenReturn(true);
    when(config.hasNonNull(REPLICATION_METHOD)).thenReturn(false);
    assertFalse(StateManagerFactory.isCdc(config));

    when(replicationConfig.hasNonNull(REPLICATION_SLOT)).thenReturn(false);
    when(replicationConfig.hasNonNull(PUBLICATION)).thenReturn(false);
    when(config.hasNonNull(REPLICATION_METHOD)).thenReturn(false);
    assertFalse(StateManagerFactory.isCdc(config));
  }

}
