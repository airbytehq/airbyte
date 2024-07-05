/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.databind.JsonNode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.util.*

private val LOGGER = KotlinLogging.logger {}

object RecordWaitTimeUtil {

    val MIN_FIRST_RECORD_WAIT_TIME: Duration = Duration.ofMinutes(2)
    val MAX_FIRST_RECORD_WAIT_TIME: Duration = Duration.ofMinutes(60)
    val DEFAULT_FIRST_RECORD_WAIT_TIME: Duration = Duration.ofMinutes(5)
    val DEFAULT_SUBSEQUENT_RECORD_WAIT_TIME: Duration = Duration.ofMinutes(1)

    @JvmStatic
    fun checkFirstRecordWaitTime(config: JsonNode) {
        // we need to skip the check because in tests, we set initial_waiting_seconds
        // to 5 seconds for performance reasons, which is shorter than the minimum
        // value allowed in production
        if (config.has("is_test") && config["is_test"].asBoolean()) {
            return
        }

        val firstRecordWaitSeconds = getFirstRecordWaitSeconds(config)
        if (firstRecordWaitSeconds.isPresent) {
            val seconds = firstRecordWaitSeconds.get()
            require(
                !(seconds < MIN_FIRST_RECORD_WAIT_TIME.seconds ||
                    seconds > MAX_FIRST_RECORD_WAIT_TIME.seconds)
            ) {
                String.format(
                    "initial_waiting_seconds must be between %d and %d seconds",
                    MIN_FIRST_RECORD_WAIT_TIME.seconds,
                    MAX_FIRST_RECORD_WAIT_TIME.seconds
                )
            }
        }
    }

    @JvmStatic
    fun getFirstRecordWaitTime(config: JsonNode): Duration {
        val isTest = config.has("is_test") && config["is_test"].asBoolean()
        var firstRecordWaitTime = DEFAULT_FIRST_RECORD_WAIT_TIME

        val firstRecordWaitSeconds = getFirstRecordWaitSeconds(config)
        if (firstRecordWaitSeconds.isPresent) {
            firstRecordWaitTime = Duration.ofSeconds(firstRecordWaitSeconds.get().toLong())
            if (!isTest && firstRecordWaitTime.compareTo(MIN_FIRST_RECORD_WAIT_TIME) < 0) {
                LOGGER.warn {
                    "First record waiting time is overridden to ${MIN_FIRST_RECORD_WAIT_TIME.toMinutes()} minutes, " +
                        "which is the min time allowed for safety."
                }
                firstRecordWaitTime = MIN_FIRST_RECORD_WAIT_TIME
            } else if (!isTest && firstRecordWaitTime.compareTo(MAX_FIRST_RECORD_WAIT_TIME) > 0) {
                LOGGER.warn {
                    "First record waiting time is overridden to ${MAX_FIRST_RECORD_WAIT_TIME.toMinutes()} minutes, " +
                        "which is the max time allowed for safety."
                }
                firstRecordWaitTime = MAX_FIRST_RECORD_WAIT_TIME
            }
        }

        LOGGER.info { "First record waiting time: ${firstRecordWaitTime.seconds} seconds" }
        return firstRecordWaitTime
    }

    @JvmStatic
    fun getSubsequentRecordWaitTime(config: JsonNode): Duration {
        var subsequentRecordWaitTime = DEFAULT_SUBSEQUENT_RECORD_WAIT_TIME
        val isTest = config.has("is_test") && config["is_test"].asBoolean()
        val firstRecordWaitSeconds = getFirstRecordWaitSeconds(config)
        if (isTest && firstRecordWaitSeconds.isPresent) {
            // In tests, reuse the initial_waiting_seconds property to speed things up.
            subsequentRecordWaitTime = Duration.ofSeconds(firstRecordWaitSeconds.get().toLong())
        }
        LOGGER.info {
            "Subsequent record waiting time: ${subsequentRecordWaitTime.seconds} seconds"
        }
        return subsequentRecordWaitTime
    }

    fun getFirstRecordWaitSeconds(config: JsonNode): Optional<Int> {
        val replicationMethod = config["replication_method"]
        if (replicationMethod != null && replicationMethod.has("initial_waiting_seconds")) {
            val seconds = config["replication_method"]["initial_waiting_seconds"].asInt()
            return Optional.of(seconds)
        }
        return Optional.empty()
    }
}
