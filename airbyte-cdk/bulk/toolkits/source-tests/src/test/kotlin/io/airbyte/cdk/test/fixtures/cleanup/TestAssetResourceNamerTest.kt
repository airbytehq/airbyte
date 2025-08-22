/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.test.fixtures.cleanup

import io.mockk.every
import io.mockk.mockk
import java.time.Clock
import java.time.Instant
import java.time.ZoneId
import kotlin.test.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

class TestAssetResourceNamerTest {

    val time = Instant.EPOCH
    val clock = Clock.fixed(time, ZoneId.of("UTC"))
    val randomSegment = "XXXXXXXX"
    val randomNameSegmentGenerator = mockk<RandomNameSegmentGenerator>()
    val namer = TestAssetResourceNamer(clock, randomNameSegmentGenerator)
    val name = "TEST_0_XXXXXXXX"

    init {
        every { randomNameSegmentGenerator.generate(any()) } returns randomSegment
    }

    @Test
    fun testGetName() {
        assertEquals(name, namer.getName())
    }

    @Test
    fun testMillisFromName_testName() {
        assertEquals(time.toEpochMilli(), namer.millisFromName(name))
    }

    @Test
    fun testMillisFromName_externalName() {
        assertNull(namer.millisFromName("PROD_1234_HERE"))
    }
}
