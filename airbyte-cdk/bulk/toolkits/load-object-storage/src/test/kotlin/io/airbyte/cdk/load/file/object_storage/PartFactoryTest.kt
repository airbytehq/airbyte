/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.object_storage

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.withContext
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class PartFactoryTest {
    @Test
    fun `parts are generated in order and empty parts are skipped (empty final)`() {
        val factory = PartFactory("key", 1)
        val part1 = factory.nextPart(byteArrayOf(1))
        val part2 = factory.nextPart(null)
        val part3 = factory.nextPart(byteArrayOf(2))
        val part4 = factory.nextPart(null, isFinal = true)

        assert(part1.partIndex == 1)
        assert(!part1.isFinal)
        assert(!part1.isEmpty)

        assert(part2.partIndex == 1)
        assert(!part2.isFinal)
        assert(part2.isEmpty)

        assert(part3.partIndex == 2)
        assert(!part3.isFinal)
        assert(!part3.isEmpty)

        assert(part4.partIndex == 2)
        assert(part4.isFinal)
        assert(part4.isEmpty)

        // No more parts can be produced after the final part.
        assertThrows<IllegalStateException> { factory.nextPart(byteArrayOf(3)) }
    }

    @Test
    fun `parts are generated in order and empty parts are skipped (non-empty final)`() {
        val factory = PartFactory("key", 1)
        val part1 = factory.nextPart(byteArrayOf(1))
        val part2 = factory.nextPart(null)
        val part3 = factory.nextPart(byteArrayOf(2))
        val part4 = factory.nextPart(byteArrayOf(3), isFinal = true)

        assert(part1.partIndex == 1)
        assert(part2.partIndex == 1)
        assert(part3.partIndex == 2)

        assert(part4.partIndex == 3)
        assert(part4.isFinal)
        assert(!part4.isEmpty)
    }

    @Test
    fun `total size is calculated correctly`() {
        val factory = PartFactory("key", 1)
        factory.nextPart(byteArrayOf(1))
        factory.nextPart(null)
        factory.nextPart(byteArrayOf(2, 2))
        factory.nextPart(byteArrayOf(3, 3, 3), isFinal = true)

        assert(factory.totalSize == 6L)
    }

    @Test
    fun `test that assembler is not complete until all parts are seen`() {
        val factory = PartFactory("key", 1)
        val assembler = PartBookkeeper()

        repeat(10) {
            val part = factory.nextPart(byteArrayOf(it.toByte()), it == 9)
            assert(!assembler.isComplete)
            assembler.add(part)
        }

        assert(assembler.isComplete)
    }

    @Test
    fun `test assembler not complete until all are seen (out-of-order, gaps, and null final)`() {
        val factory = PartFactory("key", 1)
        val assembler = PartBookkeeper()

        val sortOrder = listOf(2, 1, 0, 9, 8, 7, 6, 4, 5, 3)
        val parts =
            (0 until 10).map {
                // Make a gap every 3rd part
                val bytes =
                    if (it % 3 == 0) {
                        null
                    } else {
                        byteArrayOf(it.toByte())
                    }

                // Last in list must be final
                factory.nextPart(bytes, it == 9)
            }

        val partsSorted = parts.zip(sortOrder).sortedBy { it.second }
        partsSorted.forEach { (part, sortIndex) ->
            if (sortIndex == 9) {
                // Because the last part was null, and the assembler already saw the final part
                // it *should* think it is complete.
                assert(assembler.isComplete)
            } else {
                assert(!assembler.isComplete)
            }
            assembler.add(part)
        }

        assert(assembler.isComplete)
    }

    @Test
    fun `test adding parts asynchronously`() = runTest {
        val factory = PartFactory("key", 1)
        val parts = (0 until 100000).map { factory.nextPart(byteArrayOf(it.toByte()), it == 99999) }
        val assembler = PartBookkeeper()
        val jobs = mutableListOf<Job>()
        withContext(Dispatchers.IO) {
            parts.shuffled(random = java.util.Random(0)).forEach {
                jobs.add(
                    launch {
                        assert(!assembler.isComplete)
                        assembler.add(it)
                    }
                )
            }
            jobs.forEach { it.join() }
        }
        assert(assembler.isComplete)
    }
}
