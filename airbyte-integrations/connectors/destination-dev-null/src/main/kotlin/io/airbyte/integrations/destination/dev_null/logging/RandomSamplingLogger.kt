/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.dev_null.logging

import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import java.util.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class RandomSamplingLogger(
    streamNamePair: AirbyteStreamNameNamespacePair,
    private val samplingRatio: Double,
    seed: Long,
    maxEntryCount: Int
) : BaseLogger(streamNamePair, maxEntryCount), TestingLogger {
    private val random = Random(seed)

    override fun log(recordMessage: AirbyteRecordMessage?) {
        if (loggedEntryCount >= maxEntryCount) {
            return
        }

        if (random.nextDouble() < samplingRatio) {
            loggedEntryCount += 1
            LOGGER.info(entryMessage(recordMessage!!))
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(RandomSamplingLogger::class.java)
    }
}
