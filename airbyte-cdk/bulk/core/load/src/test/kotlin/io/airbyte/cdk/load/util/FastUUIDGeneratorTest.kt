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

internal class FastUUIDGeneratorTest {

    @Test
    fun testInsecureUuidGeneration() {
        val generator = FastUUIDGenerator()
        val uuid1 = generator.insecureUUID()
        assertNotNull(uuid1)
        val uuid2 = generator.insecureUUID()
        assertNotNull(uuid2)
        assertNotEquals(uuid1, uuid2)
    }

    @Test
    fun testRandomUuidGeneration() {
        val generator = FastUUIDGenerator()
        val uuid1 = generator.randomUUID()
        assertNotNull(uuid1)
        val uuid2 = generator.randomUUID()
        assertNotNull(uuid2)
        assertNotEquals(uuid1, uuid2)
    }

    @Test
    fun testPerformance() {
        val generator = FastUUIDGenerator()

        val fastTime = measureTime {
            @Suppress("unused")
            for (i in 0..100000) {
                generator.randomUUID()
            }
        }

        val uuidTime = measureTime {
            @Suppress("unused")
            for (i in 0..100000) {
                UUID.randomUUID()
            }
        }

        println("$fastTime < $uuidTime")
        assertTrue(fastTime < uuidTime)
    }
}
