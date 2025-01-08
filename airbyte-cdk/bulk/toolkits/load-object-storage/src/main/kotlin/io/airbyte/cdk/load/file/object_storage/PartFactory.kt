/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import java.util.concurrent.atomic.AtomicReference
import org.apache.mina.util.ConcurrentHashSet

/**
 * Generates part w/ metadata for a multi-part upload for a given key and file no. parts are
 * 1-indexed. For convenience, empty parts are tolerated but not counted by the assembler.
 *
 * Not thread-safe. It is expected that the parts are generated in order.
 */
class PartFactory(
    val key: String,
    val fileNumber: Long,
) {
    var totalSize: Long = 0
    private var nextIndex: Int = 0
    private var finalProduced = false

    fun nextPart(bytes: ByteArray?, isFinal: Boolean = false): Part {
        if (finalProduced) {
            throw IllegalStateException("Final part already produced")
        }
        finalProduced = isFinal

        totalSize += bytes?.size?.toLong() ?: 0
        // Only advance the index if the part isn't empty.
        // This way empty parts can be ignored, but empty final parts
        // can still convey the final index.
        if (bytes != null) {
            nextIndex++ // pre-increment as parts are 1-indexed
        }
        return Part(
            key = key,
            fileNumber = fileNumber,
            partIndex = nextIndex,
            bytes = bytes,
            isFinal = isFinal
        )
    }
}

/**
 * Reassembles part metadata into a view of the upload state.
 *
 * Usage: add the parts created by the factory.
 *
 * [PartBookkeeper.isComplete] will be true when all the parts AND the final part have been seen,
 * regardless of the order in which they were added.
 *
 * Thread-safe: parts can be added by multiple threads in any order.
 */
data class Part(
    val key: String,
    val fileNumber: Long,
    val partIndex: Int,
    val bytes: ByteArray?,
    val isFinal: Boolean,
) {
    val isEmpty: Boolean
        get() = bytes == null
}

class PartBookkeeper {
    private val partIndexes = ConcurrentHashSet<Int>()
    private var finalIndex = AtomicReference<Int>(null)

    val isEmpty: Boolean
        get() = partIndexes.isEmpty()

    fun add(part: Part) {
        // Only add non-empty parts
        if (part.bytes != null) {
            if (part.partIndex in partIndexes) {
                throw IllegalStateException(
                    "Part index ${part.partIndex} already seen for ${part.key}"
                )
            }
            partIndexes.add(part.partIndex)
        }

        // The final part conveys the last
        // index even if it is empty.
        if (part.isFinal) {
            if (!finalIndex.compareAndSet(null, part.partIndex)) {
                throw IllegalStateException("Final part already seen for ${part.key}")
            }
        }
    }

    /**
     * Complete
     * 1. we have seen a final part
     * 2. there are no gaps in the part indices
     * 3. the last index is the final index
     */
    val isComplete: Boolean
        get() = finalIndex.get()?.let { it == partIndexes.size } ?: false
}
