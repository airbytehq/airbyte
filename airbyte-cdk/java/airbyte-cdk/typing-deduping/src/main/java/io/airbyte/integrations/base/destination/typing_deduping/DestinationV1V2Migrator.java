/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public interface DestinationV1V2Migrator<DialectTableDefinition> {

  /**
   * This is the primary entrypoint to this interface
   * <p>
   * Determine whether a migration is necessary for a given stream and if so, migrate the raw table
   * and rebuild the final table with a soft reset
   *
   * @param sqlGenerator the class to use to generate sql
   * @param destinationHandler the handler to execute the sql statements
   * @param streamConfig the stream to assess migration needs
   */
  void migrateIfNecessary(
                          final SqlGenerator<DialectTableDefinition> sqlGenerator,
                          final DestinationHandler<DialectTableDefinition> destinationHandler,
                          final StreamConfig streamConfig)
      throws TableNotMigratedException, UnexpectedSchemaException, Exception;

}
