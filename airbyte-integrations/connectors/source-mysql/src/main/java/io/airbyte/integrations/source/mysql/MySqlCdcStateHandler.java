/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.source.mysql.MySqlSource.MYSQL_CDC_OFFSET;
import static io.airbyte.integrations.source.mysql.MySqlSource.MYSQL_DB_HISTORY;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.debezium.CdcStateHandler;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import java.util.HashMap;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlCdcStateHandler implements CdcStateHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlCdcStateHandler.class);

  private final StateManager stateManager;

  public MySqlCdcStateHandler(final StateManager stateManager) {
    this.stateManager = stateManager;
  }

  @Override
  public AirbyteMessage saveState(final Map<String, String> offset, final String dbHistory) {
    final Map<String, Object> state = new HashMap<>();
    state.put(MYSQL_CDC_OFFSET, offset);
    state.put(MYSQL_DB_HISTORY, dbHistory);

    final JsonNode asJson = Jsons.jsonNode(state);

    LOGGER.info("debezium state: {}", asJson);

    final CdcState cdcState = new CdcState().withState(asJson);
    stateManager.getCdcStateManager().setCdcState(cdcState);
    final AirbyteStateMessage stateMessage = stateManager.emit();
    return new AirbyteMessage().withType(Type.STATE).withState(stateMessage);
  }

}
