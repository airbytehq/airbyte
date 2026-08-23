/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.typing_deduping.direct_load_tables

import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryError
import com.google.cloud.bigquery.BigQueryException
import com.google.cloud.bigquery.Table
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.ColumnNameMapping
import io.airbyte.cdk.load.orchestration.db.DefaultTempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TableNames
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableStatus
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableNameInfo
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables.BigqueryDirectLoadDatabaseInitialStatusGatherer
import io.mockk.every
import io.mockk.mockk
import java.math.BigInteger
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class BigqueryDirectLoadDatabaseInitialStatusGathererTest {
    private val realTableName = TableName("namespace", "table")

    @Test
    fun `403 access denied is wrapped as ConfigErrorException`() {
        assertConvertedToConfigError(403, "Access Denied: permission denied")
    }

    @Test
    fun `401 unauthorized is wrapped as ConfigErrorException`() {
        assertConvertedToConfigError(401, "Unauthorized")
    }

    @Test
    fun `403 rate limit is not wrapped as ConfigErrorException`() {
        assertNotConverted(403, "Rate limit exceeded", "rateLimitExceeded")
    }

    @Test
    fun `500 internal error is not wrapped as ConfigErrorException`() {
        assertNotConverted(500, "Internal error", "internalError")
    }

    @Test
    fun `existing and empty tables return their statuses`() = runBlocking {
        val bigquery = mockk<BigQuery>()
        val existingTable = mockk<Table> { every { numRows } returns BigInteger.ONE }
        val emptyTable = mockk<Table> { every { numRows } returns BigInteger.ZERO }
        every { bigquery.getTable(any()) } returnsMany listOf(existingTable, emptyTable)

        val result = gatherer(bigquery).gatherInitialStatus(catalog())

        assertEquals(
            DirectLoadInitialStatus(
                realTable = DirectLoadTableStatus(isEmpty = false),
                tempTable = DirectLoadTableStatus(isEmpty = true),
            ),
            result.values.single(),
        )
    }

    @Test
    fun `absent tables return null statuses`() = runBlocking {
        val bigquery = mockk<BigQuery>()
        every { bigquery.getTable(any()) } returns null

        val result = gatherer(bigquery).gatherInitialStatus(catalog())

        assertNull(result.values.single().realTable)
        assertNull(result.values.single().tempTable)
    }

    private fun assertConvertedToConfigError(code: Int, message: String) {
        val exception = bigQueryException(code, message, "accessDenied")
        val bigquery = mockk<BigQuery> { every { getTable(any()) } throws exception }

        assertThrows<ConfigErrorException> {
            runBlocking { gatherer(bigquery).gatherInitialStatus(catalog()) }
        }
    }

    private fun assertNotConverted(code: Int, message: String, reason: String) {
        val exception = bigQueryException(code, message, reason)
        val bigquery = mockk<BigQuery> { every { getTable(any()) } throws exception }

        assertThrows<BigQueryException> {
            runBlocking { gatherer(bigquery).gatherInitialStatus(catalog()) }
        }
    }

    private fun bigQueryException(code: Int, message: String, reason: String) =
        BigQueryException(code, message, BigQueryError(reason, "location", message))

    private fun gatherer(bigquery: BigQuery) =
        BigqueryDirectLoadDatabaseInitialStatusGatherer(
            bigquery,
            DefaultTempTableNameGenerator("unused"),
        )

    private fun catalog(): TableCatalog {
        val stream = mockk<DestinationStream>()
        return TableCatalog(
            mapOf(
                stream to
                    TableNameInfo(
                        tableNames =
                            TableNames(
                                rawTableName = null,
                                finalTableName = realTableName,
                            ),
                        columnNameMapping = ColumnNameMapping(emptyMap()),
                    )
            )
        )
    }
}
