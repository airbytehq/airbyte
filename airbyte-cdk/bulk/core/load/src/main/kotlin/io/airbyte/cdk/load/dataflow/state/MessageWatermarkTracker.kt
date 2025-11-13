/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import jakarta.inject.Singleton
import java.time.Clock
import java.util.concurrent.atomic.AtomicLong

/**
 * Tracks the timestamp of the last message received from the source.
 *
 * This is used to detect when sources have stalled and stopped emitting records, which can cause
 * the destination to pause. By tracking the watermark (last message timestamp), we can identify
 * and log when no messages have been received for an extended period.
 *
 * Performance optimization: Uses the emittedAtMs timestamp already present on messages, avoiding
 * any clock system calls. This has zero performance overhead in the hot path.
 */
@Singleton
class MessageWatermarkTracker(
    private val clock: Clock = Clock.systemUTC()
) {
    private val lastMessageTimestampMs = AtomicLong(0L)

    /**
     * Updates the watermark with the given message timestamp.
     *
     * @param emittedAtMs The emittedAt timestamp from the message in milliseconds since epoch
     */
    fun updateWatermark(emittedAtMs: Long) {
        lastMessageTimestampMs.set(emittedAtMs)
    }

    /**
     * Gets the timestamp of the last message received in milliseconds since epoch,
     * or null if no messages have been received yet.
     */
    fun getLastMessageTimestampMs(): Long? {
        val timestamp = lastMessageTimestampMs.get()
        return if (timestamp == 0L) null else timestamp
    }

    /**
     * Checks if the watermark indicates the source may be stalled.
     *
     * @param thresholdMillis The threshold in milliseconds after which the source is considered stalled
     * @return true if no messages have been received within the threshold period, false otherwise
     */
    fun isStalled(thresholdMillis: Long): Boolean {
        val lastTimestampMs = lastMessageTimestampMs.get()
        if (lastTimestampMs == 0L) return false
        val nowMs = clock.instant().toEpochMilli()
        return nowMs - lastTimestampMs > thresholdMillis
    }

    /**
     * Gets the duration in milliseconds since the last message was received.
     *
     * @return the duration in milliseconds, or null if no messages have been received yet
     */
    fun getMillisSinceLastMessage(): Long? {
        val lastTimestampMs = lastMessageTimestampMs.get()
        if (lastTimestampMs == 0L) return null
        val nowMs = clock.instant().toEpochMilli()
        return nowMs - lastTimestampMs
    }
}
