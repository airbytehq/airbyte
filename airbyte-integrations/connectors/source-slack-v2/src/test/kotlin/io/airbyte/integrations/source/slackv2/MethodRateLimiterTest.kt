/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import java.time.Duration
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class MethodRateLimiterTest {

    private class FakeClock(var nanos: Long = 0L) {
        fun advanceSeconds(s: Double) {
            nanos += (s * 1_000_000_000L).toLong()
        }
    }

    @Test
    fun testBurstThenPacing() {
        val clock = FakeClock()
        val limiter =
            MethodRateLimiter(
                "m",
                configuredPerMinute = 60.0,
                burst = 3.0,
                nanoTime = { clock.nanos }
            )
        repeat(3) { Assertions.assertEquals(0L, limiter.tryAcquireOrWaitNanos()) }
        val wait: Long = limiter.tryAcquireOrWaitNanos()
        Assertions.assertTrue(wait in 900_000_000L..1_000_000_000L, "expected ~1s wait, got $wait")
        clock.advanceSeconds(1.0)
        Assertions.assertEquals(0L, limiter.tryAcquireOrWaitNanos())
    }

    @Test
    fun testRateLimitedHalvesRateAndBlocks() {
        val clock = FakeClock()
        val limiter =
            MethodRateLimiter(
                "m",
                configuredPerMinute = 50.0,
                burst = 5.0,
                nanoTime = { clock.nanos }
            )
        // A short Retry-After only halves the rate...
        limiter.onRateLimited(Duration.ofSeconds(1))
        Assertions.assertEquals(25.0, limiter.currentPerMinute())
        clock.advanceSeconds(2.0)
        // ...a long one caps it at what the header implies (30 s: two per minute).
        limiter.onRateLimited(Duration.ofSeconds(30))
        Assertions.assertEquals(2.0, limiter.currentPerMinute())
        val wait: Long = limiter.tryAcquireOrWaitNanos()
        Assertions.assertTrue(wait >= 30_000_000_000L, "blocked for Retry-After, got $wait")
        clock.advanceSeconds(31.0)
        // Blocked no more, but the bucket is empty and refills at two per minute (30 s per token).
        val next: Long = limiter.tryAcquireOrWaitNanos()
        Assertions.assertTrue(next in 1L..30_000_000_000L, "got $next")
        limiter.onRateLimited(Duration.ofSeconds(1))
        limiter.onRateLimited(Duration.ofSeconds(1))
        limiter.onRateLimited(Duration.ofSeconds(1))
        limiter.onRateLimited(Duration.ofSeconds(1))
        limiter.onRateLimited(Duration.ofSeconds(1))
        Assertions.assertEquals(MethodRateLimiter.MIN_PER_MINUTE, limiter.currentPerMinute())
        Assertions.assertEquals(7L, limiter.rateLimitedCount)
    }

    @Test
    fun testSuccessesRestoreTheRate() {
        val clock = FakeClock()
        val limiter =
            MethodRateLimiter(
                "m",
                configuredPerMinute = 50.0,
                burst = 5.0,
                nanoTime = { clock.nanos }
            )
        limiter.onRateLimited(Duration.ofSeconds(1))
        Assertions.assertEquals(25.0, limiter.currentPerMinute())
        repeat(MethodRateLimiter.RECOVERY_SUCCESSES) { limiter.onSuccess() }
        Assertions.assertEquals(31.25, limiter.currentPerMinute())
        repeat(MethodRateLimiter.RECOVERY_SUCCESSES * 3) { limiter.onSuccess() }
        Assertions.assertEquals(50.0, limiter.currentPerMinute())
    }
}
