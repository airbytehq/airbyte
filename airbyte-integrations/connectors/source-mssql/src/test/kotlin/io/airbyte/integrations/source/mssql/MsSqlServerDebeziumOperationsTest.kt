/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.util.Jsons
import io.mockk.every
import io.mockk.mockk
import java.sql.Connection
import java.sql.ResultSet
import java.sql.Statement
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

class MsSqlServerDebeziumOperationsTest {
    @ParameterizedTest
    @CsvSource("My Database, My_Database", "testdb, testdb")
    fun coldStartOffsetKeyUsesSanitizedServerAndRawDatabaseName(
        databaseName: String,
        expectedServer: String,
    ) {
        val configuration = mockk<MsSqlServerSourceConfiguration>()
        every { configuration.databaseName } returns databaseName
        val resultSet = mockk<ResultSet>(relaxed = true)
        every { resultSet.next() } returns true
        every { resultSet.getBytes("max_lsn") } returns byteArrayOf(0, 0, 0, 1, 0, 0, 0, 2, 0, 3)
        val statement = mockk<Statement>(relaxed = true)
        every { statement.executeQuery("SELECT sys.fn_cdc_get_max_lsn() AS max_lsn") } returns
            resultSet
        val connection = mockk<Connection>(relaxed = true)
        every { connection.createStatement() } returns statement
        val jdbcConnectionFactory = mockk<JdbcConnectionFactory>()
        every { jdbcConnectionFactory.get() } returns connection

        val offset =
            MsSqlServerDebeziumOperations(jdbcConnectionFactory, configuration)
                .generateColdStartOffset()

        val expectedKey =
            Jsons.readTree(
                """["$databaseName", {"server": "$expectedServer", "database": "$databaseName"}]""",
            )
        assertEquals(setOf(expectedKey), offset.wrapped.keys)
    }
}
