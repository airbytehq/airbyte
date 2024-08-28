/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.ConnectorErrorException
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.TransientErrorException
import io.micronaut.context.annotation.ConfigurationProperties
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton

const val DEFAULT_CLASSIFIER_PREFIX = "${EXCEPTION_CLASSIFIER_PREFIX}.default"

/** Default implementation of [ExceptionClassifier]. */
@Singleton
@ConfigurationProperties(DEFAULT_CLASSIFIER_PREFIX)
class DefaultExceptionClassifier(
    @Value("\${$DEFAULT_CLASSIFIER_PREFIX.order:1}") override val orderValue: Int
) : ExceptionClassifier {

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
