/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.table.TableName
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.snowflake.client.SnowflakeAirbyteClient
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.integrations.destination.snowflake.sql.SnowflakeColumnUtils
import io.airbyte.integrations.destination.snowflake.write.load.SnowflakeInsertBuffer
import io.micronaut.cache.annotation.CacheConfig
import io.micronaut.cache.annotation.Cacheable
import jakarta.inject.Singleton

@Singleton
@CacheConfig("table-columns")
// class has to be open to make the cache stuff work
open class SnowflakeAggregateFactory(
    private val snowflakeClient: SnowflakeAirbyteClient,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    private val snowflakeConfiguration: SnowflakeConfiguration,
    private val snowflakeColumnUtils: SnowflakeColumnUtils,
) : AggregateFactory {
    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName
        val buffer =
            SnowflakeInsertBuffer(
                tableName = tableName,
                columns = getTableColumns(tableName),
                snowflakeClient = snowflakeClient,
                snowflakeConfiguration = snowflakeConfiguration,
                snowflakeColumnUtils = snowflakeColumnUtils,
            )
        return SnowflakeAggregate(buffer = buffer)
    }

    // We assume that a table isn't getting altered _during_ a sync.
    // This allows us to only SHOW COLUMNS once per table per sync,
    // rather than refetching it on every aggregate.
    @Cacheable
    // function has to be open to make caching work
    internal open fun getTableColumns(tableName: TableName) =
        snowflakeClient.describeTable(tableName)
}
