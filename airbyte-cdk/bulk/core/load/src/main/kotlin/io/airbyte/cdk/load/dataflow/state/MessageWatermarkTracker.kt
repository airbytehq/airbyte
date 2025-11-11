/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow.state

import jakarta.inject.Singleton
import java.time.Clock
import java.time.Instant
import java.util.concurrent.atomic.AtomicReference

/**
 * Tracks the timestamp of the last message received from the source.
 *
 * This is used to detect when sources have stalled and stopped emitting records, which can cause
 * the destination to pause. By tracking the watermark (last message timestamp), we can identify
 * and log when no messages have been received for an extended period.
 */
@Singleton
class MessageWatermarkTracker(private val clock: Clock = Clock.systemUTC()) {
    private val lastMessageTimestamp = AtomicReference<Instant?>(null)

    /**
     * Updates the watermark to the current time, indicating a message was just received.
     */
    fun updateWatermark() {
        lastMessageTimestamp.set(clock.instant())
    }

    /**
     * Gets the timestamp of the last message received, or null if no messages have been received yet.
     */
    fun getLastMessageTimestamp(): Instant? {
        return lastMessageTimestamp.get()
    }

    /**
     * Checks if the watermark indicates the source may be stalled.
     *
     * @param thresholdMillis The threshold in milliseconds after which the source is considered stalled
     * @return true if no messages have been received within the threshold period, false otherwise
     */
    fun isStalled(thresholdMillis: Long): Boolean {
        val lastTimestamp = lastMessageTimestamp.get() ?: return false
        val now = clock.instant()
        return now.toEpochMilli() - lastTimestamp.toEpochMilli() > thresholdMillis
    }

    /**
     * Gets the duration in milliseconds since the last message was received.
     *
     * @return the duration in milliseconds, or null if no messages have been received yet
     */
    fun getMillisSinceLastMessage(): Long? {
        val lastTimestamp = lastMessageTimestamp.get() ?: return null
        val now = clock.instant()
        return now.toEpochMilli() - lastTimestamp.toEpochMilli()
    }
}
