/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_2

import io.airbyte.cdk.load.check.DestinationChecker
import jakarta.inject.Singleton

/** Checker for Dev Null 2 destination. Always succeeds since there's nothing to validate. */
@Singleton
class DevNull2Checker : DestinationChecker<DevNull2Configuration> {
    override fun check(config: DevNull2Configuration) {
        // Always succeeds - nothing to validate for /dev/null
    }
}
