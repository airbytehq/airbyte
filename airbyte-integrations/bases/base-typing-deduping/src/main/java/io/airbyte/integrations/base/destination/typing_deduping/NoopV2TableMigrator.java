/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public class NoopV2TableMigrator<DialectTableDefinition> implements V2TableMigrator<DialectTableDefinition> {

  @Override
  public void migrateIfNecessary(final StreamConfig streamConfig) {
    // do nothing
  }

}
