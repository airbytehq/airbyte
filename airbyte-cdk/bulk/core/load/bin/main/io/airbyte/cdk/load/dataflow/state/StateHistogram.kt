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

open class Histogram<T>(private val map: ConcurrentMap<T, Double> = ConcurrentHashMap()) {
    fun increment(key: T, quantity: Double): Histogram<T> =
        this.apply { map.merge(key, quantity, Double::plus) }

    fun merge(other: Histogram<T>): Histogram<T> =
        this.apply { other.map.forEach { map.merge(it.key, it.value, Double::plus) } }

    fun get(key: T): Double? = map[key]

    fun remove(key: T): Double? = map.remove(key)

    fun toMap(): Map<T, Double> = map.toMap()
}

typealias AdditionalStatsHistogram = Histogram<String>

typealias StateHistogram = Histogram<StateKey>

typealias PartitionHistogram = Histogram<PartitionKey>
