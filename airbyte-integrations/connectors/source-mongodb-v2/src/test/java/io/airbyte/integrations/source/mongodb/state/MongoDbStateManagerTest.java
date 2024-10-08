/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.state;

import static io.airbyte.integrations.source.mongodb.MongoConstants.DATABASE_CONFIG_CONFIGURATION_KEY;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.ChangeEvent.SOURCE_ORDER;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.ChangeEvent.SOURCE_RESUME_TOKEN;
import static io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants.ChangeEvent.SOURCE_SECONDS;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mongodb.MongoDbSourceConfig;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcState;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbDebeziumConstants;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

class MongoDbStateManagerTest {

  private static final String ID = "64c0029d95ad260d69ef28a0";
  private static final String RESUME_TOKEN = "8264BEB9F3000000012B0229296E04";
  private static final String STREAM_NAME = "test-collection";
  private static final String STREAM_NAMESPACE = "test-database";
  private static final String DATABASE = "test-database";

  final MongoDbSourceConfig CONFIG = new MongoDbSourceConfig(Jsons.jsonNode(
      Map.of(DATABASE_CONFIG_CONFIGURATION_KEY,
          Map.of(
              MongoDbDebeziumConstants.Configuration.CONNECTION_STRING_CONFIGURATION_KEY, "mongodb://host:12345/",
              MongoDbDebeziumConstants.Configuration.DATABASE_CONFIGURATION_KEY, DATABASE))));

  @Test
  void testCreationWithInitialState() {
    final StreamDescriptor streamDescriptor = new StreamDescriptor().withNamespace(STREAM_NAMESPACE).withName(STREAM_NAME);
    final int seconds = 123456789;
    final int order = 1;
    final Map<String, String> offset = Map.of(SOURCE_SECONDS, String.valueOf(seconds),
        SOURCE_ORDER, String.valueOf(order),
        SOURCE_RESUME_TOKEN, RESUME_TOKEN);
    final MongoDbCdcState cdcState = new MongoDbCdcState(Jsons.jsonNode(offset));
    final MongoDbStreamState mongoDbStreamState = new MongoDbStreamState(ID, InitialSnapshotStatus.IN_PROGRESS, IdType.OBJECT_ID);
    final JsonNode sharedState = Jsons.jsonNode(cdcState);
    final JsonNode streamState = Jsons.jsonNode(mongoDbStreamState);
    final AirbyteStreamState airbyteStreamState = new AirbyteStreamState().withStreamDescriptor(streamDescriptor).withStreamState(streamState);
    final AirbyteGlobalState airbyteGlobalState = new AirbyteGlobalState().withSharedState(sharedState).withStreamStates(List.of(airbyteStreamState));
    final AirbyteStateMessage airbyteStateMessage =
        new AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.GLOBAL).withGlobal(airbyteGlobalState);

    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(Jsons.jsonNode(List.of(airbyteStateMessage)), CONFIG);
    assertNotNull(stateManager);
    assertNotNull(stateManager.getCdcState());
    Assertions.assertEquals(seconds, stateManager.getCdcState().state().get(SOURCE_SECONDS).asInt());
    Assertions.assertEquals(order, stateManager.getCdcState().state().get(SOURCE_ORDER).asInt());
    Assertions.assertEquals(RESUME_TOKEN, stateManager.getCdcState().state().get(SOURCE_RESUME_TOKEN).asText());
    assertTrue(stateManager.getStreamState(STREAM_NAME, STREAM_NAMESPACE).isPresent());
    assertEquals(ID, stateManager.getStreamState(STREAM_NAME, STREAM_NAMESPACE).get().id());
  }

  @Test
  void testCreationWithInitialNullState() {
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(null, CONFIG);
    assertNotNull(stateManager);
    assertNull(stateManager.getCdcState());
  }

  @Test
  void testCreationWithInitialEmptyState() {
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(Jsons.emptyObject(), CONFIG);
    assertNotNull(stateManager);
    assertNull(stateManager.getCdcState());
  }

  @Test
  void testCreationWithInitialEmptyListState() {
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(Jsons.jsonNode(List.of()), CONFIG);
    assertNotNull(stateManager);
    assertNull(stateManager.getCdcState());
  }

  @Test
  void testCreationWithInitialStateTooManyMessages() {
    final List<AirbyteStateMessage> stateMessages = List.of(new AirbyteStateMessage(), new AirbyteStateMessage());
    assertThrows(IllegalStateException.class, () -> MongoDbStateManager.createStateManager(Jsons.jsonNode(stateMessages), CONFIG));
  }

  @Test
  void testUpdateCdcState() {
    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(null, CONFIG);
    assertNotNull(stateManager);
    assertNull(stateManager.getCdcState());

    final Map<String, String> offset = Map.of(SOURCE_SECONDS, String.valueOf(123456789),
        SOURCE_ORDER, String.valueOf(1),
        SOURCE_RESUME_TOKEN, RESUME_TOKEN);
    final MongoDbCdcState cdcState = new MongoDbCdcState(Jsons.jsonNode(offset));
    stateManager.updateCdcState(cdcState);
    assertNotNull(stateManager.getCdcState());
    Assertions.assertEquals(cdcState, stateManager.getCdcState());
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
    final MongoDbStreamState mongoDbStreamState = new MongoDbStreamState(ID, InitialSnapshotStatus.IN_PROGRESS, IdType.OBJECT_ID);
    final JsonNode sharedState = Jsons.jsonNode(cdcState);
    final JsonNode streamState = Jsons.jsonNode(mongoDbStreamState);
    final AirbyteStreamState airbyteStreamState = new AirbyteStreamState().withStreamDescriptor(streamDescriptor).withStreamState(streamState);
    final AirbyteGlobalState airbyteGlobalState = new AirbyteGlobalState().withSharedState(sharedState).withStreamStates(List.of(airbyteStreamState));
    final AirbyteStateMessage airbyteStateMessage =
        new AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.GLOBAL).withGlobal(airbyteGlobalState);

    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(Jsons.jsonNode(List.of(airbyteStateMessage)), CONFIG);
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

    final MongoDbStreamState updatedStreamState = new MongoDbStreamState("updated", InitialSnapshotStatus.COMPLETE, IdType.OBJECT_ID);
    stateManager.updateStreamState(STREAM_NAME, STREAM_NAMESPACE, updatedStreamState);
    final AirbyteStateMessage generated3 = stateManager.toState();

    assertNotNull(generated3);
    assertEquals(updatedStreamState.id(),
        Jsons.object(generated3.getGlobal().getStreamStates().get(0).getStreamState(), MongoDbStreamState.class).id());
  }

  @Test
  void testReset() {
    final StreamDescriptor streamDescriptor = new StreamDescriptor().withNamespace(STREAM_NAMESPACE).withName(STREAM_NAME);
    final int seconds = 123456789;
    final int order = 1;
    final Map<String, String> offset = Map.of(SOURCE_SECONDS, String.valueOf(seconds),
        SOURCE_ORDER, String.valueOf(order),
        SOURCE_RESUME_TOKEN, RESUME_TOKEN);
    final MongoDbCdcState cdcState = new MongoDbCdcState(Jsons.jsonNode(offset));
    final MongoDbStreamState mongoDbStreamState = new MongoDbStreamState(ID, InitialSnapshotStatus.IN_PROGRESS, IdType.OBJECT_ID);
    final JsonNode sharedState = Jsons.jsonNode(cdcState);
    final JsonNode streamState = Jsons.jsonNode(mongoDbStreamState);
    final AirbyteStreamState airbyteStreamState = new AirbyteStreamState().withStreamDescriptor(streamDescriptor).withStreamState(streamState);
    final AirbyteGlobalState airbyteGlobalState = new AirbyteGlobalState().withSharedState(sharedState).withStreamStates(List.of(airbyteStreamState));
    final AirbyteStateMessage airbyteStateMessage =
        new AirbyteStateMessage().withType(AirbyteStateMessage.AirbyteStateType.GLOBAL).withGlobal(airbyteGlobalState);

    final MongoDbStateManager stateManager = MongoDbStateManager.createStateManager(Jsons.jsonNode(List.of(airbyteStateMessage)), CONFIG);
    final MongoDbCdcState newCdcState = new MongoDbCdcState(Jsons.jsonNode(Map.of()));

    stateManager.resetState(newCdcState);
    Assertions.assertEquals(newCdcState, stateManager.getCdcState());
    assertEquals(0, stateManager.getStreamStates().size());
  }

}
