/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.output

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
import io.airbyte.protocol.models.v0.DestinationCatalog
import io.micronaut.context.annotation.DefaultImplementation
import java.time.Clock
import java.time.Instant
import java.util.function.Consumer

/** Emits the [AirbyteMessage] instances produced by the connector. */
@DefaultImplementation(StdoutOutputConsumer::class)
abstract class OutputConsumer(private val clock: Clock) : Consumer<AirbyteMessage>, AutoCloseable {
    companion object {
        const val IS_DUMMY_STATS_MESSAGE = "isDummyStatsMessage"
    }

    /**
     * The constant emittedAt timestamp we use for record timestamps.
     *
     * TODO: use the correct emittedAt time for each record. Ryan: not changing this now as it could
     * have performance implications for sources given the delicate serialization logic in place
     * here.
     */
    val recordEmittedAt: Instant = Instant.ofEpochMilli(clock.millis())

    open fun accept(record: AirbyteRecordMessage) {
        record.emittedAt = recordEmittedAt.toEpochMilli()
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
        // Use the correct emittedAt timestamp for trace messages. This allows platform and other
        // downstream consumers to take emission time into account for error classification.
        trace.emittedAt = clock.millis().toDouble()
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

    fun accept(destinationCatalog: DestinationCatalog) {
        accept(
            AirbyteMessage()
                .withType(AirbyteMessage.Type.DESTINATION_CATALOG)
                .withDestinationCatalog(destinationCatalog)
        )
    }
}
