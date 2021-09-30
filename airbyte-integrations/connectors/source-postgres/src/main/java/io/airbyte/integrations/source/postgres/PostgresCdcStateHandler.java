/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.debezium.CdcStateHandler;
import io.airbyte.integrations.source.relationaldb.StateManager;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresCdcStateHandler implements CdcStateHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresCdcStateHandler.class);
  private final StateManager stateManager;

  public PostgresCdcStateHandler(StateManager stateManager) {
    this.stateManager = stateManager;
  }

  @Override
  public AirbyteMessage saveState(Map<String, String> offset, String dbHistory) {
    final JsonNode asJson = Jsons.jsonNode(offset);
    LOGGER.info("debezium state: {}", asJson);
    CdcState cdcState = new CdcState().withState(asJson);
    stateManager.getCdcStateManager().setCdcState(cdcState);
    final AirbyteStateMessage stateMessage = stateManager.emit();
    return new AirbyteMessage().withType(Type.STATE).withState(stateMessage);
  }

}
