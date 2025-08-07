/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap

data class StateKey(
    val id: Long,
    val partitionIds: List<String>,
) : Comparable<StateKey> {
    override fun compareTo(other: StateKey): Int {
        return this.id.compareTo(other.id)
    }
}

data class PartitionKey(
    val id: String,
)

open class Histogram<T>(open val map: ConcurrentMap<T, Long> = ConcurrentHashMap()) {
    fun increment(key: T): Histogram<T> {
        return this.apply { map.merge(key, 1, Long::plus) }
    }

    fun merge(other: Histogram<T>): Histogram<T> {
        return this.apply { other.map.forEach { map.merge(it.key, it.value, Long::plus) } }
    }

    fun remove(key: T): Long? = map.remove(key)
}

typealias StateHistogram = Histogram<StateKey>

typealias PartitionHistogram = Histogram<PartitionKey>
