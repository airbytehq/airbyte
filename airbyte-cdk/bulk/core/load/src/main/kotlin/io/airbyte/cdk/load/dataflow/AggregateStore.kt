package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.command.DestinationStream
import java.util.concurrent.ConcurrentHashMap

typealias StoreKey = DestinationStream.Descriptor

class AggregateStore(
    private val aggFactory: (StoreKey) -> Aggregate,
) {
    private val aggregates = ConcurrentHashMap<StoreKey, Aggregate>()

    fun getOrCreate(desc: StoreKey): Aggregate {
        return aggregates.computeIfAbsent(desc, aggFactory)
    }

    fun remove(desc: StoreKey): Aggregate {
        return aggregates.computeIfPresent(desc) { _, _ -> null }!!
    }

}
