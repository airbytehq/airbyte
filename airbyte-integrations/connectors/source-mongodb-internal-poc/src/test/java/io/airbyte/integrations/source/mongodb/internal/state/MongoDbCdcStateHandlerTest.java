/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.state;

import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.ChangeEvent.SOURCE_ORDER;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.ChangeEvent.SOURCE_RESUME_TOKEN;
import static io.airbyte.integrations.debezium.internals.mongodb.MongoDbDebeziumConstants.ChangeEvent.SOURCE_SECONDS;
import static io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType.GLOBAL;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcState;
import io.airbyte.integrations.source.mongodb.internal.cdc.MongoDbCdcStateHandler;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class MongoDbCdcStateHandlerTest {

  private static final String RESUME_TOKEN = "8264BEB9F3000000012B0229296E04";

  private MongoDbStateManager mongoDbStateManager;

  private MongoDbCdcStateHandler mongoDbCdcStateHandler;

  @BeforeEach
  void setup() {
    mongoDbStateManager = MongoDbStateManager.createStateManager(null);
    mongoDbCdcStateHandler = new MongoDbCdcStateHandler(mongoDbStateManager);
  }

  @Test
  void testSavingState() {
    final int seconds = 1234567;
    final int order = 1;
    final Map<String, String> offset = Map.of(SOURCE_SECONDS, String.valueOf(seconds),
        SOURCE_ORDER, String.valueOf(order),
        SOURCE_RESUME_TOKEN, RESUME_TOKEN);

    final AirbyteMessage airbyteMessage = mongoDbCdcStateHandler.saveState(offset, "");

    assertNotNull(airbyteMessage);
    assertEquals(AirbyteMessage.Type.STATE, airbyteMessage.getType());
    assertNotNull(airbyteMessage.getState());
    assertEquals(GLOBAL, airbyteMessage.getState().getType());
    assertEquals(new MongoDbCdcState(Jsons.jsonNode(offset)),
        Jsons.object(airbyteMessage.getState().getGlobal().getSharedState(), MongoDbCdcState.class));
  }

  @Test
  void testSaveStateAfterCompletionOfSnapshotOfNewStreams() {
    final AirbyteMessage airbyteMessage = mongoDbCdcStateHandler.saveStateAfterCompletionOfSnapshotOfNewStreams();
    assertNotNull(airbyteMessage);
    assertEquals(AirbyteMessage.Type.STATE, airbyteMessage.getType());
    assertNotNull(airbyteMessage.getState());
    assertEquals(GLOBAL, airbyteMessage.getState().getType());
  }

}
