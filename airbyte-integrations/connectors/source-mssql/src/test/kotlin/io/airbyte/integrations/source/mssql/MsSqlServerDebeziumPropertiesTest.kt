/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.ssh.TunnelSession
import io.mockk.every
import io.mockk.mockk
import java.net.InetSocketAddress
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class MsSqlServerDebeziumPropertiesTest {
    @Test
    fun coldStartPropertiesUseFunctionDataQueryModeAndMaxIterationTransactions500() {
        val props = debeziumOperations().generateColdStartProperties(emptyList())
        Assertions.assertEquals("function", props["data.query.mode"])
        Assertions.assertEquals("500", props["max.iteration.transactions"])
        // cold start
        Assertions.assertEquals("recovery", props["snapshot.mode"])
    }

    @Test
    fun warmStartPropertiesUseFunctionDataQueryModeAndMaxIterationTransactions500() {
        val props = debeziumOperations().generateWarmStartProperties(emptyList())
        Assertions.assertEquals("function", props["data.query.mode"])
        Assertions.assertEquals("500", props["max.iteration.transactions"])
        // warm start
        Assertions.assertEquals("when_needed", props["snapshot.mode"])
    }

    @Test
    fun userSetMaxIterationTransactionsIsPassedToDebezium() {
        val cdc = Cdc().also { it.maxIterationTransactions = 0 }
        val props = debeziumOperations(cdc).generateWarmStartProperties(emptyList())
        Assertions.assertEquals("0", props["max.iteration.transactions"])
    }

    @Test
    fun negativeMaxIterationTransactionsIsRejected() {
        val cdc = Cdc().also { it.maxIterationTransactions = -1 }
        val negativeEx =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                MsSqlServerSourceConfigurationFactory().makeWithoutExceptionHandling(cdcPojo(cdc))
            }
        Assertions.assertTrue(
            negativeEx.message?.contains("must be 0 (unbounded) or a positive number") == true,
            "Unexpected error message: ${negativeEx.message}",
        )
    }

    private fun cdcPojo(cdc: Cdc = Cdc()): MsSqlServerSourceConfigurationSpecification =
        MsSqlServerSourceConfigurationSpecification().also {
            it.host = "localhost"
            it.port = 1433
            it.database = "testdb"
            it.username = "sa"
            it.password = "Password123!"
            it.encryptionJson =
                MsSqlServerEncryptionRequiredTrustServerCertificateConfigurationSpecification
            it.replicationMethodJson = cdc
        }

    private fun debeziumOperations(cdc: Cdc = Cdc()): MsSqlServerDebeziumOperations {
        val configuration = MsSqlServerSourceConfigurationFactory().make(cdcPojo(cdc))

        val tunnelSession = mockk<TunnelSession>()
        every { tunnelSession.address } returns InetSocketAddress("localhost", 1433)
        val jdbcConnectionFactory = mockk<JdbcConnectionFactory>()
        every { jdbcConnectionFactory.ensureTunnelSession() } returns tunnelSession

        return MsSqlServerDebeziumOperations(jdbcConnectionFactory, configuration)
    }
}
