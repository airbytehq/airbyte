/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.write.load

import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.integrations.destination.postgres.client.PostgresAirbyteClient
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import io.mockk.coEvery
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

internal class PostgresInsertBufferTest {

    private lateinit var postgresClient: PostgresAirbyteClient
    private lateinit var postgresConfiguration: PostgresConfiguration

    @BeforeEach
    fun setup() {
        postgresClient = mockk()
        postgresConfiguration = mockk()
        every { postgresConfiguration.legacyRawTablesOnly } returns false
    }

    @Test
    fun `flush propagates exception when COPY fails`() {
        val tableName = TableName("test_ns", "test_table")
        val columns = listOf("col1")
        val buffer =
            PostgresInsertBuffer(tableName, columns, postgresClient, postgresConfiguration)

        // Accumulate a record so csvFilePath is set
        buffer.accumulate(mapOf("col1" to StringValue("value")))
        assertNotNull(buffer.csvFilePath)

        // Make copyFromCsv throw an exception (simulating a COPY failure)
        coEvery { postgresClient.copyFromCsv(any(), any()) } throws
            RuntimeException("unsupported Unicode escape sequence")

        // flush() should propagate the exception instead of swallowing it
        assertThrows<RuntimeException> { runBlocking { buffer.flush() } }
    }

    @Test
    fun `flush cleans up resources even when exception is thrown`() {
        val tableName = TableName("test_ns", "test_table")
        val columns = listOf("col1")
        val buffer =
            PostgresInsertBuffer(tableName, columns, postgresClient, postgresConfiguration)

        buffer.accumulate(mapOf("col1" to StringValue("value")))
        assertNotNull(buffer.csvFilePath)

        coEvery { postgresClient.copyFromCsv(any(), any()) } throws
            RuntimeException("COPY failed")

        // Verify exception is thrown
        assertThrows<RuntimeException> { runBlocking { buffer.flush() } }

        // Verify resources are cleaned up despite the exception
        org.junit.jupiter.api.Assertions.assertNull(buffer.csvFilePath)
        org.junit.jupiter.api.Assertions.assertEquals(0, buffer.recordCount)
    }
}
