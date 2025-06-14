/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import com.clickhouse.client.api.Client
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.airbyte.integrations.destination.clickhouse_v2.config.ClickhouseFinalTableNameGenerator
import io.airbyte.integrations.destination.clickhouse_v2.write.RecordMunger
import jakarta.inject.Singleton

@Singleton
class ClickhouseDirectLoaderFactory(
    private val clickhouseClient: Client,
    private val tableNameMapper: ClickhouseFinalTableNameGenerator,
    private val munger: RecordMunger,
) :
    DirectLoaderFactory<ClickhouseDirectLoader> {
    override val maxNumOpenLoaders = 2

    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int
    ): ClickhouseDirectLoader {
        // Initialize the buffer
        val tableName = tableNameMapper.getTableName(streamDescriptor)
        val buffer = ClickhouseBinaryRowInsertBuffer(tableName, clickhouseClient)

        return ClickhouseDirectLoader(
            munger,
            buffer,
        )
    }
}
