/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import static io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType.GLOBAL;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.core.type.TypeReference;
import io.airbyte.cdk.integrations.debezium.internals.mongodb.MongoDbDebeziumStateUtil;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class MongoDbCdcStateHandlerTest {

  private static final String DATABASE = "test-database";
  private static final String REPLICA_SET = "test-replica-set";
  private static final String RESUME_TOKEN = "8264BEB9F3000000012B0229296E04";

  private MongoDbCdcStateHandler mongoDbCdcStateHandler;

  @BeforeEach
  void setup() {
    final MongoDbStateManager mongoDbStateManager = MongoDbStateManager.createStateManager(null);
    mongoDbCdcStateHandler = new MongoDbCdcStateHandler(mongoDbStateManager);
  }

  @Test
  void testSavingState() {
    final Map<String, String> offset =
        Jsons.object(MongoDbDebeziumStateUtil.formatState(DATABASE, REPLICA_SET, RESUME_TOKEN), new TypeReference<>() {});
    final AirbyteMessage airbyteMessage = mongoDbCdcStateHandler.saveState(offset, null);
    assertNotNull(airbyteMessage);
    assertEquals(AirbyteMessage.Type.STATE, airbyteMessage.getType());
    assertNotNull(airbyteMessage.getState());
    assertEquals(GLOBAL, airbyteMessage.getState().getType());
    assertEquals(new MongoDbCdcState(Jsons.jsonNode(offset)),
        Jsons.object(airbyteMessage.getState().getGlobal().getSharedState(), MongoDbCdcState.class));
  }

  @Test
  void testSaveStateAfterCompletionOfSnapshotOfNewStreams() {
    assertThrows(RuntimeException.class, () -> mongoDbCdcStateHandler.saveStateAfterCompletionOfSnapshotOfNewStreams());
  }

}
