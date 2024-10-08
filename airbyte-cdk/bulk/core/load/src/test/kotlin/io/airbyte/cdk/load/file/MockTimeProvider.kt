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
class MockTimeProvider : TimeProvider {
    private var currentTime = AtomicLong(0)

    override fun currentTimeMillis(): Long {
        return currentTime.get()
    }

    fun setCurrentTime(currentTime: Long) {
        this.currentTime.set(currentTime)
    }

    override suspend fun delay(ms: Long) {
        currentTime.addAndGet(ms)
    }
}
