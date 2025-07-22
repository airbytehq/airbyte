/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.skeleton_directload.write.typing_deduping.direct_load_tables

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.DatabaseInitialStatusGatherer
import io.airbyte.cdk.load.orchestration.db.TableName
import io.airbyte.cdk.load.orchestration.db.TempTableNameGenerator
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadInitialStatus
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableStatus
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalog
import io.airbyte.integrations.destination.skeleton_directload.SkeletonDirectLoadClient
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.coroutineScope
import kotlinx.coroutines.launch

@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "kotlin coroutines")
class SkeletonDirectLoadDatabaseInitialStatusGatherer(
    private val skeletonClient: SkeletonDirectLoadClient,
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
                            realTable = DirectLoadTableStatus(isEmpty=false),
                            tempTable = DirectLoadTableStatus(isEmpty=false),
                        )
                }
            }
        }
        return map
    }

    private fun getTableStatus(tableName: TableName): DirectLoadTableStatus? {
        // The flow here should be to retrieve a table information and based on if there is data
        // in there, then we define if isEmpty is true or false.
        // Right now it is forced to false to get this thing to compile
        return DirectLoadTableStatus(isEmpty = false)
    }
}
