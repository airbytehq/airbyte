/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping.direct_load_tables

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.Table
import com.google.cloud.bigquery.TableId
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableNameInfo
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadDatabaseInitialStatusGatherer
import io.mockk.every
import io.mockk.mockk
import java.math.BigInteger
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class BigqueryDirectLoadDatabaseInitialStatusGathererTest {

    private val bigquery: BigQuery = mockk()
    private val tempTableNameGenerator: TempTableNameGenerator = mockk()

    private val gatherer =
        BigqueryDirectLoadDatabaseInitialStatusGatherer(bigquery, tempTableNameGenerator)

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

    private val tableName = TableName("test_namespace", "test_stream")
    private val tempTableName = TableName("test_namespace", "test_stream_tmp")

    @Test
    fun `InterruptedException during getTable is wrapped as TransientErrorException`() =
        runBlocking {
            val interruptedException = InterruptedException("thread interrupted")
            val bigQueryException = BigQueryException(0, "interrupted", interruptedException)

            every { bigquery.getTable(any<TableId>()) } throws bigQueryException
            every { tempTableNameGenerator.generate(any()) } returns tempTableName

            val tableNames = TableNames(finalTableName = tableName, rawTableName = null)
            val catalog =
                TableCatalog(
                    mapOf(stream to TableNameInfo(tableNames, ColumnNameMapping(emptyMap())))
                )

            assertThrows<TransientErrorException> { gatherer.gatherInitialStatus(catalog) }

            // Clear interrupted status
            Thread.interrupted()
        }

    @Test
    fun `successful getTable returns status normally`() = runBlocking {
        val table: Table = mockk()
        every { table.numRows } returns BigInteger.ZERO

        every { bigquery.getTable(any<TableId>()) } returns table
        every { tempTableNameGenerator.generate(any()) } returns tempTableName

        val tableNames = TableNames(finalTableName = tableName, rawTableName = null)
        val catalog =
            TableCatalog(mapOf(stream to TableNameInfo(tableNames, ColumnNameMapping(emptyMap()))))

        val result = gatherer.gatherInitialStatus(catalog)
        assertNotNull(result[stream])
    }

    @Test
    fun `non-InterruptedException BigQueryException is rethrown as-is`() = runBlocking {
        val bigQueryException = BigQueryException(403, "permission denied")

        every { bigquery.getTable(any<TableId>()) } throws bigQueryException
        every { tempTableNameGenerator.generate(any()) } returns tempTableName

        val tableNames = TableNames(finalTableName = tableName, rawTableName = null)
        val catalog =
            TableCatalog(mapOf(stream to TableNameInfo(tableNames, ColumnNameMapping(emptyMap()))))

        assertThrows<BigQueryException> { gatherer.gatherInitialStatus(catalog) }
    }
}
