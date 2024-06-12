/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.internal

import com.google.common.annotations.VisibleForTesting
import java.time.Duration
import java.time.Instant
import java.util.concurrent.atomic.AtomicReference
import java.util.function.Supplier

/**
 * Tracks heartbeats and, when asked, says if it has been too long since the last heartbeat. He's
 * dead Jim!
 *
 * It is ThreadSafe.
 */
class HeartbeatMonitor
@VisibleForTesting
constructor(
    private val heartBeatFreshDuration: Duration?,
    private val nowSupplier: Supplier<Instant>
) {
    private val lastBeat = AtomicReference<Instant>(null)

    constructor(
        heartBeatFreshDuration: Duration?
    ) : this(heartBeatFreshDuration, Supplier<Instant> { Instant.now() })

    /** Register a heartbeat */
    fun beat() {
        lastBeat.set(nowSupplier.get())
    }

    val isBeating: Boolean
        /**
         *
         * @return true if the last heartbeat is still "fresh". i.e. time since last heartbeat is
         * less than heartBeatFreshDuration. otherwise, false.
         */
        get() {
            val instantFetched = lastBeat.get()
            val now = nowSupplier.get()
            return instantFetched != null &&
                instantFetched.plus(heartBeatFreshDuration).isAfter(now)
        }
}
