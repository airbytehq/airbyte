/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.sourceTesting.cleanup

import java.time.Clock

abstract class TestAssetCleaner(clock: Clock) : AutoCloseable {

    abstract val assetName: String

    /**
     * Cleans up old test assets from previous test runs. This might include tables, schemas, or
     * other database objects that follow a specific naming pattern used by tests and have old
     * timestamps.
     */
    abstract fun cleanupOldTestAssets()

    // Remove resources created more than one hour before startup.
    // Should avoid race conditions where simultaneous test runs delete each other's resources.
    private val cutoffMillis = clock.instant().toEpochMilli() - 1000 * 60 * 60

    fun Long?.tooOld(): Boolean {
        return this != null && this < cutoffMillis
    }
}
