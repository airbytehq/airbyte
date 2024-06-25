/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

class NoopV2TableMigrator : V2TableMigrator {
    override fun migrateIfNecessary(streamConfig: StreamConfig?) {
        // do nothing
    }
}
