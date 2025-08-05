/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

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
        return this.apply {
            map.merge(key, 1, Long::plus)
        }
    }

    fun merge(other: StateHistogram): StateHistogram {
        return this.apply {
            other.map.forEach {
                map.merge(it.key, it.value, Long::plus)
            }
        }
    }

    fun remove(key: StateKey): Long? = map.remove(key)
}
