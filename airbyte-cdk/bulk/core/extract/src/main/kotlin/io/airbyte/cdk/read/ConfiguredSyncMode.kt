/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import io.airbyte.protocol.models.v0.SyncMode

/**
 * [ConfiguredSyncMode] is equivalent to [SyncMode].
 *
 * This exists to avoid coupling the Bulk CDK code too closely to the Airbyte Protocol objects.
 */
enum class ConfiguredSyncMode {
    FULL_REFRESH,
    INCREMENTAL,
}

fun ConfiguredSyncMode.asProtocolSyncMode(): SyncMode =
    when (this) {
        ConfiguredSyncMode.FULL_REFRESH -> SyncMode.FULL_REFRESH
        ConfiguredSyncMode.INCREMENTAL -> SyncMode.INCREMENTAL
    }

fun SyncMode.asSyncMode(): ConfiguredSyncMode =
    when (this) {
        SyncMode.FULL_REFRESH -> ConfiguredSyncMode.FULL_REFRESH
        SyncMode.INCREMENTAL -> ConfiguredSyncMode.INCREMENTAL
    }
