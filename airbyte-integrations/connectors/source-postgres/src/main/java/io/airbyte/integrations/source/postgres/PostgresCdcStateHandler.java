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
import io.debezium.engine.ChangeEvent;
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

  @Override
  public boolean isSnapshotEvent(final ChangeEvent<String, String> event){
    JsonNode isSnapshotEvent = Jsons.deserialize(event.value()).get("source").get("snapshot");
    return isSnapshotEvent != null && isSnapshotEvent.asBoolean();
  }

  @Override
  public boolean isRecordBehindOffset(final Map<String, String> offset, final ChangeEvent<String, String> event) {
    if (offset.size() != 1) {
      return false;
    }

    final JsonNode offsetJson = Jsons.deserialize((String) offset.values().toArray()[0]);

    final String offset_lsn = offsetJson.get("lsn_commit") != null ?
        String.valueOf(offsetJson.get("lsn_commit")) :
        String.valueOf(offsetJson.get("lsn"));
    final String event_lsn = String.valueOf(Jsons.deserialize(event.value()).get("source").get("lsn"));
    return Integer.parseInt(event_lsn) > Integer.parseInt(offset_lsn);
  }

  @Override
  public boolean isSameOffset(final Map<String, String> offsetA, final Map<String, String> offsetB) {
    if (offsetA == null || offsetA.size() != 1){
      return false;
    }
    if (offsetB == null || offsetB.size() != 1){
      return false;
    }
    final JsonNode offsetJsonA = Jsons.deserialize((String) offsetA.values().toArray()[0]);
    final JsonNode offsetJsonB = Jsons.deserialize((String) offsetB.values().toArray()[0]);

    final String lsnA = offsetJsonA.get("lsn_commit") != null ?
        String.valueOf(offsetJsonA.get("lsn_commit")) :
        String.valueOf(offsetJsonA.get("lsn"));
    final String lsnB = offsetJsonB.get("lsn_commit") != null ?
        String.valueOf(offsetJsonB.get("lsn_commit")) :
        String.valueOf(offsetJsonB.get("lsn"));

    return Integer.parseInt(lsnA) == Integer.parseInt(lsnB);
  }

}
