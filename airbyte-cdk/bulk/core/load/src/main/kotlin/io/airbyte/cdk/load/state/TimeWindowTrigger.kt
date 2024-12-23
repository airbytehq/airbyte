/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import java.time.Clock

/*
 * Simple time-windowing strategy for bucketing partial aggregates.
 *
 * Works off time relative to the injected @param clock. Generally this is the processing time domain.
 */
data class TimeWindowTrigger(
    private val clock: Clock,
    private val windowWidthMs: Long,
) {
    var openedAtMs: Long? = null
        private set

    /*
     * Sets window open timestamp for computing completeness. Idempotent. Mutative.
     */
    fun open(): Long {
        if (openedAtMs == null) {
            openedAtMs = clock.millis()
        }
        return openedAtMs!!
    }

    /*
     * Returns whether window is complete relative to configured @param windowWidthMs. Non-mutative.
     */
    fun isComplete(): Boolean {
        return openedAtMs?.let { ts -> (clock.millis() - ts) >= windowWidthMs } ?: false
    }
}
