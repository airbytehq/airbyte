/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.state;

import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.ChangeEvent.SOURCE_ORDER;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.ChangeEvent.SOURCE_RESUME_TOKEN;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.ChangeEvent.SOURCE_SECONDS;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcState;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class MongoDbStateManagerTest {

  private static final String ID = "64c0029d95ad260d69ef28a0";
  private static final String RESUME_TOKEN = "8264BEB9F3000000012B0229296E04";
  private static final String STREAM_NAME = "test-collection";
  private static final String STREAM_NAMESPACE = "test-database";

  @Test
  void testCreationWithInitialState() {
    final StreamDescriptor streamDescriptor = new StreamDescriptor().withNamespace(STREAM_NAMESPACE).withName(STREAM_NAME);
    final int seconds = 123456789;
    final int order = 1;
    final Map<String, String> offset = Map.of(SOURCE_SECONDS, String.valueOf(seconds),
        SOURCE_ORDER, String.valueOf(order),
        SOURCE_RESUME_TOKEN, RESUME_TOKEN);
    final MongoDbCdcState cdcState = new MongoDbCdcState(Jsons.jsonNode(offset));
    final MongoDbStreamState mongoDbStreamState = new MongoDbStreamState(ID);
    final JsonNode sharedState = Jsons.jsonNode(cdcState);
    final JsonNode streamState = Jsons.jsonNode(mongoDbStreamState);
    final AirbyteStreamState airbyteStreamState = new AirbyteStreamState().withStreamDescriptor(streamDescriptor).withStreamState(streamState);
    final AirbyteGlobalState airbyteGlobalState = new AirbyteGlobalState().withSharedState(sharedState).withStreamStates(List.of(airbyteStreamState));
    final AirbyteStateMessage airbyteStateMessage =
        new AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.GLOBAL).withGlobal(airbyteGlobalState);

    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(Jsons.jsonNode(List.of(airbyteStateMessage)));
    assertNotNull(stateManager);
    assertNotNull(stateManager.getCdcState());
    assertEquals(seconds, stateManager.getCdcState().state().get(SOURCE_SECONDS).asInt());
    assertEquals(order, stateManager.getCdcState().state().get(SOURCE_ORDER).asInt());
    assertEquals(RESUME_TOKEN, stateManager.getCdcState().state().get(SOURCE_RESUME_TOKEN).asText());
    assertTrue(stateManager.getStreamState(STREAM_NAME, STREAM_NAMESPACE).isPresent());
    assertEquals(ID, stateManager.getStreamState(STREAM_NAME, STREAM_NAMESPACE).get().id());
  }

  @Test
  void testCreationWithInitialNullState() {
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(null);
    assertNotNull(stateManager);
    assertNull(stateManager.getCdcState());
  }

  @Test
  void testCreationWithInitialEmptyState() {
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(Jsons.emptyObject());
    assertNotNull(stateManager);
    assertNull(stateManager.getCdcState());
  }

  @Test
  void testCreationWithInitialEmptyListState() {
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(Jsons.jsonNode(List.of()));
    assertNotNull(stateManager);
    assertNull(stateManager.getCdcState());
  }

  @Test
  void testCreationWithInitialStateTooManyMessages() {
    final List<AirbyteStateMessage> stateMessages = List.of(new AirbyteStateMessage(), new AirbyteStateMessage());
    assertThrows(IllegalStateException.class, () -> MongoDbStateManager.createStateManager(Jsons.jsonNode(stateMessages)));
  }

  @Test
  void testUpdateCdcState() {
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(null);
    assertNotNull(stateManager);
    assertNull(stateManager.getCdcState());

    final Map<String, String> offset = Map.of(SOURCE_SECONDS, String.valueOf(123456789),
        SOURCE_ORDER, String.valueOf(1),
        SOURCE_RESUME_TOKEN, RESUME_TOKEN);
    final MongoDbCdcState cdcState = new MongoDbCdcState(Jsons.jsonNode(offset));
    stateManager.updateCdcState(cdcState);
    assertNotNull(stateManager.getCdcState());
    assertEquals(cdcState, stateManager.getCdcState());
  }

  @Test
  void testGeneratingAirbyteStateMessage() {
    final StreamDescriptor streamDescriptor = new StreamDescriptor().withNamespace(STREAM_NAMESPACE).withName(STREAM_NAME);
    final int seconds = 123456789;
    final int order = 1;
    final Map<String, String> offset = Map.of(SOURCE_SECONDS, String.valueOf(seconds),
        SOURCE_ORDER, String.valueOf(order),
        SOURCE_RESUME_TOKEN, RESUME_TOKEN);
    final MongoDbCdcState cdcState = new MongoDbCdcState(Jsons.jsonNode(offset));
    final MongoDbStreamState mongoDbStreamState = new MongoDbStreamState(ID);
    final JsonNode sharedState = Jsons.jsonNode(cdcState);
    final JsonNode streamState = Jsons.jsonNode(mongoDbStreamState);
    final AirbyteStreamState airbyteStreamState = new AirbyteStreamState().withStreamDescriptor(streamDescriptor).withStreamState(streamState);
    final AirbyteGlobalState airbyteGlobalState = new AirbyteGlobalState().withSharedState(sharedState).withStreamStates(List.of(airbyteStreamState));
    final AirbyteStateMessage airbyteStateMessage =
        new AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.GLOBAL).withGlobal(airbyteGlobalState);

    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(Jsons.jsonNode(List.of(airbyteStateMessage)));
    final AirbyteStateMessage generated = stateManager.toState();

    assertNotNull(generated);
    assertEquals(airbyteStateMessage, generated);

    final Map<String, String> offset2 = Map.of(SOURCE_SECONDS, String.valueOf(1112223334),
        SOURCE_ORDER, String.valueOf(2),
        SOURCE_RESUME_TOKEN, RESUME_TOKEN);
    final MongoDbCdcState updatedCdcState = new MongoDbCdcState(Jsons.jsonNode(offset2));
    stateManager.updateCdcState(updatedCdcState);

    final AirbyteStateMessage generated2 = stateManager.toState();

    assertNotNull(generated2);
    assertEquals(updatedCdcState, Jsons.object(generated2.getGlobal().getSharedState(), MongoDbCdcState.class));

    final MongoDbStreamState updatedStreamState = new MongoDbStreamState("updated");
    stateManager.updateStreamState(STREAM_NAME, STREAM_NAMESPACE, updatedStreamState);
    final AirbyteStateMessage generated3 = stateManager.toState();

    assertNotNull(generated3);
    assertEquals(updatedStreamState.id(),
        Jsons.object(generated3.getGlobal().getStreamStates().get(0).getStreamState(), MongoDbStreamState.class).id());
  }

}
