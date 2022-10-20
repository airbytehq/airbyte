/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

public class RefreshSchemaActivityImpl implements RefreshSchemaActivity {

  public boolean shouldRefreshSchema() {
    return false;
  }

  public void refreshSchema() {
  }

  public boolean shouldRunSync(){
    return true;
  }
}
