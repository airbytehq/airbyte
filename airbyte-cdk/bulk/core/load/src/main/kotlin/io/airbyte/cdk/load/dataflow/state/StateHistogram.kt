/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap

/** A state generally refers to a single partition but can refer to many (namely, in CDC) */
data class StateKey(
    val id: Long,
    val partitionKeys: List<PartitionKey>,
) : Comparable<StateKey> {
    override fun compareTo(other: StateKey): Int {
        return this.id.compareTo(other.id)
    }
}

/** A record is always associated with a single partition. */
data class PartitionKey(
    val id: String,
)

open class Histogram<T>(private val map: ConcurrentMap<T, Long> = ConcurrentHashMap()) {
    fun increment(key: T): Histogram<T> {
        return this.apply { map.merge(key, 1, Long::plus) }
    }

    fun merge(other: Histogram<T>): Histogram<T> {
        return this.apply { other.map.forEach { map.merge(it.key, it.value, Long::plus) } }
    }

    fun get(key: T): Long? = map[key]

    fun remove(key: T): Long? = map.remove(key)
}

typealias StateHistogram = Histogram<StateKey>

typealias PartitionHistogram = Histogram<PartitionKey>
