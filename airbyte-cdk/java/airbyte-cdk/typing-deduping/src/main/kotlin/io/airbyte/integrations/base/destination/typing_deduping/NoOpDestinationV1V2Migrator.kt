/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

class NoOpDestinationV1V2Migrator : DestinationV1V2Migrator {
    @Throws(TableNotMigratedException::class, UnexpectedSchemaException::class)
    override fun migrateIfNecessary(
        sqlGenerator: SqlGenerator,
        destinationHandler: DestinationHandler<*>,
        streamConfig: StreamConfig
    ) {
        // Do nothing
    }
}
