/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.micronaut.core.annotation.Order
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicReference

@Singleton
@Order(10)
/** [PartitionsCreatorFactory] implementation for CDC with Debezium. */
class CdcPartitionsCreatorFactory<T : Comparable<T>>(
    val concurrencyResource: ConcurrencyResource,
    val globalLockResource: CdcGlobalLockResource,
    val debeziumOps: DebeziumOperations<T>,
) : PartitionsCreatorFactory {

    /**
     * [AtomicReference] to a WAL position upper bound value shared by all [CdcPartitionsCreator]s.
     * This value is set exactly once by the first [CdcPartitionsCreator].
     */
    private val upperBoundReference = AtomicReference<T>()

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator? {
        if (feedBootstrap !is GlobalFeedBootstrap) {
            // Fall through on non-Global streams.
            return null
        }
        return CdcPartitionsCreator(
            concurrencyResource,
            globalLockResource,
            feedBootstrap,
            debeziumOps,
            debeziumOps,
            upperBoundReference,
        )
    }
}
