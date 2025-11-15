package io.airbyte.integrations.destination.mysql.dataflow

import io.airbyte.cdk.load.dataflow.aggregate.Aggregate
import io.airbyte.cdk.load.dataflow.aggregate.AggregateFactory
import io.airbyte.cdk.load.dataflow.aggregate.StoreKey
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.mysql.write.load.MySQLInsertBuffer
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import javax.sql.DataSource

@Factory
class MySQLAggregateFactory(
    private val dataSource: DataSource,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
) : AggregateFactory {

    @Singleton
    override fun create(key: StoreKey): Aggregate {
        val tableName = streamStateStore.get(key)!!.tableName

        val buffer = MySQLInsertBuffer(
            tableName = tableName,
            dataSource = dataSource,
        )

        return MySQLAggregate(buffer)
    }
}
