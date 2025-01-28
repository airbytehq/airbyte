package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.read.*
import io.airbyte.cdk.read.cdc.CdcPartitionsCreator
import io.airbyte.cdk.read.cdc.CdcPartitionsCreatorFactory
import io.airbyte.cdk.read.cdc.DebeziumOperations
import io.micronaut.context.annotation.Primary
import io.micronaut.core.annotation.Order
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicReference

@Singleton
@Order(9)
@Primary
/** [PartitionsCreatorFactory] implementation for CDC with Debezium. */
class MsSqlServerCdcPartitionCreatorFactory<T : Comparable<T>>(
    concurrencyResource: ConcurrencyResource,
    debeziumOps: DebeziumOperations<T>,
) : CdcPartitionsCreatorFactory<T>(concurrencyResource, debeziumOps) {

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator? {
        if (feedBootstrap !is GlobalFeedBootstrap) {
            // Fall through on non-Global streams.
            return null
        }
        return MsSqlServerCdcPartitionCreator(
            concurrencyResource,
            feedBootstrap,
            debeziumOps,
            debeziumOps,
            lowerBoundReference,
            upperBoundReference,
        )
    }
}
