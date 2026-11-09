/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertNotSame
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Test

class PooledByteArrayOutputStreamTest {
    /** Larger than any slab other tests leave in the shared pool. */
    private val slabSize = 7 * 1024 * 1024 + 13

    private fun drainPool() {
        do {
            val borrowed = ByteArrayPool.borrow(0)
        } while (borrowed.isNotEmpty())
    }

    @Test
    fun `a buffer takes a slab from the pool for the parts after the first`() {
        drainPool()
        val slab = ByteArray(slabSize)
        ByteArrayPool.recycle(slab)

        val stream = PooledByteArrayOutputStream()
        stream.write(byteArrayOf(1, 2, 3))
        assertArrayEquals(byteArrayOf(1, 2, 3), stream.extractBytes())

        stream.resetBuffer()
        stream.write(byteArrayOf(4))
        assertArrayEquals(byteArrayOf(4), stream.extractBytes())

        // The reset took the slab and recycled the first part's array.
        val next = ByteArrayPool.borrow(slabSize)
        assertNotSame(slab, next)
        drainPool()
    }

    @Test
    fun `a new buffer does not take a slab`() {
        drainPool()
        val slab = ByteArray(slabSize)
        ByteArrayPool.recycle(slab)

        PooledByteArrayOutputStream().write(byteArrayOf(1))

        assertSame(slab, ByteArrayPool.borrow(slabSize))
        drainPool()
    }
}
