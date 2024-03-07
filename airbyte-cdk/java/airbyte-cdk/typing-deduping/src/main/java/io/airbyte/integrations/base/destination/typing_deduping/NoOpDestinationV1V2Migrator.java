/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public class NoOpDestinationV1V2Migrator implements DestinationV1V2Migrator {

  @Override
  public void migrateIfNecessary(final SqlGenerator sqlGenerator,
                                 final DestinationHandler<?> destinationHandler,
                                 final StreamConfig streamConfig)
      throws TableNotMigratedException, UnexpectedSchemaException {
    // Do nothing
  }

}
