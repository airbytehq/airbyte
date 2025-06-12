/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.sourceTesting

import java.time.Clock
import kotlin.random.Random

// Structured names with timestamps make it easy to clean up orphaned test data.
// Names look like "TEST_XXXX_123456789".
class TestAssetResourceNamer(
    // Inject the clock and random segment generator for testability
    private val clock: Clock,
    private val randomNameSegmentGenerator: RandomNameSegmentGenerator,
) {

    private val prefix = "TEST"
    private val randomLength = 4

    fun getName(): String {
        return "${prefix}_${randomNameSegmentGenerator.generate(4)}_${clock.millis()}"
    }

    fun millisFromName(name: String): Long? {
        if (!name.startsWith(prefix)) {
            return null
        }
        return try {
            name.substring(prefix.length + randomLength + 2).toLong()
        } catch (e: Exception) {
            null
        }
    }
}

class RandomNameSegmentGenerator(private val random: Random = Random.Default) {
    fun generate(randomLength: Int): String {
        val chars = ('A'..'Z') + ('0'..'9')
        return (1..randomLength).map { random.nextInt(chars.size) }.map(chars::get).joinToString("")
    }
}
