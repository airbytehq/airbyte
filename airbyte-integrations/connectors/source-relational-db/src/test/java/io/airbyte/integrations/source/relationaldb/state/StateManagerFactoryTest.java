/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb.state;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link StateManagerFactory} class.
 */
public class StateManagerFactoryTest {

  @Test
  void testLegacyStateManagerCreationFromDbState() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final DbState state = mock(DbState.class);
    final JsonNode config = mock(JsonNode.class);

    final StateManager stateManager = StateManagerFactory.createStateManager(state, catalog, config);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(LegacyStateManager.class, stateManager.getClass());
  }

  @Test
  void testLegacyStateManagerCreationFromAirbyteStateMessage() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = mock(AirbyteStateMessage.class);
    final JsonNode config = mock(JsonNode.class);
    when(airbyteStateMessage.getData()).thenReturn(Jsons.jsonNode(new DbState()));

    final StateManager stateManager = StateManagerFactory.createStateManager(airbyteStateMessage, catalog, config);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(LegacyStateManager.class, stateManager.getClass());
  }

  @Test
  void testCdcStateManagerCreation() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = mock(AirbyteStateMessage.class);
    final JsonNode config = mock(JsonNode.class);
    final JsonNode replicationConfig = mock(JsonNode.class);

    when(replicationConfig.hasNonNull("replication_slot")).thenReturn(true);
    when(replicationConfig.hasNonNull("publication")).thenReturn(true);

    when(config.hasNonNull("replication_method")).thenReturn(true);
    when(config.get("replication_method")).thenReturn(replicationConfig);

    final StateManager stateManager = StateManagerFactory.createStateManager(airbyteStateMessage, catalog, config);

    // TODO replace with non-null assertion and type assertion once the CDC state manager exists
    Assertions.assertNull(stateManager);
  }

  @Test
  void testGlobalStateManagerCreation() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = mock(AirbyteStateMessage.class);
    final JsonNode config = mock(JsonNode.class);
    when(airbyteStateMessage.getStateType()).thenReturn(AirbyteStateType.GLOBAL);

    final StateManager stateManager = StateManagerFactory.createStateManager(airbyteStateMessage, catalog, config);

    // TODO replace with non-null assertion and type assertion once the Global state manager exists
    Assertions.assertNull(stateManager);
  }

  @Test
  void testPerStreamStateManagerCreation() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final AirbyteStateMessage airbyteStateMessage = mock(AirbyteStateMessage.class);
    final JsonNode config = mock(JsonNode.class);
    when(airbyteStateMessage.getData()).thenReturn(null);

    final StateManager stateManager = StateManagerFactory.createStateManager(airbyteStateMessage, catalog, config);

    Assertions.assertNotNull(stateManager);
    Assertions.assertEquals(PerStreamStateManager.class, stateManager.getClass());
  }

  @Test
  void testStateManagerCreationForUnknownStateObject() {
    final ConfiguredAirbyteCatalog catalog = mock(ConfiguredAirbyteCatalog.class);
    final JsonNode config = mock(JsonNode.class);

    Assertions.assertThrows(IllegalArgumentException.class, () -> StateManagerFactory.createStateManager("Not Valid", catalog, config));
  }

}
