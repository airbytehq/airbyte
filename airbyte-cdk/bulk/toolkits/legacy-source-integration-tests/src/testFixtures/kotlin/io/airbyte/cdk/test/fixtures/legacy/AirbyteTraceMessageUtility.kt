/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import io.airbyte.protocol.models.v0.*
import java.time.Instant
import java.util.function.Consumer
import org.apache.commons.lang3.exception.ExceptionUtils

object AirbyteTraceMessageUtility {
    fun emitSystemErrorTrace(e: Throwable, displayMessage: String?) {
        emitErrorTrace(e, displayMessage, AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR)
    }

    @JvmStatic
    fun emitConfigErrorTrace(e: Throwable, displayMessage: String?) {
        if (e is ConfigErrorException) {
            emitErrorTrace(
                e,
                displayMessage,
                AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
                e.internalMessage,
            )
        } else {
            emitErrorTrace(e, displayMessage, AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR)
        }
    }

    @JvmStatic
    fun emitTransientErrorTrace(e: Throwable, displayMessage: String?) {
        if (e is TransientErrorException) {
            emitErrorTrace(
                e,
                displayMessage,
                AirbyteErrorTraceMessage.FailureType.TRANSIENT_ERROR,
                e.internalMessage,
            )
        } else {
            emitErrorTrace(e, displayMessage, AirbyteErrorTraceMessage.FailureType.TRANSIENT_ERROR)
        }
    }

    fun emitCustomErrorTrace(displayMessage: String?, internalMessage: String?) {
        emitMessage(
            makeAirbyteMessageFromTraceMessage(
                makeAirbyteTraceMessage(AirbyteTraceMessage.Type.ERROR)
                    .withError(
                        AirbyteErrorTraceMessage()
                            .withFailureType(AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR)
                            .withMessage(displayMessage)
                            .withInternalMessage(internalMessage)
                    )
            )
        )
    }

    @JvmStatic
    fun emitEstimateTrace(
        byteEstimate: Long,
        type: AirbyteEstimateTraceMessage.Type?,
        rowEstimate: Long,
        streamName: String?,
        streamNamespace: String?
    ) {
        emitMessage(
            makeAirbyteMessageFromTraceMessage(
                makeAirbyteTraceMessage(AirbyteTraceMessage.Type.ESTIMATE)
                    .withEstimate(
                        AirbyteEstimateTraceMessage()
                            .withByteEstimate(byteEstimate)
                            .withType(type)
                            .withRowEstimate(rowEstimate)
                            .withName(streamName)
                            .withNamespace(streamNamespace)
                    )
            )
        )
    }

    @JvmStatic
    fun emitAnalyticsTrace(airbyteAnalyticsTraceMessage: AirbyteAnalyticsTraceMessage) {
        emitMessage(makeAnalyticsTraceAirbyteMessage(airbyteAnalyticsTraceMessage))
    }

    @JvmStatic
    fun emitErrorTrace(
        e: Throwable,
        displayMessage: String?,
        failureType: AirbyteErrorTraceMessage.FailureType,
        internalMessage: String = "",
    ) {
        emitMessage(makeErrorTraceAirbyteMessage(e, displayMessage, failureType, internalMessage))
    }

    @JvmStatic
    fun emitStreamStatusTrace(airbyteStreamStatusHolder: AirbyteStreamStatusHolder) {
        emitMessage(makeStreamStatusTraceAirbyteMessage(airbyteStreamStatusHolder))
    }

    // todo: handle the other types of trace message we'll expect in the future, see
    // io.airbyte.protocol.models.v0.AirbyteTraceMessage
    // & the tech spec:
    // https://docs.google.com/document/d/1ctrj3Yh_GjtQ93aND-WH3ocqGxsmxyC3jfiarrF6NY0/edit#
    // public void emitNotificationTrace() {}
    // public void emitMetricTrace() {}
    private fun emitMessage(message: AirbyteMessage) {
        // Not sure why defaultOutputRecordCollector is under Destination specifically,
        // but this matches usage elsewhere in base-java
        val outputRecordCollector =
            Consumer<AirbyteMessage> { m: AirbyteMessage ->
                Destination.Companion.defaultOutputRecordCollector(m)
            }
        outputRecordCollector.accept(message)
    }

    fun makeErrorTraceAirbyteMessage(
        e: Throwable,
        displayMessage: String?,
        failureType: AirbyteErrorTraceMessage.FailureType,
        internalMessage: String = "",
    ): AirbyteMessage {
        val actualInternalMessage: String =
            if (internalMessage.isEmpty()) {
                e.toString()
            } else {
                internalMessage + "\n" + e.toString()
            }
        return makeAirbyteMessageFromTraceMessage(
            makeAirbyteTraceMessage(AirbyteTraceMessage.Type.ERROR)
                .withError(
                    AirbyteErrorTraceMessage()
                        .withFailureType(failureType)
                        .withMessage(displayMessage)
                        .withInternalMessage(actualInternalMessage)
                        .withStackTrace(ExceptionUtils.getStackTrace(e))
                )
        )
    }

    private fun makeAnalyticsTraceAirbyteMessage(
        airbyteAnalyticsTraceMessage: AirbyteAnalyticsTraceMessage
    ): AirbyteMessage {
        return AirbyteMessage()
            .withType(AirbyteMessage.Type.TRACE)
            .withTrace(
                AirbyteTraceMessage()
                    .withAnalytics(airbyteAnalyticsTraceMessage)
                    .withType(AirbyteTraceMessage.Type.ANALYTICS)
                    .withEmittedAt(Instant.now().toEpochMilli().toDouble())
            )
    }

    fun makeStreamStatusTraceAirbyteMessage(
        airbyteStreamStatusHolder: AirbyteStreamStatusHolder
    ): AirbyteMessage {
        return makeAirbyteMessageFromTraceMessage(airbyteStreamStatusHolder.toTraceMessage())
    }

    private fun makeAirbyteMessageFromTraceMessage(
        airbyteTraceMessage: AirbyteTraceMessage
    ): AirbyteMessage {
        return AirbyteMessage().withType(AirbyteMessage.Type.TRACE).withTrace(airbyteTraceMessage)
    }

    private fun makeAirbyteTraceMessage(
        traceMessageType: AirbyteTraceMessage.Type
    ): AirbyteTraceMessage {
        return AirbyteTraceMessage()
            .withType(traceMessageType)
            .withEmittedAt(System.currentTimeMillis().toDouble())
    }
}
