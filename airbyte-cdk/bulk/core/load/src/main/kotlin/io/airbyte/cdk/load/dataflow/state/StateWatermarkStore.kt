package io.airbyte.cdk.load.dataflow.state

import io.airbyte.cdk.load.command.DestinationStream
import java.util.concurrent.ConcurrentHashMap

typealias StoreKey = DestinationStream.Descriptor

class StateWatermarkStore(
    private val factory: (StoreKey) -> StateHistogram,
) {
    private val watermarks = ConcurrentHashMap<StoreKey, StateHistogram>()

    fun updateOrCreate(desc: StoreKey, stateHistogram: StateHistogram): StateHistogram {
        var watermark = watermarks.computeIfAbsent(desc) { stateHistogram }
        return watermarks.computeIfPresent(desc, { _, w -> w.merge(stateHistogram) })!!
    }

    fun remove(desc: StoreKey): StateHistogram {
        val agg = watermarks.computeIfPresent(desc) { _, _ -> null }
        return agg!!
    }

}
