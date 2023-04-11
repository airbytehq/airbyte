/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.debezium.CdcStateHandler;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.Map;
import java.util.Optional;

public class PostgresCdcStateHandler implements CdcStateHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresCdcStateHandler.class);
  private final StateManager stateManager;

  public PostgresCdcStateHandler(final StateManager stateManager) {
    this.stateManager = stateManager;
  }

  @Override
  public AirbyteMessage saveState(final Map<String, String> offset, final String dbHistory) {
    final JsonNode asJson = Jsons.jsonNode(offset);
    LOGGER.info("debezium state: {}", asJson);
    final CdcState cdcState = new CdcState().withState(asJson);
    stateManager.getCdcStateManager().setCdcState(cdcState);
    /*
     * Namespace pair is ignored by global state manager, but is needed for satisfy the API contract.
     * Therefore, provide an empty optional.
     */
    final AirbyteStateMessage stateMessage = stateManager.emit(Optional.empty());
    return new AirbyteMessage().withType(Type.STATE).withState(stateMessage);
  }

  /**
   * Here we just want to emit the state to update the list of streams in the database to mark the
   * completion of snapshot of new added streams. The addition of new streams in the state is done
   * here
   * {@link io.airbyte.integrations.source.relationaldb.state.GlobalStateManager#toState(Optional)}
   * which is called inside the {@link StateManager#emit(Optional)} method which is being triggered
   * below. The toState method adds all the streams present in the catalog in the state. Since there
   * is no change in the CDC state value, whatever was present in the database will again be stored.
   * This is done so that we can mark the completion of snapshot of new tables.
   */
  @Override
  public AirbyteMessage saveStateAfterCompletionOfSnapshotOfNewStreams() {
    LOGGER.info("Snapshot of new tables is complete, saving state");
    /*
     * Namespace pair is ignored by global state manager, but is needed for satisfy the API contract.
     * Therefore, provide an empty optional.
     */
    final AirbyteStateMessage stateMessage = stateManager.emit(Optional.empty());
    return new AirbyteMessage().withType(Type.STATE).withState(stateMessage);
  }
}
