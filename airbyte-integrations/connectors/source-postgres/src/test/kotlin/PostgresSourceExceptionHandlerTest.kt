/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.integrations.util.FailureType
import io.airbyte.integrations.source.postgres.PostgresSourceExceptionHandler
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.postgresql.util.PSQLException

class PostgresSourceExceptionHandlerTest {
    private var exceptionHandler: PostgresSourceExceptionHandler? = null

    @BeforeEach
    fun setUp() {
        exceptionHandler = PostgresSourceExceptionHandler()
    }

    @Test
    fun testTranslateTemporaryFileSizeExceedsLimitException() {
        val exception =
            PSQLException("ERROR: temporary file size exceeds temp_file_limit (500kB)", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals(
            "Encountered an error while reading the database, will retry.",
            externalMessage
        )
    }

    @Test
    fun testIOException() {
        val exception = PSQLException("An I/O error occured while sending to the backend", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals(
            "Encountered an error while reading the database, will retry.",
            externalMessage
        )
    }

    @Test
    fun testPermissionException() {
        val exception = PSQLException("ERROR: permission denied for table", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.CONFIG))
        Assertions.assertEquals(
            "Database read failed due to missing read permissions on a table. " +
                "See the detailed error for the table name and update permissions accordingly.",
            externalMessage
        )
    }

    @Test
    fun testStatementTimeoutException() {
        val exception = PSQLException("canceling statement due to statement timeout", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals(
            "Database read failed due SQL statement timeout, will retry.",
            externalMessage
        )
    }

    @Test
    fun testHikariConnectionException() {
        val exception = PSQLException("connection is not available, request timed out after", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals(
            "Database read failed due to connection timeout, will retry.",
            externalMessage
        )
    }

    @Test
    fun testConnectionTimeoutException() {
        val exception = PSQLException("Timed out after 15000 msec", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals("Database connection timeout, will retry.", externalMessage)
    }

    @Test
    fun testSocketException() {
        val exception = PSQLException("java.net.SocketException: Socket is closed", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals(
            "Database connection error when performing CDC reads, will retry.",
            externalMessage
        )
    }

    @Test
    fun testBrokenPipeException() {
        val exception = PSQLException("java.net.SocketException: Broken pipe", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals(
            "Database connection error when performing CDC reads, will retry.",
            externalMessage
        )
    }

    @Test
    fun testReplicationSlotException() {
        val exception =
            PSQLException("ERROR: cannot read from logical replication slot \"airbyte_slot\"", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.CONFIG))
        Assertions.assertEquals(
            "The configured replication slot has been dropped or has corrupted. Please recreate the replication slot.",
            externalMessage
        )
    }

    @Test
    fun testConnectionClosedException() {
        val exception = PSQLException("This connection has been closed", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals(
            "The connection to the Postgres server was unexpectedly closed, will retry.",
            externalMessage
        )
    }

    @Test
    fun testConnectionClosedCaseInsensitiveException() {
        val exception = PSQLException("ERROR: THIS CONNECTION HAS BEEN CLOSED.", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals(
            "The connection to the Postgres server was unexpectedly closed, will retry.",
            externalMessage
        )
    }

    @Test
    fun testDebeziumConnectionException() {
        val exception = PSQLException("Connection or outbound has closed", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals(
            "The connection to the Postgres server was lost, will retry.",
            externalMessage
        )
    }

    @Test
    fun testRecoveryInProgressException() {
        val exception = PSQLException("recovery is in progress", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals(
            "Postgres server is currently in recovery mode, will retry.",
            externalMessage
        )
    }

    @Test
    fun testRecoveryConflictCancelationException() {
        val exception =
            PSQLException("ERROR: canceling statement due to conflict with recovery.", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals(
            "We're having issues syncing from a Postgres replica that is configured as a hot standby server. " +
                "Please see https://go.airbyte.com/pg-hot-standby-error-message for options and workarounds",
            externalMessage
        )
    }

    @Test
    fun testRecoveryConflictTerminationException() {
        val exception = PSQLException("terminating connection due to conflict with recovery", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals(
            "We're having issues syncing from a Postgres replica that is configured as a hot standby server. " +
                "Please see https://go.airbyte.com/pg-hot-standby-error-message for options and workarounds",
            externalMessage
        )
    }

    @Test
    fun testTransactionTimeoutException() {
        val exception =
            PSQLException("terminating connection due to idle-in-transaction timeout", null)
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.CONFIG))
        Assertions.assertEquals(
            "Postgres server closed the connection due to an idle-in-transaction timeout. Please review your server's timeout configuration " +
                "and increase the timeout if needed",
            externalMessage
        )
    }

    @Test
    fun testGeneralDebeziumException() {
        val exception =
            PSQLException(
                "An exception occurred in the change event producer. This connector will be stopped.",
                null
            )
        val externalMessage = exceptionHandler!!.getExternalMessage(exception)
        Assertions.assertTrue(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertEquals(
            "The sync encountered an unexpected error in the change event producer and has stopped. " +
                "Please check the logs for details and troubleshoot accordingly.",
            externalMessage
        )
    }

    // testing a case when we are throwing an error that is not part of our error handling.
    @Test
    fun testUnhandledFatalException() {
        val exception = PSQLException("FATAL: database does not exist", null)
        // This FATAL error shouldn't match any of your specific patterns
        Assertions.assertFalse(exceptionHandler!!.checkErrorType(exception, FailureType.TRANSIENT))
        Assertions.assertFalse(exceptionHandler!!.checkErrorType(exception, FailureType.CONFIG))
    }
}
