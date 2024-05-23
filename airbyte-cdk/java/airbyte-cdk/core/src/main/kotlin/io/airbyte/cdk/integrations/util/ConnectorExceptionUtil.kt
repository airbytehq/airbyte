/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.util

import com.google.common.collect.ImmutableList
import io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.exceptions.ConnectionErrorException
import io.airbyte.commons.exceptions.TransientErrorException
import io.airbyte.commons.functional.Either
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.EOFException
import java.sql.SQLException
import java.sql.SQLSyntaxErrorException
import org.apache.commons.lang3.exception.ExceptionUtils

private val LOGGER = KotlinLogging.logger {}
/** Utility class defining methods for handling configuration exceptions in connectors. */
object ConnectorExceptionUtil {

    const val COMMON_EXCEPTION_MESSAGE_TEMPLATE: String =
        "Could not connect with provided configuration. Error: %s"
    const val RECOVERY_CONNECTION_ERROR_MESSAGE: String =
        "We're having issues syncing from a Postgres replica that is configured as a hot standby server. " +
            "Please see https://go.airbyte.com/pg-hot-standby-error-message for options and workarounds"
    const val DATABASE_CONNECTION_ERROR: String =
        "Encountered an error while connecting to the database error"

    @JvmField val HTTP_AUTHENTICATION_ERROR_CODES: List<Int> = ImmutableList.of(401, 403)

    fun isConfigError(e: Throwable?): Boolean {
        return isConfigErrorException(e) ||
            isConnectionError(e) ||
            isUnknownColumnInFieldListException(e)
    }

    fun isTransientError(e: Throwable?): Boolean {
        return isTransientErrorException(e) ||
            isRecoveryConnectionException(e) ||
            isTransientEOFException(e) ||
            isTransientSQLException(e)
    }

    fun getDisplayMessage(e: Throwable?): String? {
        return if (e is ConfigErrorException) {
            e.displayMessage
        } else if (e is TransientErrorException) {
            e.message
        } else if (e is ConnectionErrorException) {
            ErrorMessage.getErrorMessage(e.stateCode, e.errorCode, e.exceptionMessage, e)
        } else if (isRecoveryConnectionException(e)) {
            RECOVERY_CONNECTION_ERROR_MESSAGE
        } else if (isUnknownColumnInFieldListException(e)) {
            e!!.message
        } else if (isTransientError(e)) {
            DATABASE_CONNECTION_ERROR
        } else {
            String.format(
                COMMON_EXCEPTION_MESSAGE_TEMPLATE,
                if (e!!.message != null) e.message else ""
            )
        }
    }

    /**
     * Returns the first instance of an exception associated with a configuration error (if it
     * exists). Otherwise, the original exception is returned.
     */
    fun getRootConfigError(e: Exception?): Throwable? {
        var current: Throwable? = e
        while (current != null) {
            if (isConfigError(current)) {
                return current
            } else {
                current = current.cause
            }
        }
        return e
    }

    /**
     * Returns the first instance of an exception associated with a configuration error (if it
     * exists). Otherwise, the original exception is returned.
     */
    fun getRootTransientError(e: Exception?): Throwable? {
        var current: Throwable? = e
        while (current != null) {
            if (isTransientError(current)) {
                return current
            } else {
                current = current.cause
            }
        }
        return e
    }

    /**
     * Log all the exceptions, and rethrow the first. This is useful for e.g. running multiple
     * futures and waiting for them to complete/fail. Rather than combining them into a single
     * mega-exception (which works poorly in the UI), we just log all of them, and throw the first
     * exception.
     *
     * In most cases, all the exceptions will look very similar, so the user only needs to see the
     * first exception anyway. This mimics e.g. a for-loop over multiple tasks, where the loop would
     * break on the first exception.
     */
    @JvmStatic
    fun <T : Throwable> logAllAndThrowFirst(initialMessage: String, throwables: Collection<T>) {
        if (!throwables.isEmpty()) {
            val stacktraces =
                throwables.joinToString("\n") { throwable: Throwable ->
                    ExceptionUtils.getStackTrace(throwable)
                }
            LOGGER.error { "$initialMessage$stacktraces\nRethrowing first exception." }
            throw throwables.iterator().next()
        }
    }

    @JvmStatic
    fun <T : Throwable, Result> getResultsOrLogAndThrowFirst(
        initialMessage: String,
        eithers: List<Either<out T, Result>>
    ): List<Result> {
        val throwables: List<T> = eithers.filter { it.isLeft() }.map { it.left!! }
        if (throwables.isNotEmpty()) {
            logAllAndThrowFirst(initialMessage, throwables)
        }
        // No need to filter on isRight since isLeft will throw before reaching this line.
        return eithers.map { obj: Either<out T, Result> -> obj.right!! }
    }

    private fun isTransientErrorException(e: Throwable?): Boolean {
        return e is TransientErrorException
    }

    private fun isConfigErrorException(e: Throwable?): Boolean {
        return e is ConfigErrorException
    }

    private fun isConnectionError(e: Throwable?): Boolean {
        return e is ConnectionErrorException
    }

    private fun isTransientEOFException(e: Throwable?): Boolean {
        return (e is EOFException) &&
            e.message!!.lowercase().contains("connection was unexpectedly lost")
    }

    private fun isTransientSQLException(e: Throwable?): Boolean {
        return (e is SQLException) &&
            e.message!!.lowercase().contains("An I/O error occurred while sending to the backend")
    }

    private fun isRecoveryConnectionException(e: Throwable?): Boolean {
        return e is SQLException &&
            e.message!!.lowercase().contains("due to conflict with recovery")
    }

    private fun isUnknownColumnInFieldListException(e: Throwable?): Boolean {
        return (e is SQLSyntaxErrorException &&
            e.message!!.lowercase().contains("unknown column") &&
            e.message!!.lowercase().contains("in 'field list'"))
    }
}
