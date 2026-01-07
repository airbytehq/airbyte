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
        log.info { "Checking dev-null-v2 connection with mode: ${config.mode}" }
        
        // Validate mode
        when (config.mode) {
            "silent" -> log.info { "Silent mode configured - records will be discarded" }
            "logging" -> log.info { "Logging mode configured - will log every ${config.logEveryN} records" }
            "failing" -> log.info { "Failing mode configured - will simulate failures" }
            else -> throw IllegalArgumentException("Invalid mode: ${config.mode}. Must be one of: silent, logging, failing")
        }
        
        // Validate logEveryN
        if (config.logEveryN <= 0) {
            throw IllegalArgumentException("logEveryN must be positive, got: ${config.logEveryN}")
        }
        
        log.info { "Check passed successfully" }
    }
}