/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

public record MaxWorkersConfig(int maxSpecWorkers, int maxCheckWorkers, int maxDiscoverWorkers, int maxSyncWorkers, int maxNotifyWorkers) {

  @Override
  public String toString() {
    return "MaxWorkersConfig{" +
        "maxSpecWorkers=" + maxSpecWorkers +
        ", maxCheckWorkers=" + maxCheckWorkers +
        ", maxDiscoverWorkers=" + maxDiscoverWorkers +
        ", maxSyncWorkers=" + maxSyncWorkers +
        ", maxNotifyWorkers=" + maxNotifyWorkers +
        '}';
  }

}
