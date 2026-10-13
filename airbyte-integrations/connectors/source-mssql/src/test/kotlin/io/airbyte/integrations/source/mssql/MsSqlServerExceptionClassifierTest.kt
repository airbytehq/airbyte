/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.TransientError
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.sql.SQLException
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class MsSqlServerExceptionClassifierTest {
    @Inject lateinit var handler: ExceptionHandler

    @Test
    fun testConnectTimedOut() {
        assertTransientError(connectTimedOutException(), "SQL Server Connection Error", JDBC_LINK)
    }

    @Test
    fun testUnknownHost() {
        val exception =
            RuntimeException(
                "The TCP/IP connection to the host nosuchhost.invalid, port 1433 has failed. " +
                    "Error: \"nosuchhost.invalid. Verify the connection properties. Make sure that an instance of SQL Server is " +
                    "running on the host and accepting TCP/IP connections at the port. Make sure that TCP connections to the port are not blocked by a firewall.\"."
            )

        assertTransientError(exception, "SQL Server Connection Error", JDBC_LINK)
    }

    @Test
    fun testWrappedConnectionFailureDuringCheck() {
        val exception = RuntimeException("Failed to connect", connectTimedOutException())

        val (first, second) = handler.handleCheckFailure(exception)

        Assertions.assertEquals(
            AirbyteErrorTraceMessage.FailureType.CONFIG_ERROR,
            first.failureType
        )
        Assertions.assertTrue(second.message.contains("could not reach", ignoreCase = true))
        Assertions.assertFalse(second.message.contains("will retry", ignoreCase = true))
    }

    @Test
    fun testSqlServerNetworkErrorCode() {
        val exception =
            SQLException(
                "A network-related or instance-specific error occurred while establishing a connection to SQL Server.",
                "08S01",
                2
            )

        assertTransientError(exception, "SQL Server Network Error", SQL_SERVER_NETWORK_LINK)
    }

    private fun assertTransientError(exception: Throwable, group: String, referenceLink: String) {
        val expected =
            TransientError("$group: $UNREACHABLE_HOST_MESSAGE\n$IP_ADDRESSES_LINK\n$referenceLink")
        val result = handler.classify(exception)

        Assertions.assertEquals(expected, result)
        Assertions.assertFalse(
            (result as TransientError).displayMessage.contains("will retry", ignoreCase = true)
        )
    }

    private fun connectTimedOutException(): RuntimeException =
        RuntimeException(
            "The TCP/IP connection to the host sqlserver.example.com, port 1433 has failed. " +
                "Error: \"Connect timed out. Verify the connection properties. Make sure that an instance of SQL Server is " +
                "running on the host and accepting TCP/IP connections at the port. Make sure that TCP connections to the port are not blocked by a firewall.\"."
        )

    private companion object {
        const val UNREACHABLE_HOST_MESSAGE =
            "Airbyte could not reach the SQL Server host and port provided. Check that the host and port are correct, " +
                "that the SQL Server instance accepts remote TCP/IP connections, and that your firewall or security group " +
                "allows inbound connections from Airbyte's IP addresses."
        const val IP_ADDRESSES_LINK =
            "https://docs.airbyte.com/platform/operating-airbyte/security#ip-addresses"
        const val JDBC_LINK =
            "https://docs.microsoft.com/en-us/sql/connect/jdbc/troubleshooting-connectivity"
        const val SQL_SERVER_NETWORK_LINK =
            "https://docs.microsoft.com/en-us/sql/relational-databases/errors-events/mssqlserver-2-database-engine-error"
    }
}
