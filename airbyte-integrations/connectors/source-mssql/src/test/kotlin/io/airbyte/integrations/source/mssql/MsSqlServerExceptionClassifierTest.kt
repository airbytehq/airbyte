/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.output.ConfigError
import io.airbyte.cdk.output.ExceptionHandler
import io.airbyte.cdk.output.TransientError
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
    fun testPrivateNetworkConnectionFailure() {
        Assertions.assertEquals(
            ConfigError("SQL Server private network host is unreachable."),
            handler.classify(
                RuntimeException(
                    "The TCP/IP connection to the host 172.16.12.10, port 1433 has failed."
                )
            ),
        )
    }

    @Test
    fun testPublicNetworkConnectionFailure() {
        Assertions.assertEquals(
            TransientError("SQL Server host is unreachable."),
            handler.classify(
                RuntimeException(
                    "The TCP/IP connection to the host example.com, port 1433 has failed."
                )
            ),
        )
    }

    @Test
    fun testSqlServerNetworkErrorCode() {
        Assertions.assertEquals(
            TransientError("SQL Server host is unreachable."),
            handler.classify(SQLException("Network error", "08S01", 2)),
        )
    }
}
