/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public class NoopV2TableMigrator implements V2TableMigrator {

  @Override
  public void migrateIfNecessary(final StreamConfig streamConfig) {
    // do nothing
  }

}
