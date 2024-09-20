/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.dev_null.logging

import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class EveryNthLogger(
    streamNamePair: AirbyteStreamNameNamespacePair,
    private val nthEntryToLog: Int,
    maxEntryCount: Int
) : BaseLogger(streamNamePair, maxEntryCount), TestingLogger {
    private var currentEntry = 0

    override fun log(recordMessage: AirbyteRecordMessage?) {
        if (loggedEntryCount >= maxEntryCount) {
            return
        }

        currentEntry += 1
        if (currentEntry % nthEntryToLog == 0) {
            loggedEntryCount += 1
            LOGGER.info(entryMessage(recordMessage!!))
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(EveryNthLogger::class.java)
    }
}
