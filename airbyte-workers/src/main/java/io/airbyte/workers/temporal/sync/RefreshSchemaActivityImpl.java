/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

public class RefreshSchemaActivityImpl implements RefreshSchemaActivity {

   private final SchedulerHandler schedulerHandler;

  @Override
  public boolean shouldRefreshSchema() {
    return false;
  }

  @Override
  public void refreshSchema() {

  }

  @Override
  public boolean shouldRunSync() {
    return true;
  }

}
