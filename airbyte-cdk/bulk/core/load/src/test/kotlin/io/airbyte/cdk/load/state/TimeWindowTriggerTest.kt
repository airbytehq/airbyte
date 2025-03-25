/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.state.TimeWindowTriggerTest.Fixtures.TIME_WINDOW_WIDTH_MS
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import java.time.Clock
import java.util.stream.Stream
import kotlin.test.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

@ExtendWith(MockKExtension::class)
class TimeWindowTriggerTest {
    @MockK lateinit var clock: Clock

    private lateinit var timeWindow: TimeWindowTrigger

    @BeforeEach
    fun setup() {
        timeWindow = TimeWindowTrigger(clock, TIME_WINDOW_WIDTH_MS)
    }

    @Test
    fun `open is idempotent`() {
        val initialOpenedAt = 1000L

        every { clock.millis() } returns initialOpenedAt
        val openedAt1 = timeWindow.open()

        assertEquals(initialOpenedAt, openedAt1)

        every { clock.millis() } returns initialOpenedAt + 1
        val openedAt2 = timeWindow.open()

        assertEquals(initialOpenedAt, openedAt2)
    }

    @Test
    fun `isComplete returns false if window not opened`() {
        every { clock.millis() } returns TIME_WINDOW_WIDTH_MS
        assertEquals(false, timeWindow.isComplete())

        every { clock.millis() } returns TIME_WINDOW_WIDTH_MS + 1
        assertEquals(false, timeWindow.isComplete())

        every { clock.millis() } returns TIME_WINDOW_WIDTH_MS + 60000
        assertEquals(false, timeWindow.isComplete())
    }

    @ParameterizedTest
    @MethodSource("windowWidthMatrix")
    fun `isComplete calculates time window based on configured width`(windowWidthMs: Long) {
        every { clock.millis() } returns 0

        timeWindow = TimeWindowTrigger(clock, windowWidthMs)

        val openedAt = timeWindow.open()
        assertEquals(0, openedAt)

        every { clock.millis() } returns windowWidthMs - 1
        assertEquals(false, timeWindow.isComplete())

        every { clock.millis() } returns windowWidthMs - 124
        assertEquals(false, timeWindow.isComplete())

        every { clock.millis() } returns windowWidthMs
        assertEquals(true, timeWindow.isComplete())

        every { clock.millis() } returns windowWidthMs + 1
        assertEquals(true, timeWindow.isComplete())

        every { clock.millis() } returns windowWidthMs + 60000
        assertEquals(true, timeWindow.isComplete())
    }

    object Fixtures {
        const val TIME_WINDOW_WIDTH_MS = 60000L
    }

    companion object {
        @JvmStatic
        private fun windowWidthMatrix(): Stream<Arguments> {
            return Stream.of(
                Arguments.of(100L),
                Arguments.of(10000L),
                Arguments.of(900000L),
                Arguments.of(900001L),
            )
        }
    }
}
