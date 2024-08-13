/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.output

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteAnalyticsTraceMessage
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.airbyte.protocol.models.v0.AirbyteEstimateTraceMessage
import io.airbyte.protocol.models.v0.AirbyteLogMessage
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.micronaut.context.annotation.DefaultImplementation
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.time.Instant
import java.util.function.Consumer
import org.apache.commons.lang3.exception.ExceptionUtils

/** Emits the [AirbyteMessage] instances produced by the connector. */
@DefaultImplementation(StdoutOutputConsumer::class)
interface OutputConsumer : Consumer<AirbyteMessage>, AutoCloseable {
    val emittedAt: Instant

    fun accept(record: AirbyteRecordMessage) {
        record.emittedAt = emittedAt.toEpochMilli()
        accept(AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(record))
    }

    fun accept(state: AirbyteStateMessage) {
        accept(AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(state))
    }

    fun accept(log: AirbyteLogMessage) {
        accept(AirbyteMessage().withType(AirbyteMessage.Type.LOG).withLog(log))
    }

    fun accept(spec: ConnectorSpecification) {
        accept(AirbyteMessage().withType(AirbyteMessage.Type.SPEC).withSpec(spec))
    }

    fun accept(status: AirbyteConnectionStatus) {
        accept(
            AirbyteMessage()
                .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                .withConnectionStatus(status),
        )
    }

    fun accept(catalog: AirbyteCatalog) {
        accept(AirbyteMessage().withType(AirbyteMessage.Type.CATALOG).withCatalog(catalog))
    }

    fun accept(trace: AirbyteTraceMessage) {
        trace.emittedAt = emittedAt.toEpochMilli().toDouble()
        accept(AirbyteMessage().withType(AirbyteMessage.Type.TRACE).withTrace(trace))
    }

    fun accept(error: AirbyteErrorTraceMessage) {
        accept(AirbyteTraceMessage().withType(AirbyteTraceMessage.Type.ERROR).withError(error))
    }

    fun accept(estimate: AirbyteEstimateTraceMessage) {
        accept(
            AirbyteTraceMessage()
                .withType(AirbyteTraceMessage.Type.ESTIMATE)
                .withEstimate(estimate),
        )
    }

    fun accept(streamStatus: AirbyteStreamStatusTraceMessage) {
        accept(
            AirbyteTraceMessage()
                .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                .withStreamStatus(streamStatus),
        )
    }

    fun accept(analytics: AirbyteAnalyticsTraceMessage) {
        accept(
            AirbyteTraceMessage()
                .withType(AirbyteTraceMessage.Type.ANALYTICS)
                .withAnalytics(analytics),
        )
    }

    fun acceptTraceOnConfigError(e: Throwable) {
        val configErrorException: ConfigErrorException = ConfigErrorException.unwind(e) ?: return
        accept(
            AirbyteErrorTraceMessage()
                .withFailureType(AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR)
                .withMessage(configErrorException.message)
                .withInternalMessage(e.toString())
                .withStackTrace(ExceptionUtils.getStackTrace(e)),
        )
    }
}

// Used for integration tests.
const val CONNECTOR_OUTPUT_FILE = "airbyte.connector.output.file"

/** Default implementation of [OutputConsumer]. */
@Singleton
@Secondary
private class StdoutOutputConsumer : OutputConsumer {
    override val emittedAt: Instant = Instant.now()

    private val buffer = ByteArrayOutputStream()

    override fun accept(airbyteMessage: AirbyteMessage) {
        // This method effectively println's its JSON-serialized argument.
        // Using println is not particularly efficient, however.
        // To improve performance, this method accumulates RECORD messages into a buffer
        // before writing them to standard output in a batch.
        // Other Airbyte message types are not buffered, instead they trigger an immediate flush.
        // Such messages should not linger indefinitely in a buffer.
        val isRecord: Boolean = airbyteMessage.type == AirbyteMessage.Type.RECORD
        val json: ByteArray = Jsons.writeValueAsBytes(airbyteMessage)
        synchronized(this) {
            if (buffer.size() > 0) {
                buffer.write('\n'.code)
            }
            buffer.writeBytes(json)
            if (!isRecord || buffer.size() >= BUFFER_MAX_SIZE) {
                withLockFlush()
            }
        }
    }

    override fun close() {
        synchronized(this) {
            // Flush any remaining buffer contents to stdout before closing.
            withLockFlush()
        }
    }

    private fun withLockFlush() {
        if (buffer.size() > 0) {
            println(buffer.toString(Charsets.UTF_8))
            buffer.reset()
        }
    }

    companion object {
        const val BUFFER_MAX_SIZE = 1024 * 1024
    }
}
