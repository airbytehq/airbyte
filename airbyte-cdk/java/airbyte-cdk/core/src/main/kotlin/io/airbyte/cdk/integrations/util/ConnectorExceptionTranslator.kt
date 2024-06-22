/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.util

import io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.exceptions.ConnectionErrorException
import io.airbyte.commons.exceptions.TransientErrorException
import io.github.oshai.kotlinlogging.KotlinLogging

private val LOGGER = KotlinLogging.logger {}

const val COMMON_EXCEPTION_MESSAGE_TEMPLATE: String =
    "Could not connect with provided configuration. Error: %s"

const val DATABASE_CONNECTION_ERROR: String =
    "Encountered an error while connecting to the database error"

class ConnectorErrorProfile {
    var id: Int = 0
    var errorClass: String? = null
    var regexMatchingPattern: String? = null
    var errorType: String? = null // config, transient, system
    var externalMessage: String? = null
    var sampleInternalMessage: String? = null
    var githubIssues: List<String>? = null

    constructor(id: Int, errorClass: String?, regexMatchingPattern: String?,
                errorType: String?, externalMessage: String?, sampleInternalMessage: String?, githubIssues: List<String>?) {
        this.id = id
        this.errorClass = errorClass
        this.regexMatchingPattern = regexMatchingPattern
        this.errorType = errorType
        this.externalMessage = externalMessage
        this.sampleInternalMessage = sampleInternalMessage
        this.githubIssues = githubIssues
    }
}

/**
 * This abstract class defines interfaces that will be implemented by individual connectors for
 *  translating internal exception error messages to external user-friendly error messages.
 */
abstract class ConnectorExceptionTranslator {


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
            ConnectorExceptionUtil.COMMON_EXCEPTION_MESSAGE_TEMPLATE,
            if (e!!.message != null) e.message else ""
        )
    }

    /**
     * Initializes the error dictionary for the connector.
     * This method should be implemented by individual connectors that wish to translate
     * connector specific error messages.
     */
    open fun initializeErrorDictionary() {}

    /**
     * Translates a connector specific error message to an external user-friendly message.
     * This method should be implemented by individual connectors that wish to translate connector specific
     * error messages.
     */
    open fun translateConnectorSpecificErrorMessage(e: Throwable?): String? {
        return null
    }

    public open var connectorErrorDictionary: List<ConnectorErrorProfile> = listOf()

}
