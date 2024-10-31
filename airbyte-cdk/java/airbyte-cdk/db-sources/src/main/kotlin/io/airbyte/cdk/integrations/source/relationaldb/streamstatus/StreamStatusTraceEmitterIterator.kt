/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.relationaldb.streamstatus

import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility.makeStreamStatusTraceAirbyteMessage
import io.airbyte.commons.stream.AirbyteStreamStatusHolder
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.protocol.models.v0.AirbyteMessage
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class StreamStatusTraceEmitterIterator(private val statusHolder: AirbyteStreamStatusHolder) :
    AutoCloseableIterator<AirbyteMessage?> {
    private var emitted = false

    override fun hasNext(): Boolean {
        return !emitted
    }

    override fun next(): AirbyteMessage {
        emitted = true
        return makeStreamStatusTraceAirbyteMessage(statusHolder)
    }

    @Throws(Exception::class)
    override fun close() {
        // no-op
    }

    override fun remove() {
        // no-op
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(StreamStatusTraceEmitterIterator::class.java)
    }
}
