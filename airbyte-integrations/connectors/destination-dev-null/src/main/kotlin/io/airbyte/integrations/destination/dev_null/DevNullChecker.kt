/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.load.check.DestinationChecker
import jakarta.inject.Singleton

@Singleton
class DevNullChecker(
    @Suppress("unused") private val config: DevNullConfiguration,
) : DestinationChecker {
    override fun check() {
        // Do nothing - config injection validates the configuration
    }
}
