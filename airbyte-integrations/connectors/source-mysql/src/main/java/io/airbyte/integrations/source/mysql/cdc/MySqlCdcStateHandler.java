/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc;

import static io.airbyte.integrations.source.mysql.cdc.MySqlDebeziumStateUtil.serialize;
import static io.airbyte.integrations.source.mysql.cdc.MysqlCdcStateConstants.COMPRESSION_ENABLED;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.debezium.CdcStateHandler;
import io.airbyte.cdk.integrations.debezium.internals.AirbyteSchemaHistoryStorage.SchemaHistory;
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlCdcStateHandler implements CdcStateHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlCdcStateHandler.class);

  private final StateManager stateManager;

  public MySqlCdcStateHandler(final StateManager stateManager) {
    this.stateManager = stateManager;
  }

  @Override
  public boolean isCdcCheckpointEnabled() {
    return true;
  }

  @Override
  public AirbyteMessage saveState(final Map<String, String> offset, final SchemaHistory<String> dbHistory) {
    final JsonNode asJson = serialize(offset, dbHistory);

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
  public boolean compressSchemaHistoryForState() {
    return COMPRESSION_ENABLED;
  }

}
