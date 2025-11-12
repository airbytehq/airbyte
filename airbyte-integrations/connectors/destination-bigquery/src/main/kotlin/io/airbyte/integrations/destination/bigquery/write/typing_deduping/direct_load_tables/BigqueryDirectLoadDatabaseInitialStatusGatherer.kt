/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables

import com.google.cloud.bigquery.BigQuery
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableStatus
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.cdk.load.table.TableName
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.toTableId
import java.math.BigInteger
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch

@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "kotlin coroutines")
class BigqueryDirectLoadDatabaseInitialStatusGatherer(
    private val bigquery: BigQuery,
    private val tempTableNameGenerator: TempTableNameGenerator,
) : DatabaseInitialStatusGatherer<DirectLoadInitialStatus> {
    override suspend fun gatherInitialStatus(
        streams: TableCatalog,
    ): Map<DestinationStream, DirectLoadInitialStatus> {
        val map = ConcurrentHashMap<DestinationStream, DirectLoadInitialStatus>(streams.size)
        coroutineScope {
            streams.forEach { (stream, tableNameInfo) ->
                launch {
                    val tableName = tableNameInfo.tableNames.finalTableName!!
                    map[stream] =
                        DirectLoadInitialStatus(
                            realTable = getTableStatus(tableName),
                            tempTable = getTableStatus(tempTableNameGenerator.generate(tableName)),
                        )
                }
            }
        }
        return map
    }

    private fun getTableStatus(tableName: TableName): DirectLoadTableStatus? {
        val table = bigquery.getTable(tableName.toTableId())
        return table?.let { DirectLoadTableStatus(isEmpty = table.numRows == BigInteger.ZERO) }
    }
}
