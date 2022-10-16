/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

public class MaxWorkersConfig {

  private final int maxSpecWorkers;
  private final int maxCheckWorkers;
  private final int maxDiscoverWorkers;
  private final int maxSyncWorkers;

  public MaxWorkersConfig(final int maxSpecWorkers, final int maxCheckWorkers, final int maxDiscoverWorkers, final int maxSyncWorkers) {
    this.maxSpecWorkers = maxSpecWorkers;
    this.maxCheckWorkers = maxCheckWorkers;
    this.maxDiscoverWorkers = maxDiscoverWorkers;
    this.maxSyncWorkers = maxSyncWorkers;
  }

  public int getMaxSpecWorkers() {
    return maxSpecWorkers;
  }

  public int getMaxCheckWorkers() {
    return maxCheckWorkers;
  }

  public int getMaxDiscoverWorkers() {
    return maxDiscoverWorkers;
  }

  public int getMaxSyncWorkers() {
    return maxSyncWorkers;
  }

  @Override
  public String toString() {
    return "MaxWorkersConfig{" +
        "maxSpecWorkers=" + maxSpecWorkers +
        ", maxCheckWorkers=" + maxCheckWorkers +
        ", maxDiscoverWorkers=" + maxDiscoverWorkers +
        ", maxSyncWorkers=" + maxSyncWorkers +
        '}';
  }

}
