/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public class NoOpDestinationV1V2Migrator<DialectTableDefinition> implements DestinationV1V2Migrator<DialectTableDefinition> {

  @Override
  public void migrateIfNecessary(final SqlGenerator<DialectTableDefinition> sqlGenerator,
                                 final DestinationHandler<DialectTableDefinition> destinationHandler,
                                 final StreamConfig streamConfig)
      throws TableNotMigratedException, UnexpectedSchemaException {
    // Do nothing
  }

}
