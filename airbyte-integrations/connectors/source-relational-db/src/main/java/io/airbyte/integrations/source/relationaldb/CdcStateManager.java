/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.Collections;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CdcStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(CdcStateManager.class);

  private final CdcState initialState;
  private final Set<AirbyteStreamNameNamespacePair> initialStreamsSynced;
  private final AirbyteStateMessage rawStateMessage;
  private CdcState currentState;

  public CdcStateManager(final CdcState serialized, final Set<AirbyteStreamNameNamespacePair> initialStreamsSynced, final AirbyteStateMessage stateMessage) {
    this.initialState = serialized;
    this.currentState = serialized;
    this.initialStreamsSynced = initialStreamsSynced;

    this.rawStateMessage = stateMessage;
    LOGGER.info("Initialized CDC state with: {}", serialized);
  }

  public void setCdcState(final CdcState state) {
    this.currentState = state;
  }

  public CdcState getCdcState() {
    return currentState != null ? Jsons.clone(currentState) : null;
  }

  public AirbyteStateMessage getRawStateMessage() {
    return rawStateMessage;
  }

  public Set<AirbyteStreamNameNamespacePair> getInitialStreamsSynced() {
    return initialStreamsSynced != null ? Collections.unmodifiableSet(initialStreamsSynced) : null;
  }

  @Override
  public String toString() {
    return "CdcStateManager{" +
        "initialState=" + initialState +
        ", currentState=" + currentState +
        '}';
  }

}
