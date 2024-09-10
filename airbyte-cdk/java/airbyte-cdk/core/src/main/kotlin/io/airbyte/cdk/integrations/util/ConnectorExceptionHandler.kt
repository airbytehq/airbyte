/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.util

import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility
import io.airbyte.cdk.integrations.base.Command
import io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.exceptions.ConnectionErrorException
import io.airbyte.commons.exceptions.TransientErrorException
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.function.Consumer
import java.util.regex.Pattern
import kotlin.system.exitProcess
import org.jetbrains.annotations.VisibleForTesting

private val LOGGER = KotlinLogging.logger {}

enum class FailureType {
    CONFIG,
    TRANSIENT
}

data class ConnectorErrorProfile(
    val errorClass: String,
    val regexMatchingPattern: String,
    val failureType: FailureType,
    val externalMessage: String,
    val sampleInternalMessage: String,
    val referenceLinks: List<String> = emptyList(),
) {
    val regexPattern: Pattern = Pattern.compile(regexMatchingPattern, Pattern.CASE_INSENSITIVE)
    init {
        require(externalMessage.isNotBlank()) { "externalMessage must not be blank" }
        require(sampleInternalMessage.isNotBlank()) { "sampleInternalMessage must not be blank" }
    }
}

/**
 * This class defines interfaces that will be implemented by individual connectors for translating
 * internal exception error messages to external user-friendly error messages.
 */
open class ConnectorExceptionHandler {
    private val COMMON_EXCEPTION_MESSAGE_TEMPLATE: String =
        "Could not connect with provided configuration. Error: %s"

    protected open val connectorErrorDictionary: MutableList<ConnectorErrorProfile> =
        mutableListOf()

    init {
        initializeErrorDictionary()
    }

    /**
     * Handles exceptions thrown by the connector. This method is the main entrance for handling
     * exceptions thrown by the connector. It checks if the exception is a known exception, and if
     * so, it emits the appropriate trace and external user-friendly error message. If the exception
     * is not known, it rethrows the exception, which becomes a system error.
     */
    fun handleException(
        e: Throwable,
        cmd: Command,
        outputRecordCollector: Consumer<AirbyteMessage>
    ) {
        LOGGER.error(e) { "caught exception!" }
        ApmTraceUtils.addExceptionToTrace(e)
        val rootException: Throwable = getRootException(e)
        val externalMessage: String? = getExternalMessage(rootException)
        /* error messages generated during check() needs special handling */
        if (cmd == Command.CHECK) {
            outputRecordCollector.accept(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                    .withConnectionStatus(
                        AirbyteConnectionStatus()
                            .withStatus(AirbyteConnectionStatus.Status.FAILED)
                            .withMessage(externalMessage),
                    ),
            )
        } else {
            if (checkErrorType(rootException, FailureType.CONFIG)) {
                AirbyteTraceMessageUtility.emitConfigErrorTrace(e, externalMessage)
                exitProcess(1)
            } else if (checkErrorType(rootException, FailureType.TRANSIENT)) {
                AirbyteTraceMessageUtility.emitTransientErrorTrace(e, externalMessage)
                exitProcess(1)
            }
            throw e
        }
    }

    /**
     * Initializes the error dictionary for the connector. This method shall include all the errors
     * that are shared by all connectors.
     */
    open fun initializeErrorDictionary() {}

    /**
     * Translates an internal exception message to an external user-friendly message. This is the
     * main entrance of the error translation process.
     */
    fun getExternalMessage(e: Throwable?): String? {
        // some common translations that every connector would share can be done here
        if (e is ConfigErrorException) {
            return e.displayMessage
        } else if (e is TransientErrorException) {
            return e.message
        } else if (e is ConnectionErrorException) {
            return ErrorMessage.getErrorMessage(e.stateCode, e.errorCode, e.exceptionMessage, e)
        } else {
            val msg = translateConnectorSpecificErrorMessage(e)
            if (msg != null) return msg
        }
        // if no specific translation is found, return a generic message
        return String.format(
            COMMON_EXCEPTION_MESSAGE_TEMPLATE,
            if (e!!.message != null) e.message else "",
        )
    }

    fun add(errorProfile: ConnectorErrorProfile) {
        connectorErrorDictionary.add(errorProfile)
    }

    /**
     * Translates a connector specific error message to an external user-friendly message. This
     * method should be implemented by individual connectors that wish to translate connector
     * specific error messages.
     */
    open fun translateConnectorSpecificErrorMessage(e: Throwable?): String? {
        if (e == null) return null
        for (error in connectorErrorDictionary) if (error.regexPattern.matcher(e.message).matches())
            return error.externalMessage
        return null
    }

    /**
     * Many of the exceptions thrown are nested inside layers of RuntimeExceptions. An attempt is
     * made to find the root exception that corresponds to a configuration error. If that does not
     * exist, we just return the original exception.
     */
    @VisibleForTesting
    internal fun getRootException(e: Throwable): Throwable {
        var current: Throwable? = e
        while (current != null) {
            if (isRecognizableError(current)) {
                return current
            } else {
                current = current.cause
            }
        }
        return e
    }

    @VisibleForTesting
    internal fun checkErrorType(e: Throwable?, failureType: FailureType?): Boolean {
        if (failureType == FailureType.CONFIG && e is ConfigErrorException) {
            return true
        }

        if (failureType == FailureType.TRANSIENT && e is TransientErrorException) {
            return true
        }

        for (error in connectorErrorDictionary) if (
            error.failureType == failureType && error.regexPattern.matcher(e!!.message).matches()
        )
            return true
        return false
    }

    /*
     *  Checks if the error can be recognized. A recognizable error is either
     *  a known transient exception, a config exception, or an exception whose error messages have been
     *  stored as part of the error profile in the error dictionary.
     * */
    @VisibleForTesting
    private fun isRecognizableError(e: Throwable?): Boolean {
        if (e?.message == null) return false
        if (e is TransientErrorException || e is ConfigErrorException) {
            return true
        }
        for (error in connectorErrorDictionary) if (error.regexPattern.matcher(e.message).matches())
            return true
        return false
    }
}
