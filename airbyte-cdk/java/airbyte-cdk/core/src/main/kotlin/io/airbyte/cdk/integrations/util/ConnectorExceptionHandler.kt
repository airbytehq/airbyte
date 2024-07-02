/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.util

import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility
import io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.exceptions.ConnectionErrorException
import io.airbyte.commons.exceptions.TransientErrorException
import io.github.oshai.kotlinlogging.KotlinLogging
import io.airbyte.cdk.integrations.base.Command
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import  java.util.function.Consumer
import io.airbyte.protocol.models.v0.AirbyteMessage

private val LOGGER = KotlinLogging.logger {}

const val COMMON_EXCEPTION_MESSAGE_TEMPLATE: String =
    "Could not connect with provided configuration. Error: %s"

const val DATABASE_CONNECTION_ERROR: String =
    "Encountered an error while connecting to the database error"

data class ConnectorErrorProfile(
    var errorClass: String,
    var regexMatchingPattern: String,
    var failureType: String,
    var externalMessage: String,
    var sampleInternalMessage: String,
    var referenceLink: List<String>)

/**
 * This abstract class defines interfaces that will be implemented by individual connectors for
 *  translating internal exception error messages to external user-friendly error messages.
 */
abstract class ConnectorExceptionHandler {
    @kotlin.jvm.JvmField
    var DATABASE_READ_ERROR: String =
        "Encountered an error while reading the database"

    /**
     * Translates an internal exception message to an external user-friendly message.
     * This is the main entrance of the error translation process.
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
            if (e!!.message != null) e.message else ""
        )
    }

    /**
     * Initializes the error dictionary for the connector.
     * This method should be implemented by individual connectors that wish to translate
     * connector specific error messages.
     */
    //open fun initializeErrorDictionary() {}

    /**
     * Translates a connector specific error message to an external user-friendly message.
     * This method should be implemented by individual connectors that wish to translate connector specific
     * error messages.
     */
    open fun translateConnectorSpecificErrorMessage(e: Throwable?): String? {
        return null
    }

    /**
    * Many of the exceptions thrown are nested inside layers of RuntimeExceptions. An
    * attempt is made to find the root exception that corresponds to a configuration error. If that does not
    * exist, we just return the original exception.
     */
    private fun getRootException(e: Throwable): Throwable? {
        var current: Throwable? = e
        while (current != null) {
            if (isRecognizableError(current)) {
                return current;
            } else {
                current = current.cause
            }
        }
        return e
    }

    fun handleException(e: Throwable, cmd: Command,
                        outputRecordCollector: Consumer<AirbyteMessage>) {
        ApmTraceUtils.addExceptionToTrace(e)
        val rootException: Throwable? = getRootException(e);
        val externalMessage: String? = getExternalMessage(rootException)
        if (cmd == Command.CHECK) {
            outputRecordCollector.accept(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                    .withConnectionStatus(
                        AirbyteConnectionStatus()
                            .withStatus(AirbyteConnectionStatus.Status.FAILED)
                            .withMessage(externalMessage)
                    )
            )
        } else {
            if (checkErrorType(rootException, "config")) {
                AirbyteTraceMessageUtility.emitConfigErrorTrace(e, externalMessage)
                System.exit(1);
            } else if (checkErrorType(rootException, "transient")) {
                AirbyteTraceMessageUtility.emitTransientErrorTrace(e, externalMessage)
                System.exit(1);
            }
            throw e
        }
    }

    open var connectorErrorDictionary: List<ConnectorErrorProfile> = listOf()

    private fun checkErrorType(e: Throwable?, failureType: String?): Boolean {
        for (error in connectorErrorDictionary) {
            if (e != null) {
                if (error.failureType == failureType && e.message?.matches(error.regexMatchingPattern.toRegex())!!)
                    return true
            }
        }
        return false
    }

    /*
    *  Checks if the error can be recognized by us. A recognizable error is either
    *  a transient exception, a config exception, or an exception whose error messages have been
    *  stored as part of the error profile in the error dictionary.
    * */
    fun isRecognizableError(e: Throwable?) : Boolean {
        if (e == null) return false;
        if (e is TransientErrorException || e is ConfigErrorException) {
            return true;
        }
        for (error in connectorErrorDictionary) {
            if (e.message?.matches(error.regexMatchingPattern.toRegex())!!)
                return true
        }
        return false
    }

    fun isTransientError(e: Throwable?): Boolean {
        return (e is TransientErrorException) || checkErrorType(e, "transient")
    }

    fun isConfigError(e: Throwable?): Boolean {
        return  (e is ConfigErrorException)  ||  checkErrorType(e, "config")
    }
}
