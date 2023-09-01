/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public interface V2TableMigrator<DialectTableDefinition> {

  void migrateIfNecessary(final StreamConfig streamConfig) throws Exception;

}
