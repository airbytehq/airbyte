/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.sourceTesting

import jakarta.inject.Singleton
import java.time.Clock
import kotlin.random.Random

// Structured names with timestamps make it easy to clean up orphaned test data.
// Names look like "TEST_XXXX_123456789".
@Singleton
class TestAssetResourceNamer(
    // Inject the clock for testability
    private val clock: Clock,
) {

    private val prefix = "TEST"
    private val randomLength = 4

    fun getName(): String {
        return "${prefix}_${getRandom()}_${clock.millis()}"
    }

    fun timestampFromName(name: String): Long? {
        if (!name.startsWith(prefix)) {
            return null
        }
        return try {
            name.substring(prefix.length + randomLength + 2).toLong()
        } catch (e: Exception) {
            null
        }
    }

    private fun getRandom(): String {
        val chars = ('A'..'Z') + ('0'..'9')
        return (1..randomLength).map { Random.nextInt(chars.size) }.map(chars::get).joinToString("")
    }
}
