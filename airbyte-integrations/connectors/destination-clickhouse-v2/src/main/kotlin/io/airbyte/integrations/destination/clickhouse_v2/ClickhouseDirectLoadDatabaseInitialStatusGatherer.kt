package io.airbyte.integrations.destination.clickhouse_v2

import com.clickhouse.client.api.Client
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableStatus
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import java.math.BigInteger
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch

class ClickhouseDirectLoadDatabaseInitialStatusGatherer(
    private val clickhouseClient: Client,
    private val internalTableDataset: String = "airbyte_internal",
) : DatabaseInitialStatusGatherer<DirectLoadInitialStatus> {
    override suspend fun gatherInitialStatus(streams: TableCatalog): Map<DestinationStream, DirectLoadInitialStatus> {
        val map = ConcurrentHashMap<DestinationStream, DirectLoadInitialStatus>(streams.size)
        coroutineScope {
            streams.forEach { (stream, tableNameInfo) ->
                launch {
                    val tableName = tableNameInfo.tableNames.finalTableName!!
                    map[stream] =
                        DirectLoadInitialStatus(
                            realTable = getTableStatus(tableName),
                            // TODO this feels sketchy. We maybe should compute the temp table name
                            //   in DirectLoadTableWriter, then pass that down to the status
                            //   gatherer (and wherever else we're using it)?
                            tempTable =
                            getTableStatus(
                                tableName.asTempTable(internalNamespace = internalTableDataset)
                            ),
                        )
                }
            }
        }
        return map
    }

    private fun getTableStatus(tableName: TableName): DirectLoadTableStatus? {
        // val table = clickhouseClient.query("SELECT count(1) FROM ${tableName.name}").get()
        //     .inputStream.

        return DirectLoadTableStatus(isEmpty = true)
    }
}
