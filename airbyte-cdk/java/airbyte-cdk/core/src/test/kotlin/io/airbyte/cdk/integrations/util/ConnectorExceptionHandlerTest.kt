package io.airbyte.cdk.integrations.util



import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.exceptions.ConnectionErrorException
import io.airbyte.commons.exceptions.TransientErrorException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import java.sql.SQLException

internal class ConnectorExceptionHandlerTest {

    // Concrete subclass for testing
    private class TestConnectorExceptionHandler : ConnectorExceptionHandler() {
    }

    @Test
    fun `test getExternalMessage() with ConfigErrorException`() {
        val exceptionHandler = TestConnectorExceptionHandler()
        val configError = ConfigErrorException(CONFIG_EXCEPTION_MESSAGE)
        val actualMessage = exceptionHandler.getExternalMessage(configError)
        assertEquals(CONFIG_EXCEPTION_MESSAGE, actualMessage)
    }

    @Test
    fun `test getExternalMessage() with TransientErrorException`() {
        val exceptionHandler = TestConnectorExceptionHandler()
        val configError = TransientErrorException(TRANSIENT_EXCEPTION_MESSAGE)
        val actualMessage = exceptionHandler.getExternalMessage(configError)
        assertEquals(TRANSIENT_EXCEPTION_MESSAGE, actualMessage)
    }

    @Test
    fun `test getExternalMessage() with ConnectionErrorException`() {
        val exceptionHandler = TestConnectorExceptionHandler()
        val testCode = "test code"
        val errorCode = -1
        val connectionErrorException =
            ConnectionErrorException(testCode, errorCode, CONFIG_EXCEPTION_MESSAGE, Exception())
        val actualDisplayMessage =
            exceptionHandler.getExternalMessage(connectionErrorException)
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
        val exceptionHandler = TestConnectorExceptionHandler()
        val recoveryException = SQLException(RECOVERY_EXCEPTION_MESSAGE)
        val actualDisplayMessage = exceptionHandler.getExternalMessage(recoveryException)
        val expectedMessage = String.format(COMMON_EXCEPTION_MESSAGE_TEMPLATE,  recoveryException.message)
        assertEquals(
            expectedMessage,
            actualDisplayMessage
        )
    }


    companion object {
        const val CONFIG_EXCEPTION_MESSAGE: String = "test message"
        const val TRANSIENT_EXCEPTION_MESSAGE: String = "test message"
        const val RECOVERY_EXCEPTION_MESSAGE: String =
            "FATAL: terminating connection due to conflict with recovery"
        const val COMMON_EXCEPTION_MESSAGE: String = "something happens with connection"
        const val CONNECTION_ERROR_MESSAGE_TEMPLATE: String =
            "State code: %s; Error code: %s; Message: %s"
    }
}
