/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.Feed
import io.airbyte.cdk.read.Global
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.StateQuerier
import io.micronaut.core.annotation.Order
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicReference

@Singleton
@Order(10)
/** [PartitionsCreatorFactory] implementation for CDC with Debezium. */
class CdcPartitionsCreatorFactory<T : Comparable<T>>(
    val concurrencyResource: ConcurrencyResource,
    val globalLockResource: CdcGlobalLockResource,
    val outputConsumer: OutputConsumer,
    val debeziumOps: DebeziumOperations<T>,
) : PartitionsCreatorFactory {

    /**
     * [AtomicReference] to a WAL position upper bound value shared by all [CdcPartitionsCreator]s.
     * This value is set exactly once by the first [CdcPartitionsCreator].
     */
    private val upperBoundReference = AtomicReference<T>()

    override fun make(stateQuerier: StateQuerier, feed: Feed): PartitionsCreator? {
        if (feed !is Global) {
            // Fall through on non-Global streams.
            return null
        }
        val opaqueStateValue: OpaqueStateValue? = stateQuerier.current(feed)
        return CdcPartitionsCreator(
            concurrencyResource,
            globalLockResource,
            stateQuerier,
            outputConsumer,
            debeziumOps,
            debeziumOps,
            upperBoundReference,
            opaqueStateValue,
        )
    }
}
