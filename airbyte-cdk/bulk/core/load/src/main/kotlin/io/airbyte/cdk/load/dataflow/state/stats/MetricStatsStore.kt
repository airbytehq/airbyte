package io.airbyte.cdk.load.dataflow.state.stats

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.state.Histogram
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Singleton
class MetricStatsStore {
    private val stats = ConcurrentHashMap<PartitionKey, Map<DestinationStream.Descriptor, Histogram<String>>>()

    fun addStats(p: PartitionKey, d: DestinationStream.Descriptor, h: Histogram<String>) {}

    fun drainStats(ps: List<PartitionKey>): Map<DestinationStream.Descriptor, Histogram<String>> {
        return ps
            .mapNotNull { stats.remove(it) }
            .fold(mutableMapOf()) { acc, perStreamStats ->
                perStreamStats.forEach { (desc, histo) ->
                    acc.merge(desc, histo, Histogram<String>::merge)
                }
                acc
            }
    }
}
