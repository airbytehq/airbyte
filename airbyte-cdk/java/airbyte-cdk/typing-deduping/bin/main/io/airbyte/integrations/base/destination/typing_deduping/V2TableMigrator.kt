/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

/**
 * Prefer [io.airbyte.integrations.base.destination.typing_deduping.migrators.Migration] instead.
 */
interface V2TableMigrator {
    @Throws(Exception::class) fun migrateIfNecessary(streamConfig: StreamConfig?)
}
