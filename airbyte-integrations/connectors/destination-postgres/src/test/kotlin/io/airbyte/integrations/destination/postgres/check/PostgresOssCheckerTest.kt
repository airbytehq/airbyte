/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.check

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

internal class PostgresOssCheckerTest {
    private lateinit var checker: PostgresOssChecker
    private lateinit var postgresAirbyteClient: PostgresAirbyteClient
    private lateinit var postgresConfiguration: PostgresConfiguration

    @BeforeEach
    fun setup() {
        postgresAirbyteClient = mockk(relaxed = true)
        postgresConfiguration = mockk()
        checker = PostgresOssChecker(postgresAirbyteClient, postgresConfiguration)
    }

    @Test
    fun testCheckSucceeds() {
        val schema = "test_schema"
        every { postgresConfiguration.schema } returns schema
        every { postgresConfiguration.legacyRawTablesOnly } returns false

        coEvery { postgresAirbyteClient.createNamespace(any()) } returns Unit
        coEvery { postgresAirbyteClient.createTable(any(), any(), any(), any()) } returns Unit
        coEvery { postgresAirbyteClient.describeTable(any()) } returns listOf(CHECK_COLUMN_NAME)
        coEvery { postgresAirbyteClient.countTable(any()) } returns 1L
        coEvery { postgresAirbyteClient.dropTable(any()) } returns Unit

        // Should not throw any exception
        checker.check()

        coVerify(exactly = 1) { postgresAirbyteClient.createNamespace(schema) }
        coVerify(exactly = 1) {
            postgresAirbyteClient.createTable(
                stream = any<DestinationStream>(),
                tableName = any<TableName>(),
                columnNameMapping = any<ColumnNameMapping>(),
                replace = true
            )
        }
    }

    @Test
    fun testCheckFails() {
        val schema = "test_schema"
        every { postgresConfiguration.schema } returns schema
        every { postgresConfiguration.legacyRawTablesOnly } returns false

        coEvery { postgresAirbyteClient.createNamespace(any()) } returns Unit
        coEvery { postgresAirbyteClient.createTable(any(), any(), any(), any()) } returns Unit
        coEvery { postgresAirbyteClient.describeTable(any()) } returns listOf(CHECK_COLUMN_NAME)
        coEvery { postgresAirbyteClient.countTable(any()) } returns 0L
        coEvery { postgresAirbyteClient.dropTable(any()) } returns Unit

        val exception = assertThrows<IllegalArgumentException> { checker.check() }

        assertEquals(
            "Failed to insert expected rows into check table. Actual written: 0",
            exception.message
        )

        coVerify(exactly = 1) { postgresAirbyteClient.createNamespace(schema) }
        coVerify(exactly = 1) {
            postgresAirbyteClient.createTable(
                stream = any<DestinationStream>(),
                tableName = any<TableName>(),
                columnNameMapping = any<ColumnNameMapping>(),
                replace = true
            )
        }
        coVerify(exactly = 1) { postgresAirbyteClient.dropTable(any()) }
    }
}
