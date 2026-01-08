/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null_v2

import io.airbyte.cdk.load.check.DestinationChecker
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton

@Singleton
class DevNullV2Checker : DestinationChecker<DevNullV2Configuration> {
    private val log = KotlinLogging.logger {}

    override fun check(config: DevNullV2Configuration) {
        log.info { "Checking dev-null-v2 connection with type: ${config.type}" }

        // Validate based on type
        when (config.type) {
            DevNullV2Configuration.Type.SILENT ->
                log.info { "Silent mode configured - records will be discarded" }
            DevNullV2Configuration.Type.LOGGING -> {
                log.info { "Logging mode configured - will log every ${config.logEvery} records" }
                if (config.logEvery <= 0) {
                    throw IllegalArgumentException(
                        "logEvery must be positive, got: ${config.logEvery}"
                    )
                }
                if (config.maxEntryCount <= 0) {
                    throw IllegalArgumentException(
                        "maxEntryCount must be positive, got: ${config.maxEntryCount}"
                    )
                }
            }
            DevNullV2Configuration.Type.THROTTLED -> {
                log.info {
                    "Throttled mode configured - will wait ${config.millisPerRecord}ms between records"
                }
                if (config.millisPerRecord < 0) {
                    throw IllegalArgumentException(
                        "millisPerRecord must be non-negative, got: ${config.millisPerRecord}"
                    )
                }
            }
            DevNullV2Configuration.Type.FAILING -> {
                log.info {
                    "Failing mode configured - will fail after ${config.numMessages} messages"
                }
                if (config.numMessages < 0) {
                    throw IllegalArgumentException(
                        "numMessages must be non-negative, got: ${config.numMessages}"
                    )
                }
            }
        }

        log.info { "Check passed successfully" }
    }
}
