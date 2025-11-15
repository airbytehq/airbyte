/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource

class StringInterpolationUtilsTest {

    @Test
    fun `unicodeInterpolatedStrings should generate correct number of steps`() {
        val result = unicodeInterpolatedStrings("a", "z", 5)
        assertEquals(6, result.size, "Should generate steps+1 values (including start and end)")
    }

    @Test
    fun `unicodeInterpolatedStrings should start with start value`() {
        val result = unicodeInterpolatedStrings("apple", "banana", 3)
        assertEquals("apple", result.first(), "First element should be the start string")
    }

    @Test
    fun `unicodeInterpolatedStrings should be monotonically increasing`() {
        val result = unicodeInterpolatedStrings("a", "z", 10)
        for (i in 0 until result.size - 1) {
            assertTrue(
                result[i] <= result[i + 1],
                "Each string should be lexicographically <= the next: ${result[i]} vs ${result[i + 1]}"
            )
        }
    }

    @Test
    fun `unicodeInterpolatedStrings should handle empty start string`() {
        val result = unicodeInterpolatedStrings("", "hello", 3)
        assertEquals(4, result.size)
        assertEquals("", result.first())
    }

    @Test
    fun `unicodeInterpolatedStrings should handle single step`() {
        val result = unicodeInterpolatedStrings("a", "z", 1)
        assertEquals(2, result.size)
        assertEquals("a", result[0])
    }

    @Test
    fun `unicodeInterpolatedStrings should handle zero steps`() {
        val result = unicodeInterpolatedStrings("start", "end", 0)
        assertEquals(1, result.size)
        assertEquals("start", result[0])
    }

    @Test
    fun `unicodeInterpolatedStrings should handle same start and end`() {
        val result = unicodeInterpolatedStrings("test", "test", 5)
        assertEquals(6, result.size)
        result.forEach {
            assertEquals("test", it, "All values should be the same when start equals end")
        }
    }

    @Test
    fun `unicodeInterpolatedStrings should handle multi-byte unicode characters`() {
        val result = unicodeInterpolatedStrings("α", "ω", 3)
        assertEquals(4, result.size)
        assertEquals("α", result.first())
    }

    @Test
    fun `unicodeInterpolatedStrings should handle strings of different lengths`() {
        val result = unicodeInterpolatedStrings("a", "hello", 5)
        assertEquals(6, result.size)
        assertEquals("a", result.first())
    }

    @ParameterizedTest
    @CsvSource("a, z, 2", "hello, world, 4", "test, testing, 3", "0, 9, 5")
    fun `unicodeInterpolatedStrings should generate expected number of results`(
        start: String,
        end: String,
        steps: Int
    ) {
        val result = unicodeInterpolatedStrings(start, end, steps)
        assertEquals(steps + 1, result.size)
    }

    @Test
    fun `guidInterpolatedStrings should generate correct number of steps`() {
        val result =
            guidInterpolatedStrings(
                "00000000-0000-0000-0000-000000000000",
                "ffffffff-ffff-ffff-ffff-ffffffffffff",
                5
            )
        assertEquals(6, result.size, "Should generate steps+1 values (including start and end)")
    }

    @Test
    fun `guidInterpolatedStrings should start with start value`() {
        val start = "00000000-0000-0000-0000-000000000001"
        val end = "ffffffff-ffff-ffff-ffff-ffffffffffff"
        val result = guidInterpolatedStrings(start, end, 3)
        assertEquals(start, result.first(), "First element should be the start string")
    }

    @Test
    fun `guidInterpolatedStrings should be monotonically increasing`() {
        val result =
            guidInterpolatedStrings(
                "00000000-0000-0000-0000-000000000000",
                "ffffffff-ffff-ffff-ffff-ffffffffffff",
                10
            )
        for (i in 0 until result.size - 1) {
            assertTrue(
                result[i] <= result[i + 1],
                "Each GUID should be lexicographically <= the next: ${result[i]} vs ${result[i + 1]}"
            )
        }
    }

    @Test
    fun `guidInterpolatedStrings should handle single step`() {
        val start = "00000000-0000-0000-0000-000000000000"
        val end = "ffffffff-ffff-ffff-ffff-ffffffffffff"
        val result = guidInterpolatedStrings(start, end, 1)
        assertEquals(2, result.size)
        assertEquals(start, result[0])
    }

    @Test
    fun `guidInterpolatedStrings should handle zero steps`() {
        val start = "12345678-1234-1234-1234-123456789abc"
        val result = guidInterpolatedStrings(start, start, 0)
        assertEquals(1, result.size)
        assertEquals(start, result[0])
    }

    @Test
    fun `guidInterpolatedStrings should handle same start and end`() {
        val guid = "a1b2c3d4-e5f6-a1b2-c3d4-e5f6a1b2c3d4"
        val result = guidInterpolatedStrings(guid, guid, 5)
        assertEquals(6, result.size)
        result.forEach {
            assertEquals(guid, it, "All values should be the same when start equals end")
        }
    }

    @Test
    fun `guidInterpolatedStrings should handle lowercase GUIDs`() {
        val start = "abcdef00-1234-5678-9abc-def012345678"
        val end = "abcdef00-1234-5678-9abc-def012345679"
        val result = guidInterpolatedStrings(start, end, 3)
        assertEquals(4, result.size)
        assertEquals(start, result.first())
    }

    @Test
    fun `guidInterpolatedStrings should handle uppercase GUIDs`() {
        val start = "ABCDEF00-1234-5678-9ABC-DEF012345678"
        val end = "ABCDEF00-1234-5678-9ABC-DEF012345679"
        val result = guidInterpolatedStrings(start, end, 3)
        assertEquals(4, result.size)
        assertEquals(start, result.first())
    }

    @Test
    fun `guidInterpolatedStrings should handle mixed case GUIDs`() {
        val start = "AbCdEf00-1234-5678-9aBc-DeF012345678"
        val end = "AbCdEf00-1234-5678-9aBc-DeF012345679"
        val result = guidInterpolatedStrings(start, end, 3)
        assertEquals(4, result.size)
        assertEquals(start, result.first())
    }

    @Test
    fun `guidInterpolatedStrings should throw on invalid GUID character`() {
        assertThrows(IllegalArgumentException::class.java) {
            guidInterpolatedStrings(
                "GGGGGGGG-0000-0000-0000-000000000000",
                "ffffffff-ffff-ffff-ffff-ffffffffffff",
                2
            )
        }
    }

    @Test
    fun `guidInterpolatedStrings should throw on invalid character in start`() {
        assertThrows(IllegalArgumentException::class.java) {
            guidInterpolatedStrings("invalid!", "00000000-0000-0000-0000-000000000001", 2)
        }
    }

    @Test
    fun `guidInterpolatedStrings should throw on invalid character in end`() {
        assertThrows(IllegalArgumentException::class.java) {
            guidInterpolatedStrings("00000000-0000-0000-0000-000000000000", "invalid!", 2)
        }
    }

    @ParameterizedTest
    @CsvSource(
        "00000000-0000-0000-0000-000000000000, 11111111-1111-1111-1111-111111111111, 2",
        "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa, bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb, 4",
        "12345678-90ab-cdef-1234-567890abcdef, 12345678-90ab-cdef-1234-567890abcdf0, 3"
    )
    fun `guidInterpolatedStrings should generate expected number of results`(
        start: String,
        end: String,
        steps: Int
    ) {
        val result = guidInterpolatedStrings(start, end, steps)
        assertEquals(steps + 1, result.size)
    }

    @Test
    fun `guidInterpolatedStrings should preserve GUID format`() {
        val result =
            guidInterpolatedStrings(
                "00000000-0000-0000-0000-000000000000",
                "ffffffff-ffff-ffff-ffff-ffffffffffff",
                5
            )
        val guidPattern = Regex("^[0-9a-fA-F-]+$")
        result.forEach {
            assertTrue(
                guidPattern.matches(it),
                "Result should only contain valid GUID characters: $it"
            )
            assertEquals(36, it.length, "GUID should be 36 characters long")
        }
    }

    @Test
    fun `unicodeInterpolatedStrings and guidInterpolatedStrings should produce similar results for simple ASCII`() {
        // When both functions operate on simple ASCII GUID-compatible strings, they should both
        // produce
        // monotonically increasing sequences
        val start = "00000"
        val end = "11111"
        val steps = 5

        val unicodeResult = unicodeInterpolatedStrings(start, end, steps)
        val guidResult = guidInterpolatedStrings(start, end, steps)

        // Both should have the same length
        assertEquals(unicodeResult.size, guidResult.size)

        // Both should start with the same value
        assertEquals(start, unicodeResult.first())
        assertEquals(start, guidResult.first())

        // Both should be monotonically increasing
        for (i in 0 until unicodeResult.size - 1) {
            assertTrue(unicodeResult[i] <= unicodeResult[i + 1])
        }
        for (i in 0 until guidResult.size - 1) {
            assertTrue(guidResult[i] <= guidResult[i + 1])
        }
    }

    @Test
    fun `unicodeInterpolatedStrings should handle numeric strings`() {
        val result = unicodeInterpolatedStrings("0", "9", 9)
        assertEquals(10, result.size)
        assertEquals("0", result.first())
    }

    @Test
    fun `guidInterpolatedStrings should work with realistic UUID range`() {
        // Realistic scenario: splitting a UUID range for database partitioning
        val start = "550e8400-e29b-41d4-a716-446655440000"
        val end = "550e8400-e29b-41d4-a716-446655440100"
        val result = guidInterpolatedStrings(start, end, 4)

        assertEquals(5, result.size)
        assertEquals(start, result.first())

        // Verify all results are valid and increasing
        for (i in 0 until result.size - 1) {
            assertTrue(result[i] <= result[i + 1])
        }
    }

    @Test
    fun `unicodeInterpolatedStrings should distribute evenly across range`() {
        val result = unicodeInterpolatedStrings("a", "e", 4)
        assertEquals(5, result.size)

        // With uniform distribution, each step should advance roughly equally
        // (this is a rough check since the distribution may not be perfectly linear in all bases)
        assertTrue(result[0] < result[1])
        assertTrue(result[1] < result[2])
        assertTrue(result[2] < result[3])
        assertTrue(result[3] < result[4])
    }
}
