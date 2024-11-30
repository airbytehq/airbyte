/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file

import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicLong

@Singleton
@Primary
@Requires(env = ["MockTimeProvider"])
open class MockTimeProvider : TimeProvider {
    private var syncTime = AtomicLong(0)
    private var currentTime = AtomicLong(0)

    fun setCurrentTime(currentTime: Long) {
        this.currentTime.set(currentTime)
    }

    fun setSyncTime(currentTime: Long) {
        this.syncTime.set(currentTime)
    }

    override fun currentTimeMillis(): Long {
        return currentTime.get()
    }

    override suspend fun delay(ms: Long) {
        currentTime.addAndGet(ms)
    }

    override fun syncTimeMillis(): Long {
        return syncTime.get()
    }
}
