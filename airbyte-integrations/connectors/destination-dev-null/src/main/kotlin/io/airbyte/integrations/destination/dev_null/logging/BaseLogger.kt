/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.dev_null.logging

import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneId
import java.time.format.DateTimeFormatter

abstract class BaseLogger(
    protected val streamNamePair: AirbyteStreamNameNamespacePair,
    protected val maxEntryCount: Int
) : TestingLogger {
    protected var loggedEntryCount: Int = 0

    protected fun entryMessage(recordMessage: AirbyteRecordMessage): String {
        return String.format(
            "[%s] %s #%04d: %s",
            emissionTimestamp(recordMessage.emittedAt),
            streamName(streamNamePair),
            loggedEntryCount,
            recordMessage.data
        )
    }

    companion object {
        protected fun streamName(pair: AirbyteStreamNameNamespacePair): String {
            return if (pair.namespace == null) {
                pair.name
            } else {
                String.format("%s.%s", pair.namespace, pair.name)
            }
        }

        protected fun emissionTimestamp(emittedAt: Long): String {
            return OffsetDateTime.ofInstant(Instant.ofEpochMilli(emittedAt), ZoneId.systemDefault())
                .format(DateTimeFormatter.ISO_OFFSET_DATE_TIME)
        }
    }
}
