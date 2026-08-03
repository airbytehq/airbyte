/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.toolkits.iceberg.parquet.io

import org.apache.iceberg.StructLike
import org.apache.iceberg.types.Types
import org.apache.iceberg.util.StructLikeMap
import org.apache.iceberg.util.StructLikeUtil

/** Keys affected by one bounded positional-delete flush. */
class TouchedKeys(
    keyType: Types.StructType,
    private val maximum: Int = PositionalDeleteResolver.DEFAULT_MAX_TOUCHED_KEYS,
) {
    private val keys = StructLikeMap.create<Boolean>(keyType)
    private val currentWrites = StructLikeMap.create<PositionalDeleteResolver.RowLocation>(keyType)
    private val superseded = mutableListOf<PositionalDeleteResolver.RowLocation>()

    fun markWritten(
        key: StructLike,
        location: PositionalDeleteResolver.RowLocation,
    ) {
        keys[StructLikeUtil.copy(key)] = true
        currentWrites.remove(key)?.let(superseded::add)
        currentWrites[StructLikeUtil.copy(key)] = location
    }

    /** Tracks an inserted row for same-flush supersession without treating INSERT as an upsert. */
    fun markInserted(
        key: StructLike,
        location: PositionalDeleteResolver.RowLocation,
    ) {
        currentWrites.remove(key)?.let(superseded::add)
        currentWrites[StructLikeUtil.copy(key)] = location
    }

    fun markDeleted(key: StructLike) {
        keys[StructLikeUtil.copy(key)] = true
        currentWrites.remove(key)?.let(superseded::add)
    }

    fun keys(): Set<StructLike> = keys.keys

    fun supersededWithinFlush(): Sequence<PositionalDeleteResolver.RowLocation> =
        superseded.asSequence()

    fun isFull(): Boolean = keys.size + superseded.size >= maximum

    fun isEmpty(): Boolean = keys.isEmpty() && superseded.isEmpty()

    /** Clears keys resolved by a batch while retaining current writes for later repeats. */
    fun clear() {
        keys.clear()
        superseded.clear()
    }
}
