/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CdcStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(CdcStateManager.class);

  private final CdcState initialState;

  private CdcState currentState;

  public CdcStateManager(final CdcState serialized) {
    this.initialState = serialized;
    this.currentState = serialized;

    LOGGER.info("Initialized CDC state with: {}", serialized);
  }

  public void setCdcState(final CdcState state) {
    this.currentState = state;
  }

  public CdcState getCdcState() {
    return currentState != null ? Jsons.clone(currentState) : null;
  }

  @Override
  public String toString() {
    return "CdcStateManager{" +
        "initialState=" + initialState +
        ", currentState=" + currentState +
        '}';
  }

}
