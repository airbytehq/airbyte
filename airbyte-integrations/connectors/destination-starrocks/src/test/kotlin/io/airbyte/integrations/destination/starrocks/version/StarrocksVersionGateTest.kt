/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.version

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class StarrocksVersionGateTest {

    @Test
    fun `parses plain and suffixed version strings`() {
        assertEquals("3.3.11", StarrocksVersionGate.parse("3.3.11").toString())
        // current_version() can return extra build info after the semver
        assertEquals("4.1.1", StarrocksVersionGate.parse("4.1.1 e8a3a2c").toString())
        assertEquals("3.5.4", StarrocksVersionGate.parse("StarRocks-3.5.4").toString())
    }

    @Test
    fun `rejects non-version strings`() {
        assertThrows<IllegalArgumentException> { StarrocksVersionGate.parse("not-a-version") }
    }

    @Test
    fun `compression capability turns on at 3_3_2`() {
        assertFalse(StarrocksVersionGate.capabilities("3.3.1").compression)
        assertTrue(StarrocksVersionGate.capabilities("3.3.2").compression)
        assertTrue(StarrocksVersionGate.capabilities("3.3.11").compression)
        assertTrue(StarrocksVersionGate.capabilities("4.1.1").compression)
    }

    @Test
    fun `validate rejects versions below the 3_3 floor`() {
        assertThrows<IllegalStateException> { StarrocksVersionGate.validate("3.2.9") }
        assertThrows<IllegalStateException> { StarrocksVersionGate.validate("3.1.0") }
        assertThrows<IllegalStateException> { StarrocksVersionGate.validate("2.5.0") }
    }

    @Test
    fun `validate accepts the 3_3 floor and newer`() {
        StarrocksVersionGate.validate("3.3.0")
        StarrocksVersionGate.validate("3.3.11")
        StarrocksVersionGate.validate("4.1.1")
    }
}
