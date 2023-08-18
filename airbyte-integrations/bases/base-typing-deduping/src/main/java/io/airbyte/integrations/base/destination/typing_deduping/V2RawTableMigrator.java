/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public interface V2RawTableMigrator<DialectTableDefinition> {

  void migrateIfNecessary(final StreamConfig streamConfig) throws InterruptedException;

}
