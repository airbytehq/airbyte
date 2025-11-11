/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.sourceTesting.cleanup

import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.event.ShutdownEvent
import io.micronaut.runtime.event.annotation.EventListener
import jakarta.inject.Singleton

@Singleton
class AssetCleanerShutdownRunner(private val cleaners: Set<TestAssetCleaner>) {

    private val log = KotlinLogging.logger {}

    @EventListener
    @Suppress("UNUSED_PARAMETER")
    fun onShutdown(event: ShutdownEvent) {
        for (cleaner in cleaners) {
            log.info { "Cleaning up test assets for ${cleaner.assetName}" }
            try {
                cleaner.use { cleaner.cleanupOldTestAssets() }
            } catch (e: Exception) {
                log.error(e) { "Failed to cleanup test assets for ${cleaner.assetName}" }
            }
        }
    }
}
