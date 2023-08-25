/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.cdc;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.debezium.CdcStateHandler;
import io.airbyte.integrations.source.mongodb.internal.state.MongoDbStateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Implementation of the {@link CdcStateHandler} that handles saving the CDC offset as Airbyte state
 * for MongoDB.
 */
public class MongoDbCdcStateHandler implements CdcStateHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(MongoDbCdcStateHandler.class);

  private final MongoDbStateManager stateManager;

  public MongoDbCdcStateHandler(MongoDbStateManager stateManager) {
    this.stateManager = stateManager;
  }

  @Override
  public AirbyteMessage saveState(final Map<String, String> offset, String dbHistory) {
    final MongoDbCdcState cdcState = new MongoDbCdcState(Jsons.jsonNode(offset));

    LOGGER.info("Saving Debezium state {}...", cdcState);
    stateManager.updateCdcState(cdcState);

    final AirbyteStateMessage stateMessage = stateManager.toState();
    return new AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(stateMessage);
  }

  @Override
  public AirbyteMessage saveStateAfterCompletionOfSnapshotOfNewStreams() {
    throw new RuntimeException("Debezium is not used to carry out the snapshot of tables.");
  }

  @Override
  public boolean isCdcCheckpointEnabled() {
    return false;
  }

}
