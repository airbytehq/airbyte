/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.typing_deduping.direct_load_tables

import com.google.cloud.bigquery.BigQuery
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableStatus
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.integrations.destination.bigquery.write.typing_deduping.toTableId
import java.math.BigInteger
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch

class BigqueryDirectLoadDatabaseInitialStateGatherer(private val bigquery: BigQuery) :
    DatabaseInitialStatusGatherer<DirectLoadInitialStatus> {
    override suspend fun gatherInitialStatus(
        streams: TableCatalog,
    ): Map<DestinationStream, DirectLoadInitialStatus> {
        val map = ConcurrentHashMap<DestinationStream, DirectLoadInitialStatus>()
        coroutineScope {
            streams.forEach { (stream, tableNameInfo) ->
                launch {
                    val tableName = tableNameInfo.tableNames.finalTableName!!
                    map[stream] =
                        DirectLoadInitialStatus(
                            realTable = getTableStatus(tableName),
                            tempTable = getTableStatus(tableName.asTempTable()),
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
