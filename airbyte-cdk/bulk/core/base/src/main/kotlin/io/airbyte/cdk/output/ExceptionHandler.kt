/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output

import io.airbyte.cdk.util.ApmTraceUtils
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import jakarta.inject.Singleton
import org.apache.commons.lang3.exception.ExceptionUtils

/** [ExceptionHandler] applies all available [ExceptionClassifier] implementations in sequence. */
@Singleton
class ExceptionHandler(val classifiers: List<ExceptionClassifier>) {

    fun classify(e: Throwable): ConnectorError {
        for (classifier in classifiers) {
            val classified: ConnectorError? = classifier.classify(e)
            if (classified != null) {
                return classified
            }
        }
        return SystemError(e.message)
    }

    /** Maps [e] to a [AirbyteErrorTraceMessage] to be passed to the [OutputConsumer]. */
    fun handle(e: Throwable): AirbyteErrorTraceMessage {
        ApmTraceUtils.addExceptionToTrace(e)
        val errorTraceMessage =
            AirbyteErrorTraceMessage()
                .withInternalMessage(e.toString())
                .withStackTrace(ExceptionUtils.getStackTrace(e))
        return when (val classified: ConnectorError = classify(e)) {
            is ConfigError ->
                errorTraceMessage
                    .withFailureType(AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR)
                    .withMessage(classified.displayMessage)
            is TransientError ->
                errorTraceMessage
                    .withFailureType(AirbyteErrorTraceMessage.FailureType.TRANSIENT_ERROR)
                    .withMessage(classified.displayMessage)
            is SystemError ->
                errorTraceMessage
                    .withFailureType(AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR)
                    .withMessage(classified.displayMessage ?: e.message)
        }
    }

    fun handleCheckFailure(e: Throwable): Pair<AirbyteErrorTraceMessage, AirbyteConnectionStatus> {
        val errorTraceMessage: AirbyteErrorTraceMessage = handle(e)
        errorTraceMessage.failureType = AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR
        val connectionStatusMessage: String =
            String.format(COMMON_EXCEPTION_MESSAGE_TEMPLATE, errorTraceMessage.message)

        return Pair(
            errorTraceMessage,
            AirbyteConnectionStatus()
                .withMessage(connectionStatusMessage)
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
        )
    }

    companion object {
        const val COMMON_EXCEPTION_MESSAGE_TEMPLATE: String =
            "Could not connect with provided configuration. Error: %s"
    }
}
