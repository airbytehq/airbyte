/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.PartitionsCreatorFactorySupplier
import io.micronaut.core.annotation.Order
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicReference

@Singleton
@Order(10)
/** [PartitionsCreatorFactory] implementation for CDC with Debezium. */
class CdcPartitionsCreatorFactory<T : Comparable<T>>(
    val concurrencyResource: ConcurrencyResource,
    val cdcPartitionsCreatorDbzOps: CdcPartitionsCreatorDebeziumOperations<T>,
    val cdcPartitionReaderDbzOps: CdcPartitionReaderDebeziumOperations<T>,
) : PartitionsCreatorFactory {

    /**
     * [AtomicReference] to a WAL position lower bound value shared by all [CdcPartitionsCreator]s.
     * This value is updated by the [CdcPartitionsCreator] based on the incumbent state and is used
     * to detect stalls.
     */
    private val lowerBoundReference = AtomicReference<T>()

    /**
     * [AtomicReference] to a WAL position upper bound value shared by all [CdcPartitionsCreator]s.
     * This value is set exactly once by the first [CdcPartitionsCreator].
     */
    private val upperBoundReference = AtomicReference<T>()

    /** [AtomicReference] used to trigger resetting a sync when not null. */
    private val resetReason = AtomicReference<String?>(null)

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator? {
        if (feedBootstrap !is GlobalFeedBootstrap) {
            // Fall through on non-Global streams.
            return null
        }
        return CdcPartitionsCreator(
            concurrencyResource,
            feedBootstrap,
            cdcPartitionsCreatorDbzOps,
            cdcPartitionReaderDbzOps,
            lowerBoundReference,
            upperBoundReference,
            resetReason,
        )
    }
}

@Singleton
class CdcPartitionsCreatorFactorySupplier<T : CdcPartitionsCreatorFactory<C>, C : Comparable<C>>(
    val factory: T
) : PartitionsCreatorFactorySupplier<T> {
    override fun get(): T = factory
}
