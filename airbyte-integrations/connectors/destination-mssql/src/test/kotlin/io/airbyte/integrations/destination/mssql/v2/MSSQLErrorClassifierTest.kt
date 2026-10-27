/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql.v2

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.mssql.v2.config.MSSQLConfiguration
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import java.sql.BatchUpdateException
import java.sql.Connection
import java.sql.PreparedStatement
import java.sql.SQLException
import javax.sql.DataSource
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Test

class MSSQLErrorClassifierTest {

    @Test
    fun `size quota error code is a config error`() {
        assertConfigError(
            SQLException("", "S0001", 40544),
            "The destination database has reached its maximum size. Increase the database's max size or service tier, or free up space, then retry the sync.",
        )
    }

    @Test
    fun `size quota message is a config error without a matching code`() {
        assertConfigError(
            SQLException("The database 'example' HAS REACHED ITS SIZE QUOTA.", "S0001", 0),
            "The destination database has reached its maximum size. Increase the database's max size or service tier, or free up space, then retry the sync.",
        )
    }

    @Test
    fun `filegroup full error code is a config error`() {
        assertConfigError(
            SQLException("", "S0001", 1105),
            "The destination database filegroup is full. Add space or files, enable autogrowth, or free disk space, then retry the sync.",
        )
    }

    @Test
    fun `filegroup full message is a config error without a matching code`() {
        assertConfigError(
            SQLException(
                "Could not allocate space for object 'dbo.example' in database 'example' because the 'PRIMARY' filegroup is full.",
                "S0001",
                0,
            ),
            "The destination database filegroup is full. Add space or files, enable autogrowth, or free disk space, then retry the sync.",
        )
    }

    @Test
    fun `log full and empty SQL errors are rethrown unchanged`() {
        listOf(
                SQLException("The transaction log for database 'example' is full.", "S0001", 9002),
                SQLException(),
            )
            .forEach { original ->
                val exception =
                    assertThrows(SQLException::class.java) {
                        MSSQLErrorClassifier.rethrowClassified(original)
                    }
                assertSame(original, exception)
            }
    }

    private fun assertConfigError(original: SQLException, message: String) {
        val exception =
            assertThrows(ConfigErrorException::class.java) {
                MSSQLErrorClassifier.rethrowClassified(original)
            }
        assertEquals(message, exception.message)
        assertSame(original, exception.cause)
    }

    @Test
    fun `permission denied error is a config error`() {
        val original =
            BatchUpdateException(
                "The INSERT permission was denied on the object 'unit_info', database 'data', schema 'gcpexport'.",
                "42000",
                229,
                intArrayOf(),
            )

        val exception =
            assertThrows(ConfigErrorException::class.java) {
                MSSQLErrorClassifier.rethrowClassified(original)
            }

        assertSame(original, exception.cause)
    }

    @Test
    fun `permission denied message is a config error without a matching code`() {
        val exception =
            assertThrows(ConfigErrorException::class.java) {
                MSSQLErrorClassifier.rethrowClassified(
                    SQLException(
                        "The INSERT permission was denied on the object 'unit_info'.",
                        "42000",
                        0,
                    ),
                )
            }

        assertEquals("Database user lacks permission on the destination table.", exception.message)
    }

    @Test
    fun `string truncation error is a config error`() {
        val exception =
            assertThrows(ConfigErrorException::class.java) {
                MSSQLErrorClassifier.rethrowClassified(
                    BatchUpdateException(
                        "String or binary data would be truncated in table 'x', column 'y'.",
                        "22001",
                        2628,
                        intArrayOf(),
                    ),
                )
            }

        assertEquals(
            "Record value exceeds the length of a destination table column.",
            exception.message,
        )
    }

    @Test
    fun `wrapped permission denied error is a config error`() {
        val original =
            BatchUpdateException("batch failed", null, 0, intArrayOf()).also {
                it.initCause(SQLException("The INSERT permission was denied.", "42000", 229))
            }

        val exception =
            assertThrows(ConfigErrorException::class.java) {
                MSSQLErrorClassifier.rethrowClassified(original)
            }

        assertSame(original, exception.cause)
    }

    @Test
    fun `wrapped permission denied message is a config error without matching codes`() {
        val original =
            SQLException("batch failed").also {
                it.initCause(SQLException("The INSERT permission was denied on the object 'x'."))
            }

        val exception =
            assertThrows(ConfigErrorException::class.java) {
                MSSQLErrorClassifier.rethrowClassified(original)
            }

        assertSame(original, exception.cause)
    }

    @Test
    fun `unrelated SQL error is rethrown unchanged`() {
        val original = SQLException("Transaction was deadlocked", "40001", 1205)

        val exception =
            assertThrows(SQLException::class.java) {
                MSSQLErrorClassifier.rethrowClassified(original)
            }

        assertSame(original, exception)
    }

    @Test
    fun `direct loader classifies permission denied batch errors`() {
        val descriptor = DestinationStream.Descriptor("dbo", "unit_info")
        val dataSource = mockk<DataSource>()
        val connection = mockk<Connection>(relaxed = true)
        val preparedStatement = mockk<PreparedStatement>(relaxed = true)
        val sqlBuilder = mockk<MSSQLQueryBuilder>(relaxed = true)
        val stateStore = StreamStateStore<MSSQLStreamState>()
        val config =
            mockk<MSSQLConfiguration>(relaxed = true) {
                every { batchEveryNRecords } returns 1
                every { maxBatchSizeBytes } returns Long.MAX_VALUE
            }
        val parent = mockk<MSSQLDirectLoaderFactory>(relaxed = true)

        every { dataSource.connection } returns connection
        every { connection.autoCommit = any() } just runs
        every { connection.prepareStatement(any()) } returns preparedStatement
        every { preparedStatement.executeBatch() } throws
            BatchUpdateException("The INSERT permission was denied.", "42000", 229, intArrayOf())
        stateStore.put(descriptor, MSSQLDirectLoaderStreamState(dataSource, sqlBuilder))

        val loader = MSSQLDirectLoader(config, stateStore, descriptor, 0, parent)

        assertThrows(ConfigErrorException::class.java) {
            runBlocking { loader.accept(mockk<DestinationRecordRaw>(relaxed = true)) }
        }
    }
}
