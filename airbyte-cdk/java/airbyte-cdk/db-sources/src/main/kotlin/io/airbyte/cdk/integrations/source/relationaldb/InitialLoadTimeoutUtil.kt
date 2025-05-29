/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.relationaldb

import com.fasterxml.jackson.databind.JsonNode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.util.*

private val LOGGER = KotlinLogging.logger {}

object InitialLoadTimeoutUtil {

    val MIN_INITIAL_LOAD_TIMEOUT: Duration = Duration.ofHours(4)
    val MAX_INITIAL_LOAD_TIMEOUT: Duration = Duration.ofHours(24)
    val DEFAULT_INITIAL_LOAD_TIMEOUT: Duration = Duration.ofHours(8)

    @JvmStatic
    fun getInitialLoadTimeout(config: JsonNode): Duration {
        val isTest = config.has("is_test") && config["is_test"].asBoolean()
        var initialLoadTimeout = DEFAULT_INITIAL_LOAD_TIMEOUT

        val initialLoadTimeoutHours = getInitialLoadTimeoutHours(config)

        if (initialLoadTimeoutHours.isPresent) {
            initialLoadTimeout = Duration.ofHours(initialLoadTimeoutHours.get().toLong())
            if (!isTest && initialLoadTimeout.compareTo(MIN_INITIAL_LOAD_TIMEOUT) < 0) {
                LOGGER.warn {
                    "Initial Load timeout is overridden to ${MIN_INITIAL_LOAD_TIMEOUT.toHours()} hours, " +
                        "which is the min time allowed for safety."
                }
                initialLoadTimeout = MIN_INITIAL_LOAD_TIMEOUT
            } else if (!isTest && initialLoadTimeout.compareTo(MAX_INITIAL_LOAD_TIMEOUT) > 0) {
                LOGGER.warn {
                    "Initial Load timeout is overridden to ${MAX_INITIAL_LOAD_TIMEOUT.toHours()} hours, " +
                        "which is the max time allowed for safety."
                }
                initialLoadTimeout = MAX_INITIAL_LOAD_TIMEOUT
            }
        }

        LOGGER.info { "Initial Load timeout: ${initialLoadTimeout.seconds} seconds" }
        return initialLoadTimeout
    }

    fun getInitialLoadTimeoutHours(config: JsonNode): Optional<Int> {
        val replicationMethod = config["replication_method"]
        if (replicationMethod != null && replicationMethod.has("initial_load_timeout_hours")) {
            val seconds = config["replication_method"]["initial_load_timeout_hours"].asInt()
            return Optional.of(seconds)
        }
        return Optional.empty()
    }
}
