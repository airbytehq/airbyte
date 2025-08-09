/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.util

import java.util.UUID
import kotlin.time.measureTime
import org.junit.jupiter.api.Assertions.assertNotEquals
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

internal class UUIDGeneratorTest {

    @Test
    fun testV4UuidGeneration() {
        val generator = UUIDGenerator()
        val uuid1 = generator.v4()
        assertNotNull(uuid1)
        val uuid2 = generator.v4()
        assertNotNull(uuid2)
        assertNotEquals(uuid1, uuid2)
    }

    @Test
    fun testV7Generation() {
        val generator = UUIDGenerator()
        val uuid1 = generator.v7()
        assertNotNull(uuid1)
        val uuid2 = generator.v7()
        assertNotNull(uuid2)
        assertNotEquals(uuid1, uuid2)
    }

    @Test
    fun testV4Performance() {
        val generator = UUIDGenerator()

        val fastTime = measureTime {
            @Suppress("unused")
            for (i in 0..100000) {
                generator.v4()
            }
        }

        val uuidTime = measureTime {
            @Suppress("unused")
            for (i in 0..100000) {
                UUID.randomUUID()
            }
        }

        assertTrue(fastTime < uuidTime)
    }

    @Test
    fun testV7Performance() {
        val generator = UUIDGenerator()

        val fastTime = measureTime {
            @Suppress("unused")
            for (i in 0..100000) {
                generator.v7()
            }
        }

        val uuidTime = measureTime {
            @Suppress("unused")
            for (i in 0..100000) {
                UUID.randomUUID()
            }
        }

        assertTrue(fastTime < uuidTime)
    }
}
