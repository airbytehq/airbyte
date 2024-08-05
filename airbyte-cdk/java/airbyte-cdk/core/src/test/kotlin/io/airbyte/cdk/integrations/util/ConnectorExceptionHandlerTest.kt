/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.util

import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.exceptions.ConnectionErrorException
import io.airbyte.commons.exceptions.TransientErrorException
import java.sql.SQLException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class ConnectorExceptionHandlerTest {

    val exceptionHandler = ConnectorExceptionHandler()

    @Test
    fun `test getExternalMessage() with ConfigErrorException`() {
        val configError = ConfigErrorException(CONFIG_EXCEPTION_MESSAGE)
        val actualMessage = exceptionHandler.getExternalMessage(configError)
        assertEquals(CONFIG_EXCEPTION_MESSAGE, actualMessage)
    }

    @Test
    fun `test getExternalMessage() with TransientErrorException`() {
        val configError = TransientErrorException(TRANSIENT_EXCEPTION_MESSAGE)
        val actualMessage = exceptionHandler.getExternalMessage(configError)
        assertEquals(TRANSIENT_EXCEPTION_MESSAGE, actualMessage)
    }

    @Test
    fun `test getExternalMessage() with ConnectionErrorException`() {
        val testCode = "test code"
        val errorCode = -1
        val connectionErrorException =
            ConnectionErrorException(testCode, errorCode, CONFIG_EXCEPTION_MESSAGE, Exception())
        val actualDisplayMessage = exceptionHandler.getExternalMessage(connectionErrorException)
        assertEquals(
            String.format(
                CONNECTION_ERROR_MESSAGE_TEMPLATE,
                testCode,
                errorCode,
                CONFIG_EXCEPTION_MESSAGE
            ),
            actualDisplayMessage
        )
    }

    @Test
    fun `test getExternalMessage() with SQL Exceptions`() {
        // the following exceptions being tested are DB source specific, therefore,
        // we expect a common error gets returned by the default implementation
        val recoveryException = SQLException(RECOVERY_EXCEPTION_MESSAGE)
        val actualDisplayMessage = exceptionHandler.getExternalMessage(recoveryException)
        val expectedMessage =
            String.format(COMMON_EXCEPTION_MESSAGE_TEMPLATE, recoveryException.message)
        assertEquals(expectedMessage, actualDisplayMessage)
    }

    @Test
    fun `test getRootException() with ConfigErrorException being root exception`() {
        // creates a nested exception rooted by a config error exception
        val configErrorException = ConfigErrorException(CONFIG_EXCEPTION_MESSAGE)
        val nestedException = Exception(COMMON_EXCEPTION_MESSAGE, configErrorException)
        val result = exceptionHandler.getRootException(nestedException)
        assertEquals(configErrorException, result)
    }

    @Test
    fun `test getRootException() with TransientErrorException being root exception`() {
        // creates a nested exception rooted by a config error exception
        val transientErrorException = TransientErrorException(TRANSIENT_EXCEPTION_MESSAGE)
        val nestedException = Exception(COMMON_EXCEPTION_MESSAGE, transientErrorException)
        val result = exceptionHandler.getRootException(nestedException)
        assertEquals(transientErrorException, result)
    }

    @Test
    fun `test getRootException() with three nested exception`() {
        // creates a nested exception rooted by a config error exception
        val transientErrorException = TransientErrorException(TRANSIENT_EXCEPTION_MESSAGE)
        val nestedException = Exception(COMMON_EXCEPTION_MESSAGE, transientErrorException)
        val e = Exception(COMMON_EXCEPTION_MESSAGE, nestedException)
        val result = exceptionHandler.getRootException(e)
        assertEquals(transientErrorException, result)
    }

    @Test
    fun `test getRootException() with nested but unrecognizable exception`() {
        // creates a nested exception rooted by a config error exception
        val e1 = Exception(COMMON_EXCEPTION_MESSAGE)
        val e2 = Exception(COMMON_EXCEPTION_MESSAGE, e1)
        val e3 = Exception(COMMON_EXCEPTION_MESSAGE, e2)
        val result = exceptionHandler.getRootException(e3)
        assertEquals(e3, result)
    }

    @Test
    fun `test checkErrorType() with ConfigErrorException`() {
        val configError = ConfigErrorException(CONFIG_EXCEPTION_MESSAGE)
        val actualResult = exceptionHandler.checkErrorType(configError, FailureType.CONFIG)
        assertEquals(true, actualResult)
    }

    @Test
    fun `test checkErrorType() with TransientErrorException`() {
        val transientError = TransientErrorException(TRANSIENT_EXCEPTION_MESSAGE)
        val actualResult = exceptionHandler.checkErrorType(transientError, FailureType.TRANSIENT)
        assertEquals(true, actualResult)
    }

    companion object {
        const val CONFIG_EXCEPTION_MESSAGE: String = "test config error message"
        const val TRANSIENT_EXCEPTION_MESSAGE: String = "test transient error message"
        const val RECOVERY_EXCEPTION_MESSAGE: String =
            "FATAL: terminating connection due to conflict with recovery"
        const val COMMON_EXCEPTION_MESSAGE: String = "something happens with connection"
        const val CONNECTION_ERROR_MESSAGE_TEMPLATE: String =
            "State code: %s; Error code: %s; Message: %s"
        const val COMMON_EXCEPTION_MESSAGE_TEMPLATE: String =
            "Could not connect with provided configuration. Error: %s"
    }
}
