package io.airbyte.cdk.load.dataflow.state

import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap

data class StateKey(
    val id: String,
)

class StateHistogram(
    val map: ConcurrentMap<StateKey, Long> = ConcurrentHashMap()
) {
    fun increment(key: StateKey): StateHistogram {
        map.merge(
            key,
            1,
            Long::plus,
        )

        return this
    }

    fun merge(other: StateHistogram): StateHistogram {
        return this.apply {
            other.map.forEach {
                map.merge(
                    it.key,
                    it.value,
                    Long::plus,
                )
            }
        }
    }

    fun remove(key: StateKey): Long? = map.remove(key)
}
