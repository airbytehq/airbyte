/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.output

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.ConnectorErrorException
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.util.ApmTraceUtils
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.micronaut.context.annotation.DefaultImplementation
import jakarta.inject.Singleton
import org.apache.commons.lang3.exception.ExceptionUtils

@Singleton
@DefaultImplementation(DefaultExceptionClassifier::class)
fun interface ExceptionClassifier {

    /** Classifies [e] into a [ConnectorError] if possible, null otherwise. */
    fun classify(e: Throwable): ConnectorError?

    /** [SystemError] display message for [e] in case it can't be classified. */
    fun fallbackDisplayMessage(e: Throwable): String? = e.message

    /** Maps [e] to a [AirbyteErrorTraceMessage] to be passed to the [OutputConsumer]. */
    fun handle(e: Throwable): AirbyteErrorTraceMessage {
        ApmTraceUtils.addExceptionToTrace(e)
        val connectorError: ConnectorError =
            DefaultExceptionClassifier().classify(e)
                ?: classify(e) ?: SystemError(fallbackDisplayMessage(e) ?: e.message)
        val errorTraceMessage =
            AirbyteErrorTraceMessage()
                .withInternalMessage(e.toString())
                .withStackTrace(ExceptionUtils.getStackTrace(e))
        return when (connectorError) {
            is ConfigError ->
                errorTraceMessage
                    .withFailureType(AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR)
                    .withMessage(connectorError.displayMessage)
            is TransientError ->
                errorTraceMessage
                    .withFailureType(AirbyteErrorTraceMessage.FailureType.TRANSIENT_ERROR)
                    .withMessage(connectorError.displayMessage)
            is SystemError ->
                errorTraceMessage
                    .withFailureType(AirbyteErrorTraceMessage.FailureType.SYSTEM_ERROR)
                    .withMessage(connectorError.displayMessage ?: e.message)
        }
    }
}

/** Each [ConnectorError] subtype corresponds to a [AirbyteErrorTraceMessage.FailureType]. */
sealed interface ConnectorError

/**
 * A [ConfigError] means there is something wrong with the user's connector configuration or any
 * other error for which the connector informs the platform that the error is not transient in
 * nature and thus to not bother retrying.
 */
data class ConfigError(val displayMessage: String) : ConnectorError

/**
 * A [TransientError] means there is something wrong with the user's source or any other error for
 * which the connector informs the platform that the error is transient in nature.
 */
data class TransientError(val displayMessage: String) : ConnectorError

/**
 * A [SystemError] means there is something wrong with the connector.
 *
 * In practice these are also ll errors that are neither [ConfigError] or [TransientError]. This is
 * whatever falls through the cracks of the [ExceptionClassifier], as such there is a standing goal
 * to minimize occurrences of these instances.
 */
data class SystemError(val displayMessage: String?) : ConnectorError

/** Default implementation of [ExceptionClassifier]. */
@Singleton
class DefaultExceptionClassifier : ExceptionClassifier {

    override fun classify(e: Throwable): ConnectorError? {
        return when (val connectorErrorException: ConnectorErrorException? = unwind(e)) {
            is ConfigErrorException -> ConfigError(connectorErrorException.message!!)
            is TransientErrorException -> TransientError(connectorErrorException.message!!)
            is SystemErrorException -> SystemError(connectorErrorException.message)
            null -> null
        }
    }

    /** Recursively walks the causes of [e] and returns the last [ConnectorErrorException]. */
    fun unwind(e: Throwable): ConnectorErrorException? {
        var connectorErrorException: ConnectorErrorException? = null
        var unwound: Throwable? = e
        while (unwound != null) {
            if (unwound is ConnectorErrorException) {
                connectorErrorException = unwound
            }
            unwound = unwound.cause
        }
        return connectorErrorException
    }
}
