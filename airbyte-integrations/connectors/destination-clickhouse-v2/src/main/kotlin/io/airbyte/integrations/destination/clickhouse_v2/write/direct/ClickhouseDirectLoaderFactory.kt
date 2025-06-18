/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.clickhouse_v2.write.RecordMunger
import jakarta.inject.Singleton

/*
 * Munges the table name and creates the buffer for easier testing.
 */
@Singleton
class ClickhouseDirectLoaderFactory(
    private val clickhouseClient: Client,
    private val stateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val munger: RecordMunger,
) : DirectLoaderFactory<ClickhouseDirectLoader> {
    override val maxNumOpenLoaders = 2

    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int
    ): ClickhouseDirectLoader {
        val tableName = stateStore.get(streamDescriptor)!!.tableName
        val buffer = BinaryRowInsertBuffer(tableName, clickhouseClient)

        return ClickhouseDirectLoader(
            munger,
            buffer,
        )
    }
}
