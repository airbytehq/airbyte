/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.table.ColumnNameMapping
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class TableOperationsClientTest {

    /** Minimal client that only reports a fixed row count, exercising the default methods. */
    private class CountOnlyClient(private val count: Long?) : TableOperationsClient {
        override suspend fun countTable(tableName: TableName): Long? = count

        override suspend fun createTable(
            stream: DestinationStream,
            tableName: TableName,
            columnNameMapping: ColumnNameMapping,
            replace: Boolean,
        ) = Unit
        override suspend fun dropTable(tableName: TableName) = Unit
        override suspend fun overwriteTable(
            sourceTableName: TableName,
            targetTableName: TableName,
        ) = Unit
        override suspend fun copyTable(
            columnNameMapping: ColumnNameMapping,
            sourceTableName: TableName,
            targetTableName: TableName,
        ) = Unit
        override suspend fun upsertTable(
            stream: DestinationStream,
            columnNameMapping: ColumnNameMapping,
            sourceTableName: TableName,
            targetTableName: TableName,
        ) = Unit
    }

    private val tableName = TableName("namespace", "name")

    @Test
    fun `default tableIsEmpty is true when count is zero`() = runTest {
        assertTrue(CountOnlyClient(0L).tableIsEmpty(tableName))
    }

    @Test
    fun `default tableIsEmpty is false when count is positive`() = runTest {
        assertFalse(CountOnlyClient(5L).tableIsEmpty(tableName))
    }

    @Test
    fun `default tableIsEmpty is false when count is null`() = runTest {
        assertFalse(CountOnlyClient(null).tableIsEmpty(tableName))
    }
}
