/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.pipeline

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.mockk.every
import io.mockk.impl.annotations.MockK
import kotlin.random.Random
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class DefaultPipelineFlushStrategyTest {
    companion object {
        private const val MAX_DATA_AGE_SECONDS = 10L
    }

    @MockK(relaxed = true) lateinit var config: DestinationConfiguration

    @BeforeEach
    fun setup() {
        every { config.maxTimeWithoutFlushingDataSeconds } returns MAX_DATA_AGE_SECONDS
    }

    @Test
    fun `always flush if microbatching is set and input count gt 0`() {
        // If the legacy batch override is set, assume we're microbatching and force
        // a finish for every row.
        val microBatchOverride = 1L
        val strategy = DefaultPipelineFlushStrategy(microBatchOverride, config)
        val prng = Random(0)
        repeat(1000) {
            if (it > 0) {
                assert(strategy.shouldFlush(it.toLong(), prng.nextLong()))
            } else {
                assert(!strategy.shouldFlush(it.toLong(), prng.nextLong()))
            }
        }
    }

    @Test
    fun `flush if microbatching is not set and data is too old`() {
        val strategy = DefaultPipelineFlushStrategy(null, config)

        assert(strategy.shouldFlush(1, MAX_DATA_AGE_SECONDS * 1000L))
        assert(strategy.shouldFlush(1, MAX_DATA_AGE_SECONDS * 1000L + 1))
        assert(!strategy.shouldFlush(1, MAX_DATA_AGE_SECONDS * 1000L - 1))
        assert(!strategy.shouldFlush(0, MAX_DATA_AGE_SECONDS * 1000L))
    }
}
