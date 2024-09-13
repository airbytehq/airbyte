/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

interface DestinationV1V2Migrator {
    /**
     * This is the primary entrypoint to this interface
     *
     * Determine whether a migration is necessary for a given stream and if so, migrate the raw
     * table and rebuild the final table with a soft reset
     *
     * @param sqlGenerator the class to use to generate sql
     * @param destinationHandler the handler to execute the sql statements
     * @param streamConfig the stream to assess migration needs
     */
    @Throws(TableNotMigratedException::class, UnexpectedSchemaException::class, Exception::class)
    fun migrateIfNecessary(
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler<*>,
        streamConfig: StreamConfig
    )
}
