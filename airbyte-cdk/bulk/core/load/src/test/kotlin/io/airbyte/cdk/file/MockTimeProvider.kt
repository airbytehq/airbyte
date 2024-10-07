/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.file

import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

@Singleton
@Primary
@Requires(env = ["MockTimeProvider"])
class MockTimeProvider : TimeProvider {
    private var currentTime: Long = 0

    override fun currentTimeMillis(): Long {
        return currentTime
    }

    fun setCurrentTime(currentTime: Long) {
        this.currentTime = currentTime
    }

    override suspend fun delay(ms: Long) {
        currentTime += ms
    }
}
