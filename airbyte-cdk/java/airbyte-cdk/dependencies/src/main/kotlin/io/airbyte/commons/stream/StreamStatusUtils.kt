/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.stream

import io.airbyte.commons.util.AirbyteStreamAware
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import java.util.*
import java.util.function.Consumer
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/** Collection of utility methods that support the generation of stream status updates. */
object StreamStatusUtils {
    private val LOGGER: Logger = LoggerFactory.getLogger(StreamStatusUtils::class.java)

    /**
     * Creates a new [Consumer] that wraps the provided [Consumer] with stream status reporting
     * capabilities. Specifically, this consumer will emit an [AirbyteStreamStatus.RUNNING] status
     * after the first message is consumed by the delegated [Consumer].
     *
     * @param stream The stream from which the delegating [Consumer] will consume messages for
     * processing.
     * @param delegateRecordCollector The delegated [Consumer] that will be called when this
     * consumer accepts a message for processing.
     * @param streamStatusEmitter The optional [Consumer] that will be used to emit stream status
     * updates.
     * @return A wrapping [Consumer] that provides stream status updates when the provided delegate
     * [Consumer] is invoked.
     */
    fun statusTrackingRecordCollector(
        stream: AutoCloseableIterator<AirbyteMessage>,
        delegateRecordCollector: Consumer<AirbyteMessage>,
        streamStatusEmitter: Optional<Consumer<AirbyteStreamStatusHolder>>
    ): Consumer<AirbyteMessage> {
        return object : Consumer<AirbyteMessage> {
            private var firstRead = true

            override fun accept(airbyteMessage: AirbyteMessage) {
                try {
                    delegateRecordCollector.accept(airbyteMessage)
                } finally {
                    if (firstRead) {
                        emitRunningStreamStatus(stream, streamStatusEmitter)
                        firstRead = false
                    }
                }
            }
        }
    }

    /**
     * Emits a [AirbyteStreamStatus.RUNNING] stream status for the provided stream.
     *
     * @param airbyteStream The stream that should be associated with the stream status.
     * @param statusEmitter The [Optional] stream status emitter.
     */
    fun emitRunningStreamStatus(
        airbyteStream: AutoCloseableIterator<AirbyteMessage>,
        statusEmitter: Optional<Consumer<AirbyteStreamStatusHolder>>
    ) {
        emitRunningStreamStatus(airbyteStream as AirbyteStreamAware, statusEmitter)
    }

    /**
     * Emits a [AirbyteStreamStatus.RUNNING] stream status for the provided stream.
     *
     * @param airbyteStream The stream that should be associated with the stream status.
     * @param statusEmitter The [Optional] stream status emitter.
     */
    fun emitRunningStreamStatus(
        airbyteStream: AirbyteStreamAware,
        statusEmitter: Optional<Consumer<AirbyteStreamStatusHolder>>
    ) {
        emitRunningStreamStatus(airbyteStream.airbyteStream, statusEmitter)
    }

    /**
     * Emits a [AirbyteStreamStatus.RUNNING] stream status for the provided stream.
     *
     * @param airbyteStream The stream that should be associated with the stream status.
     * @param statusEmitter The [Optional] stream status emitter.
     */
    fun emitRunningStreamStatus(
        airbyteStream: Optional<AirbyteStreamNameNamespacePair>,
        statusEmitter: Optional<Consumer<AirbyteStreamStatusHolder>>
    ) {
        airbyteStream.ifPresent { s: AirbyteStreamNameNamespacePair ->
            LOGGER.debug("RUNNING -> {}", s)
            emitStreamStatus(
                s,
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.RUNNING,
                statusEmitter
            )
        }
    }

    /**
     * Emits a [AirbyteStreamStatus.STARTED] stream status for the provided stream.
     *
     * @param airbyteStream The stream that should be associated with the stream status.
     * @param statusEmitter The [Optional] stream status emitter.
     */
    fun emitStartStreamStatus(
        airbyteStream: AutoCloseableIterator<AirbyteMessage>,
        statusEmitter: Optional<Consumer<AirbyteStreamStatusHolder>>
    ) {
        emitStartStreamStatus(airbyteStream as AirbyteStreamAware, statusEmitter)
    }

    /**
     * Emits a [AirbyteStreamStatus.STARTED] stream status for the provided stream.
     *
     * @param airbyteStream The stream that should be associated with the stream status.
     * @param statusEmitter The [Optional] stream status emitter.
     */
    fun emitStartStreamStatus(
        airbyteStream: AirbyteStreamAware,
        statusEmitter: Optional<Consumer<AirbyteStreamStatusHolder>>
    ) {
        emitStartStreamStatus(airbyteStream.airbyteStream, statusEmitter)
    }

    /**
     * Emits a [AirbyteStreamStatus.STARTED] stream status for the provided stream.
     *
     * @param airbyteStream The stream that should be associated with the stream status.
     * @param statusEmitter The [Optional] stream status emitter.
     */
    fun emitStartStreamStatus(
        airbyteStream: Optional<AirbyteStreamNameNamespacePair>,
        statusEmitter: Optional<Consumer<AirbyteStreamStatusHolder>>
    ) {
        airbyteStream.ifPresent { s: AirbyteStreamNameNamespacePair ->
            LOGGER.debug("STARTING -> {}", s)
            emitStreamStatus(
                s,
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED,
                statusEmitter
            )
        }
    }

    /**
     * Emits a [AirbyteStreamStatus.COMPLETE] stream status for the provided stream.
     *
     * @param airbyteStream The stream that should be associated with the stream status.
     * @param statusEmitter The [Optional] stream status emitter.
     */
    fun emitCompleteStreamStatus(
        airbyteStream: AutoCloseableIterator<AirbyteMessage>,
        statusEmitter: Optional<Consumer<AirbyteStreamStatusHolder>>
    ) {
        emitCompleteStreamStatus(airbyteStream as AirbyteStreamAware, statusEmitter)
    }

    /**
     * Emits a [AirbyteStreamStatus.COMPLETE] stream status for the provided stream.
     *
     * @param airbyteStream The stream that should be associated with the stream status.
     * @param statusEmitter The [Optional] stream status emitter.
     */
    fun emitCompleteStreamStatus(
        airbyteStream: AirbyteStreamAware,
        statusEmitter: Optional<Consumer<AirbyteStreamStatusHolder>>
    ) {
        emitCompleteStreamStatus(airbyteStream.airbyteStream, statusEmitter)
    }

    /**
     * Emits a [AirbyteStreamStatus.COMPLETE] stream status for the provided stream.
     *
     * @param airbyteStream The stream that should be associated with the stream status.
     * @param statusEmitter The [Optional] stream status emitter.
     */
    fun emitCompleteStreamStatus(
        airbyteStream: Optional<AirbyteStreamNameNamespacePair>,
        statusEmitter: Optional<Consumer<AirbyteStreamStatusHolder>>
    ) {
        airbyteStream.ifPresent { s: AirbyteStreamNameNamespacePair ->
            LOGGER.debug("COMPLETE -> {}", s)
            emitStreamStatus(
                s,
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE,
                statusEmitter
            )
        }
    }

    /**
     * Emits a [AirbyteStreamStatus.INCOMPLETE] stream status for the provided stream.
     *
     * @param airbyteStream The stream that should be associated with the stream status.
     * @param statusEmitter The [Optional] stream status emitter.
     */
    fun emitIncompleteStreamStatus(
        airbyteStream: AutoCloseableIterator<AirbyteMessage>,
        statusEmitter: Optional<Consumer<AirbyteStreamStatusHolder>>
    ) {
        emitIncompleteStreamStatus(airbyteStream as AirbyteStreamAware, statusEmitter)
    }

    /**
     * Emits a [AirbyteStreamStatus.INCOMPLETE] stream status for the provided stream.
     *
     * @param airbyteStream The stream that should be associated with the stream status.
     * @param statusEmitter The [Optional] stream status emitter.
     */
    fun emitIncompleteStreamStatus(
        airbyteStream: AirbyteStreamAware,
        statusEmitter: Optional<Consumer<AirbyteStreamStatusHolder>>
    ) {
        emitIncompleteStreamStatus(airbyteStream.airbyteStream, statusEmitter)
    }

    /**
     * Emits a [AirbyteStreamStatus.INCOMPLETE] stream status for the provided stream.
     *
     * @param airbyteStream The stream that should be associated with the stream status.
     * @param statusEmitter The [Optional] stream status emitter.
     */
    fun emitIncompleteStreamStatus(
        airbyteStream: Optional<AirbyteStreamNameNamespacePair>,
        statusEmitter: Optional<Consumer<AirbyteStreamStatusHolder>>
    ) {
        airbyteStream.ifPresent { s: AirbyteStreamNameNamespacePair ->
            LOGGER.debug("INCOMPLETE -> {}", s)
            emitStreamStatus(
                s,
                AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.INCOMPLETE,
                statusEmitter
            )
        }
    }

    /**
     * Emits a stream status for the provided stream.
     *
     * @param airbyteStreamNameNamespacePair The stream identifier.
     * @param airbyteStreamStatus The status update.
     * @param statusEmitter The [Optional] stream status emitter.
     */
    private fun emitStreamStatus(
        airbyteStreamNameNamespacePair: AirbyteStreamNameNamespacePair?,
        airbyteStreamStatus: AirbyteStreamStatusTraceMessage.AirbyteStreamStatus,
        statusEmitter: Optional<Consumer<AirbyteStreamStatusHolder>>
    ) {
        statusEmitter.ifPresent {
            it.accept(
                AirbyteStreamStatusHolder(airbyteStreamNameNamespacePair, airbyteStreamStatus)
            )
        }
    }
}
