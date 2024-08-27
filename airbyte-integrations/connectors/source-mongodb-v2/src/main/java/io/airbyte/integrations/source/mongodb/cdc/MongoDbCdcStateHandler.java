/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.cdc;

import io.airbyte.cdk.integrations.debezium.CdcStateHandler;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mongodb.state.InitialSnapshotStatus;
import io.airbyte.integrations.source.mongodb.state.MongoDbStateManager;
import io.airbyte.integrations.source.mongodb.state.MongoDbStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.util.List;
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

  public MongoDbCdcStateHandler(final MongoDbStateManager stateManager) {
    this.stateManager = stateManager;
  }

  @Override
  public AirbyteMessage saveState(final Map<String, String> offset, final AirbyteSchemaHistoryStorage.SchemaHistory<String> ignored) {
    final Boolean previousStateSchemaEnforced = stateManager.getCdcState() != null ? stateManager.getCdcState().schema_enforced() : null;
    final MongoDbCdcState cdcState = new MongoDbCdcState(Jsons.jsonNode(offset), previousStateSchemaEnforced);

    LOGGER.info("Saving Debezium state {}...", cdcState);
    stateManager.updateCdcState(cdcState);

    final AirbyteStateMessage stateMessage = stateManager.toState();
    return new AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(stateMessage);
  }

  public void setCdcStreamList(List<ConfiguredAirbyteStream> streamList) {
    streamList.stream().forEach(configuredAirbyteStream -> {
      stateManager.updateStreamState(configuredAirbyteStream.getStream().getName(), configuredAirbyteStream.getStream().getNamespace(),
          stateManager.getStreamState(configuredAirbyteStream.getStream().getName(), configuredAirbyteStream.getStream().getNamespace()).orElse(null));
    });
  }

  @Override
  public AirbyteMessage saveStateAfterCompletionOfSnapshotOfNewStreams() {
    throw new RuntimeException("Debezium is not used to carry out the snapshot of tables.");
  }

  @Override
  public boolean isCdcCheckpointEnabled() {
    return true;
  }

}
