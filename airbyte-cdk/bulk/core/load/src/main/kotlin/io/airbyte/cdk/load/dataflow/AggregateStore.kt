package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.command.DestinationStream
import java.util.concurrent.ConcurrentHashMap

typealias StoreKey = DestinationStream.Descriptor

open class AggregateStore(
    private val aggFactory: (StoreKey) -> Aggregate,
    // TODO: Inject
    private val maxConcurrentAggregates: Int = 42,
) {
    private val aggregates = ConcurrentHashMap<StoreKey, Aggregate>()

    open fun getOrCreate(desc: StoreKey): Aggregate {
        return aggregates.computeIfAbsent(desc, aggFactory)
    }

    open fun remove(desc: StoreKey): Aggregate {
        return aggregates.remove(desc)!!
    }

    open fun getAndRemoveBiggestAggregate(): Aggregate {
        val (descriptorToRemove, aggregate) = aggregates.maxBy { it.value.size() }
        aggregates.remove(descriptorToRemove)
        return aggregate
    }

    open fun canAggregate(desc: StoreKey): Boolean {
        return aggregates.containsKey(desc) || aggregates.size < maxConcurrentAggregates
    }
}
