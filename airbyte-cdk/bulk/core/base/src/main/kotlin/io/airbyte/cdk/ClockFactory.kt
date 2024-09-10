/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk

import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.time.Clock
import java.time.Duration
import java.time.Instant
import java.time.ZoneOffset

/** Injects the system clock in production and a fake clock in tests. */
@Factory
class ClockFactory {

    @Singleton @Requires(notEnv = [Environment.TEST]) fun system(): Clock = Clock.systemUTC()

    @Singleton
    @Requires(env = [Environment.TEST])
    @Requires(notEnv = [OFFSET_CLOCK])
    fun fixed(): Clock = Clock.fixed(fakeNow, ZoneOffset.UTC)

    @Singleton
    @Requires(env = [Environment.TEST])
    @Requires(env = [OFFSET_CLOCK])
    fun offset(): Clock = Clock.offset(Clock.systemUTC(), Duration.between(fakeNow, Instant.now()))

    companion object {
        const val OFFSET_CLOCK = "offset-clock"

        /** Some convenient timestamp with an easy-to-read ISO8601 representation. */
        val fakeNow: Instant = Instant.ofEpochSecond(3133641600)
    }
}
