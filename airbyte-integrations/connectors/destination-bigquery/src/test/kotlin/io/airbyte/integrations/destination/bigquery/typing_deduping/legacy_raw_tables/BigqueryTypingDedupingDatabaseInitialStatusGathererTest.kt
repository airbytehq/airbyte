/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping.legacy_raw_tables

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.TableId
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableNameInfo
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.legacy_raw_tables.BigqueryTypingDedupingDatabaseInitialStatusGatherer
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class BigqueryTypingDedupingDatabaseInitialStatusGathererTest {

    private val bq: BigQuery = mockk()

    private val gatherer = BigqueryTypingDedupingDatabaseInitialStatusGatherer(bq)

    private val stream =
        DestinationStream(
            "test_namespace",
            "test_stream",
            Append,
            ObjectType(linkedMapOf()),
            generationId = 0,
            minimumGenerationId = 0,
            syncId = 0,
            namespaceMapper = NamespaceMapper(),
        )

    private val rawTableName = TableName("test_namespace", "test_stream_raw")
    private val finalTableName = TableName("test_namespace", "test_stream")

    @Test
    fun `InterruptedException during getTable is wrapped as TransientErrorException`() =
        runBlocking {
            val interruptedException = InterruptedException("thread interrupted")
            val bigQueryException = BigQueryException(0, "interrupted", interruptedException)

            every { bq.getTable(any<TableId>()) } throws bigQueryException

            val tableNames =
                TableNames(rawTableName = rawTableName, finalTableName = finalTableName)
            val catalog =
                TableCatalog(
                    mapOf(stream to TableNameInfo(tableNames, ColumnNameMapping(emptyMap())))
                )

            assertThrows<TransientErrorException> { gatherer.gatherInitialStatus(catalog) }

            // Clear interrupted status
            Thread.interrupted()
        }

    @Test
    fun `table not found returns status with null raw table state`() = runBlocking {
        every { bq.getTable(any<TableId>()) } returns null

        val tableNames = TableNames(rawTableName = rawTableName, finalTableName = finalTableName)
        val catalog =
            TableCatalog(mapOf(stream to TableNameInfo(tableNames, ColumnNameMapping(emptyMap()))))

        val result = gatherer.gatherInitialStatus(catalog)
        assertNotNull(result[stream])
        assertNull(result[stream]!!.rawTableStatus)
    }

    @Test
    fun `non-InterruptedException BigQueryException is rethrown as-is`() = runBlocking {
        val bigQueryException = BigQueryException(403, "permission denied")

        every { bq.getTable(any<TableId>()) } throws bigQueryException

        val tableNames = TableNames(rawTableName = rawTableName, finalTableName = finalTableName)
        val catalog =
            TableCatalog(mapOf(stream to TableNameInfo(tableNames, ColumnNameMapping(emptyMap()))))

        assertThrows<BigQueryException> { gatherer.gatherInitialStatus(catalog) }
    }
}
