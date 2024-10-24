/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.integrations.base.DestinationConfig.Companion.instance
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import java.util.concurrent.ConcurrentHashMap
import java.util.function.Supplier
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * A slightly more complicated way to keep track of when to perform type and dedupe operations per
 * stream
 */
class TypeAndDedupeOperationValve
@JvmOverloads
constructor(private val nowness: Supplier<Long> = SYSTEM_NOW) :
    ConcurrentHashMap<AirbyteStreamNameNamespacePair, Long?>() {
    private val incrementalIndex = ConcurrentHashMap<AirbyteStreamNameNamespacePair, Int>()

    @SuppressFBWarnings("NP_PARAMETER_MUST_BE_NONNULL_BUT_MARKED_AS_NULLABLE")
    override fun put(key: AirbyteStreamNameNamespacePair, value: Long?): Long? {
        if (!incrementalIndex.containsKey(key)) {
            incrementalIndex[key] = 0
        }
        return super.put(key, value)
    }

    /**
     * Adds a stream specific timestamp to track type and dedupe operations
     *
     * @param key the AirbyteStreamNameNamespacePair to track
     */
    fun addStream(key: AirbyteStreamNameNamespacePair) {
        put(key, nowness.get())
    }

    fun addStreamIfAbsent(key: AirbyteStreamNameNamespacePair) {
        putIfAbsent(key, nowness.get())
        incrementalIndex.putIfAbsent(key, 0)
    }

    /**
     * Whether we should type and dedupe at this point in time for this particular stream.
     *
     * @param key the stream in question
     * @return a boolean indicating whether we have crossed the interval threshold for typing and
     * deduping.
     */
    fun readyToTypeAndDedupe(key: AirbyteStreamNameNamespacePair): Boolean {
        if (!instance!!.getBooleanValue("enable_incremental_final_table_updates")) {
            LOGGER.info("Skipping Incremental Typing and Deduping")
            return false
        }
        if (!containsKey(key)) {
            return false
        }

        return nowness.get() - get(key)!! >
            typeAndDedupeIncreasingIntervals[incrementalIndex[key]!!]
    }

    /**
     * Increment the interval at which typing and deduping should occur for the stream, max out at
     * last index of [TypeAndDedupeOperationValve.typeAndDedupeIncreasingIntervals]
     *
     * @param key the stream to increment the interval of
     * @return the index of the typing and deduping interval associated with this stream
     */
    fun incrementInterval(key: AirbyteStreamNameNamespacePair): Int {
        if (incrementalIndex[key]!! < typeAndDedupeIncreasingIntervals.size - 1) {
            incrementalIndex[key] = incrementalIndex[key]!! + 1
        }
        return incrementalIndex[key]!!
    }

    /**
     * Meant to be called after [TypeAndDedupeOperationValve.readyToTypeAndDedupe] will set a
     * streams last operation to the current time and increase its index reference in
     * [TypeAndDedupeOperationValve.typeAndDedupeIncreasingIntervals]
     *
     * @param key the stream to update
     */
    fun updateTimeAndIncreaseInterval(key: AirbyteStreamNameNamespacePair) {
        put(key, nowness.get())
        incrementInterval(key)
    }

    /**
     * Get the current interval for the stream
     *
     * @param key the stream in question
     * @return a long value representing the length of the interval milliseconds
     */
    fun getIncrementInterval(key: AirbyteStreamNameNamespacePair): Long {
        return typeAndDedupeIncreasingIntervals[incrementalIndex[key]!!]
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(TypeAndDedupeOperationValve::class.java)

        private const val NEGATIVE_MILLIS: Long = -1
        private const val SIX_HOURS_MILLIS = (1000 * 60 * 60 * 6).toLong()

        // New users of airbyte likely want to see data flowing into their tables as soon as
        // possible, and
        // we want to catch new errors which might appear early within an incremental sync.
        // However, as their destination tables grow in size, typing and de-duping data becomes an
        // expensive
        // operation.
        // To strike a balance between showing data quickly and not slowing down the entire sync, we
        // use an
        // increasing interval based approach, from 0 up to 4 hours.
        // This is not fancy, just hard coded intervals.
        val typeAndDedupeIncreasingIntervals: List<Long> =
            java.util.List.of(NEGATIVE_MILLIS, SIX_HOURS_MILLIS)

        private val SYSTEM_NOW = Supplier { System.currentTimeMillis() }
    }
}
