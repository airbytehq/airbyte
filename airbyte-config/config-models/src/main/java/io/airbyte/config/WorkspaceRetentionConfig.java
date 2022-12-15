/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

public class WorkspaceRetentionConfig {

  private final long minDays;
  private final long maxDays;
  private final long maxSizeMb;

  public WorkspaceRetentionConfig(final long minDays, final long maxDays, final long maxSizeMb) {
    this.minDays = minDays;
    this.maxDays = maxDays;
    this.maxSizeMb = maxSizeMb;
  }

  public long getMinDays() {
    return minDays;
  }

  public long getMaxDays() {
    return maxDays;
  }

  public long getMaxSizeMb() {
    return maxSizeMb;
  }

}
