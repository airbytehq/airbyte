/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

public class DebeziumTracker {

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
  }

  public boolean isStarted() {
    return started;
  }

  public void incrementUpdateCounter() {
    this.updateCounter += 1;
  }

  public long getUpdateCounter() {
    return updateCounter;
  }

}
