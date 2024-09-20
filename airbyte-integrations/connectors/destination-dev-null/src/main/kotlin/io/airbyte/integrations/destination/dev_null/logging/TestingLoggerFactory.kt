/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.dev_null.logging

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair

class TestingLoggerFactory(private val config: JsonNode) {
    fun create(streamNamePair: AirbyteStreamNameNamespacePair): TestingLogger {
        require(config.has("test_destination")) {
            "Property test_destination is required, but not found"
        }

        val testDestinationConfig = config["test_destination"]

        require(testDestinationConfig.has("logging_config")) {
            "Property logging_config is required, but not found"
        }

        val logConfig = testDestinationConfig["logging_config"]
        val loggingType = TestingLogger.LoggingType.valueOf(logConfig["logging_type"].asText())
        when (loggingType) {
            TestingLogger.LoggingType.FirstN -> {
                val maxEntryCount = logConfig["max_entry_count"].asInt()
                return FirstNLogger(streamNamePair, maxEntryCount)
            }
            TestingLogger.LoggingType.EveryNth -> {
                val nthEntryToLog = logConfig["nth_entry_to_log"].asInt()
                val maxEntryCount = logConfig["max_entry_count"].asInt()
                return EveryNthLogger(streamNamePair, nthEntryToLog, maxEntryCount)
            }
            TestingLogger.LoggingType.RandomSampling -> {
                val samplingRatio = logConfig["sampling_ratio"].asDouble()
                val seed =
                    if (logConfig.has("seed")) logConfig["seed"].asLong()
                    else System.currentTimeMillis()
                val maxEntryCount = logConfig["max_entry_count"].asInt()
                return RandomSamplingLogger(streamNamePair, samplingRatio, seed, maxEntryCount)
            }
            else -> throw IllegalArgumentException("Unexpected logging type: $loggingType")
        }
    }
}
