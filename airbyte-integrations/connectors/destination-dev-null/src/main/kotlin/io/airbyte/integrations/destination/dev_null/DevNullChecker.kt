/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import io.airbyte.cdk.check.DestinationChecker
import jakarta.inject.Singleton

@Singleton
class DevNullChecker : DestinationChecker<DevNullConfiguration> {
    override fun check(config: DevNullConfiguration) {
        // Do nothing
    }
}
