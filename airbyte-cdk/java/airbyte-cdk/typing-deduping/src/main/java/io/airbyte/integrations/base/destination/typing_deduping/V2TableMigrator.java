/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

/**
 * Prefer {@link io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration}
 * instead.
 */
public interface V2TableMigrator {

  void migrateIfNecessary(final StreamConfig streamConfig) throws Exception;

}
