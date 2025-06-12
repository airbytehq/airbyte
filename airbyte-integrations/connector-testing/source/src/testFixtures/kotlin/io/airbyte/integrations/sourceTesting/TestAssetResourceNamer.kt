/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.sourceTesting

import java.time.Clock
import kotlin.random.Random

/**
 * Structured names with timestamps make it easy to clean up orphaned test data. Names look like
 * "TEST_XXXXXXXX_123456789". We use seconds instead of millis in order to keep the names short
 * enough to be valid in all DBs. We decode it in millis as a convenience for the consumer, despite
 * the loss in precision.
 *
 * @param clock injectable clock for testability. Use default UTC clock in production.
 * @param randomNameSegmentGenerator injectable randomized segment generator for testability. Use
 * default in production.
 */
class TestAssetResourceNamer(
    private val clock: Clock = Clock.systemUTC(), // always use UTC to avoid race conditions
    private val randomNameSegmentGenerator: RandomNameSegmentGenerator =
        RandomNameSegmentGenerator(),
) {

    private val prefix = "TEST"
    private val randomLength = 8

    fun getName(): String {
        return "${prefix}_${randomNameSegmentGenerator.generate(randomLength)}_${seconds()}"
    }

    fun millisFromName(name: String): Long? {
        if (!name.startsWith(prefix)) {
            return null
        }
        return try {
            name.substring(prefix.length + randomLength + 2).toLong().secondsToMillis()
        } catch (e: Exception) {
            null
        }
    }

    private fun seconds(): Long {
        return clock.millis().millisToSeconds()
    }

    private fun Long.millisToSeconds(): Long {
        return (this / 1000)
    }

    private fun Long.secondsToMillis(): Long {
        return (this * 1000)
    }
}

class RandomNameSegmentGenerator(private val random: Random = Random.Default) {
    fun generate(randomLength: Int): String {
        val chars = ('A'..'Z') + ('0'..'9')
        return (1..randomLength).map { random.nextInt(chars.size) }.map(chars::get).joinToString("")
    }
}
