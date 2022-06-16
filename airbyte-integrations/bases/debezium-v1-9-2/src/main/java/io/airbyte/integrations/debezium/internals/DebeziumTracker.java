/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DebeziumTracker {

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumTracker.class);

  private static final DebeziumTracker INSTANCE = new DebeziumTracker();

  // status of the Debezium source task
  private boolean started = false;
  private long updateCounter = 0L;

  public static DebeziumTracker getInstance() {
    return INSTANCE;
  }

  private DebeziumTracker() {}

  public void markAsStarted() {
    this.started = true;
    LOGGER.info("Debezium source task has started...");
  }

  public boolean isStarted() {
    return started;
  }

  public void incrementUpdateCounter() {
    this.updateCounter += 1;
    if (this.updateCounter % 100000 == 0) {
      LOGGER.info("Processed {} records", this.updateCounter);
    }
  }

  public long getUpdateCounter() {
    return updateCounter;
  }

}
