package io.airbyte.cdk.load.dataflow.stats

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.dataflow.state.Histogram
import io.airbyte.cdk.load.dataflow.state.PartitionHistogram
import io.airbyte.cdk.load.dataflow.state.PartitionKey
import io.airbyte.protocol.models.v0.StreamDescriptor
import jakarta.inject.Singleton
import java.util.concurrent.ConcurrentHashMap

@Singleton
class StreamStatsStore(
    private val catalog: DestinationCatalog,
) {
    private val readCounts = Histogram<StreamDescriptor>()

    private val aggregatedStats = ConcurrentHashMap<StreamDescriptor, PartitionStats>()

    fun incrementReadCount(s: StreamDescriptor) = readCounts.increment(s, 1)

    fun acceptStats(s: StreamDescriptor, flushed: PartitionHistogram, bytes: PartitionHistogram) =
        aggregatedStats.merge(s, PartitionStats(flushed, bytes), PartitionStats::merge)

    fun removeStats(s: StreamDescriptor, p: PartitionKey): EmissionStats? =
        aggregatedStats[s]?.let {
            EmissionStats(
                it.flushed.remove(p)!!,
                it.bytes.remove(p)!!,
            )
        }
}

data class EmissionStats(
    val count: Long,
    val bytes: Long,
)

data class PartitionStats(
    // Counts of flushed messages by partition id
    val flushed: PartitionHistogram = PartitionHistogram(),
    // Counts of flushed bytes by partition id
    val bytes: PartitionHistogram = PartitionHistogram(),
) {
    fun merge(other: PartitionStats): PartitionStats = this.apply {
        flushed.merge(other.flushed)
        bytes.merge(other.bytes)
    }
}
