/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.copy

import java.io.IOException
import java.nio.file.Files
import java.nio.file.Path
import java.util.concurrent.Callable
import java.util.concurrent.CyclicBarrier
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.awaitCancellation
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.io.TempDir

@Timeout(15)
class StandardInsertArchiveBatchTest {
    @TempDir lateinit var directory: Path

    private val retained = mutableListOf<Pair<Path, Throwable>>()

    private fun manager(maxBatchBytes: Long = 1L shl 30, maxTotalBytes: Long = 4L shl 30) =
        StandardInsertSpoolManager(
            directory,
            maxBatchBytes,
            maxTotalBytes,
            hasActiveReader = { failure ->
                generateSequence(failure) { it.cause }.any { it is ActiveReaderFailure }
            },
            onRetained = { path, failure -> retained.add(path to failure) },
        )

    private fun paths(): List<Path> = Files.list(directory).use { it.toList() }

    private fun StandardInsertSpoolManager.unfinished() = create { _, _, _ ->
        error("Unexpected upload")
    }

    @Test
    fun `lazily spools exact raw bytes and independent input and loaded counts`() = runBlocking {
        val first = "{ \"id\": 1 }\r\n".toByteArray()
        val second = byteArrayOf(0, 0xff.toByte(), 10)
        var calls = 0
        manager().use { manager ->
            val batch =
                manager.create { path, inputCount, loadedCount ->
                    calls++
                    assertTrue(path.fileName.toString().endsWith(".jsonl"))
                    assertArrayEquals(first + second, Files.readAllBytes(path))
                    assertEquals(2L, inputCount)
                    assertEquals(1L, loadedCount)
                }
            assertTrue(paths().isEmpty())
            batch.append(first)
            batch.append(second)
            assertEquals(1, paths().size)
            batch.complete(1)
            batch.complete(1)
            assertEquals(1, calls)
            assertTrue(paths().isEmpty())
            assertThrows<IllegalArgumentException> { batch.append(first) }
            batch.close()
            batch.close()
            assertThrows<IllegalArgumentException> { batch.complete(1) }
        }
        assertTrue(retained.isEmpty())
    }

    @Test
    fun `empty finish creates no file and uploads nothing`() = runBlocking {
        manager().use { manager ->
            val batch = manager.unfinished()
            batch.complete(0)
            batch.complete(0)
            batch.close()
            assertTrue(paths().isEmpty())
        }
    }

    @Test
    fun `zero byte append still counts as an input record`() = runBlocking {
        var calls = 0
        manager().use { manager ->
            val batch =
                manager.create { path, inputCount, loadedCount ->
                    calls++
                    assertEquals(0L, Files.size(path))
                    assertEquals(1L, inputCount)
                    assertEquals(0L, loadedCount)
                }
            batch.append(byteArrayOf())
            batch.complete(0)
        }
        assertEquals(1, calls)
        assertTrue(paths().isEmpty())
    }

    @Test
    fun `rejects invalid bounds and loaded counts with Fusion messages`() = runBlocking {
        for (bounds in listOf(0L to 1L, 1L to 0L, -1L to 1L, 1L to -1L)) {
            val failure =
                assertThrows<IllegalArgumentException> { manager(bounds.first, bounds.second) }
            assertTrue(failure.message!!.contains("Fusion"))
        }
        manager().use { manager ->
            for (loadedCount in listOf(-1L, 1L)) {
                val batch = manager.unfinished()
                val failure = assertThrows<IllegalArgumentException> { batch.complete(loadedCount) }
                assertTrue(failure.message!!.contains("Fusion"))
                assertThrows<IllegalArgumentException> { batch.complete(0) }
                assertThrows<IllegalArgumentException> { batch.append(byteArrayOf()) }
            }
            val batch = manager.unfinished()
            batch.append(byteArrayOf(1))
            assertThrows<IllegalArgumentException> { batch.complete(-1) }
            assertTrue(paths().isEmpty())
        }
    }

    @Test
    fun `batch overflow fails immediately deletes previous bytes and releases budget`() =
        runBlocking {
            manager(maxBatchBytes = 4, maxTotalBytes = 4).use { manager ->
                val batch = manager.unfinished()
                batch.append(ByteArray(4))
                val failure =
                    assertThrows<IllegalArgumentException> { batch.append(byteArrayOf(1)) }
                assertTrue(failure.message!!.contains("Fusion"))
                assertTrue(failure.message!!.contains("maxBatchBytes (4)"))
                assertTrue(paths().isEmpty())
                assertThrows<IllegalArgumentException> { batch.append(byteArrayOf()) }
                assertThrows<IllegalArgumentException> { batch.complete(1) }
                manager.unfinished().use { it.append(ByteArray(4)) }
            }
        }

    @Test
    fun `aggregate overflow releases only failed batch and permits reuse after deletion`() =
        runBlocking {
            manager(maxBatchBytes = 8, maxTotalBytes = 6).use { manager ->
                val first = manager.unfinished()
                val second = manager.unfinished()
                first.append(ByteArray(4))
                val firstPath = paths().single()
                second.append(ByteArray(2))
                val failure =
                    assertThrows<IllegalArgumentException> { second.append(byteArrayOf(1)) }
                assertTrue(failure.message!!.contains("maxTotalBytes (6)"))
                assertEquals(listOf(firstPath), paths())
                manager.unfinished().use { it.append(ByteArray(2)) }
                first.close()
                manager.unfinished().use { it.append(ByteArray(6)) }
                assertTrue(paths().isEmpty())
            }
        }

    @Test
    fun `oversized first append never allocates a spool`() {
        manager(maxBatchBytes = 1).use { manager ->
            val batch = manager.unfinished()
            assertThrows<IllegalArgumentException> { batch.append(ByteArray(2)) }
            assertTrue(paths().isEmpty())
        }
    }

    @Test
    fun `eight interleaved spools accept records without transfer permits`() = runBlocking {
        manager(maxBatchBytes = 3, maxTotalBytes = 24).use { manager ->
            var uploads = 0
            val batches =
                List(8) { index ->
                    manager.create { path, inputCount, loadedCount ->
                        uploads++
                        assertArrayEquals(ByteArray(3) { index.toByte() }, Files.readAllBytes(path))
                        assertEquals(3L, inputCount)
                        assertEquals(3L, loadedCount)
                    }
                }
            repeat(3) {
                batches.forEachIndexed { index, batch -> batch.append(byteArrayOf(index.toByte())) }
            }
            assertEquals(8, paths().size)
            batches.forEach { it.complete(3) }
            assertEquals(8, uploads)
            assertTrue(paths().isEmpty())
            manager.unfinished().use { it.append(ByteArray(3)) }
        }
    }

    @Test
    fun `active upload freezes spool and keeps budget until callback returns`() = runBlocking {
        val entered = CompletableDeferred<Path>()
        val release = CompletableDeferred<Unit>()
        manager(maxBatchBytes = 6, maxTotalBytes = 6).use { manager ->
            val batch =
                manager.create { path, _, _ ->
                    entered.complete(path)
                    release.await()
                    assertEquals(6L, Files.size(path))
                }
            batch.append(ByteArray(6))
            val upload = launch {
                val failure = assertThrows<IllegalArgumentException> { batch.complete(1) }
                assertTrue(failure.message!!.contains("closed"))
            }
            try {
                val path = entered.await()
                assertThrows<IllegalArgumentException> { batch.append(byteArrayOf(1)) }
                assertThrows<IllegalArgumentException> { batch.complete(1) }
                assertThrows<IllegalArgumentException> {
                    manager.unfinished().append(byteArrayOf(1))
                }
                batch.close()
                batch.close()
                assertTrue(Files.exists(path))
            } finally {
                release.complete(Unit)
                upload.join()
            }
            assertTrue(paths().isEmpty())
            manager.unfinished().use { it.append(ByteArray(6)) }
        }
    }

    @Test
    fun `manager close preserves successful or failing active callbacks and deletes incomplete files`() =
        runBlocking {
            for (failure in listOf(null, IOException("upload failed"))) {
                val manager = manager()
                val entered = CompletableDeferred<Path>()
                val release = CompletableDeferred<Unit>()
                val batch =
                    manager.create { path, _, _ ->
                        entered.complete(path)
                        release.await()
                        assertTrue(Files.exists(path))
                        if (failure != null) throw failure
                    }
                batch.append(byteArrayOf(1))
                val incomplete = manager.unfinished().also { it.append(byteArrayOf(2)) }
                val upload = launch {
                    if (failure == null) {
                        val closed = assertThrows<IllegalArgumentException> { batch.complete(1) }
                        assertTrue(closed.message!!.contains("closed"))
                    } else assertSame(failure, assertThrows<IOException> { batch.complete(1) })
                }
                try {
                    val path = entered.await()
                    manager.close()
                    manager.close()
                    assertEquals(listOf(path), paths())
                    assertThrows<IllegalArgumentException> { manager.unfinished() }
                    assertThrows<IllegalArgumentException> { incomplete.append(byteArrayOf(1)) }
                    assertThrows<IllegalArgumentException> { incomplete.complete(1) }
                    assertThrows<IllegalArgumentException> { batch.complete(1) }
                } finally {
                    release.complete(Unit)
                    upload.join()
                    manager.close()
                }
                assertTrue(paths().isEmpty())
            }
            assertTrue(retained.isEmpty())
        }

    @Test
    fun `cancellation and close preserve file until callback reader finally stops`() = runBlocking {
        val manager = manager(maxBatchBytes = 4, maxTotalBytes = 4)
        val entered = CompletableDeferred<Path>()
        val draining = CompletableDeferred<Unit>()
        val release = CompletableDeferred<Unit>()
        val batch =
            manager.create { path, _, _ ->
                Files.newInputStream(path).use { input ->
                    entered.complete(path)
                    try {
                        awaitCancellation()
                    } finally {
                        withContext(NonCancellable) {
                            draining.complete(Unit)
                            release.await()
                            assertTrue(Files.exists(path))
                            assertEquals(4, input.readAllBytes().size)
                        }
                    }
                }
            }
        batch.append(ByteArray(4))
        var observed: Throwable? = null
        val upload = launch {
            try {
                batch.complete(1)
            } catch (failure: Throwable) {
                observed = failure
                throw failure
            }
        }
        try {
            val path = entered.await()
            upload.cancel()
            draining.await()
            assertThrows<IllegalArgumentException> { manager.unfinished().append(byteArrayOf(1)) }
            batch.close()
            manager.close()
            assertTrue(Files.exists(path))
        } finally {
            release.complete(Unit)
            upload.join()
            manager.close()
        }
        assertTrue(observed is CancellationException)
        assertTrue(paths().isEmpty())
        assertTrue(retained.isEmpty())
    }

    @Test
    fun `upload failure is preserved deletes spool releases budget and rejects retries`() =
        runBlocking {
            manager(maxBatchBytes = 4, maxTotalBytes = 4).use { manager ->
                val failure = IOException("upload failed")
                val batch = manager.create { _, _, _ -> throw failure }
                batch.append(ByteArray(4))
                assertSame(failure, assertThrows<IOException> { batch.complete(1) })
                assertTrue(paths().isEmpty())
                assertThrows<IllegalArgumentException> { batch.complete(1) }
                assertThrows<IllegalArgumentException> { batch.append(byteArrayOf(1)) }
                batch.close()
                batch.close()
                manager.unfinished().use { it.append(ByteArray(4)) }
            }
        }

    @Test
    fun `wrapped active reader failure retains bytes and budget even after close`() = runBlocking {
        val manager = manager(maxBatchBytes = 4, maxTotalBytes = 4)
        val failure = IOException("wrapped", ActiveReaderFailure())
        val batch = manager.create { _, _, _ -> throw failure }
        batch.append(ByteArray(4))
        val path = paths().single()
        assertSame(failure, assertThrows<IOException> { batch.complete(1) })
        assertEquals(listOf(path to failure), retained)
        assertEquals(4L, Files.size(path))
        assertThrows<IllegalArgumentException> { manager.unfinished().append(byteArrayOf(1)) }
        assertThrows<IllegalArgumentException> { batch.complete(1) }
        batch.close()
        manager.close()
        manager.close()
        assertTrue(Files.exists(path))
        assertEquals(1, retained.size)
    }

    @Test
    fun `append reopens file so missing spool fails and releases reservation`() = runBlocking {
        manager(maxBatchBytes = 4, maxTotalBytes = 4).use { manager ->
            val batch = manager.unfinished()
            batch.append(ByteArray(2))
            Files.delete(paths().single())
            assertThrows<IOException> { batch.append(ByteArray(2)) }
            assertTrue(paths().isEmpty())
            assertThrows<IllegalArgumentException> { batch.complete(1) }
            assertThrows<IllegalArgumentException> { batch.append(byteArrayOf()) }
            batch.close()
            batch.close()
            manager.unfinished().use { it.append(ByteArray(4)) }
        }
    }

    @Test
    fun `file allocation failure fails batch without leaking budget`() = runBlocking {
        Files.delete(directory)
        manager(maxBatchBytes = 4, maxTotalBytes = 4).use { manager ->
            val batch = manager.unfinished()
            assertThrows<IOException> { batch.append(ByteArray(4)) }
            assertThrows<IllegalArgumentException> { batch.complete(1) }
            Files.createDirectory(directory)
            manager.unfinished().use { it.append(ByteArray(4)) }
        }
        assertTrue(paths().isEmpty())
    }

    @Test
    fun `failed deletion and reporting cannot mask upload error or release budget`() = runBlocking {
        val failure = IOException("original upload error")
        val reportingFailure = IllegalStateException("reporting failed")
        val manager =
            StandardInsertSpoolManager(
                directory,
                4,
                4,
                hasActiveReader = { false },
                onRetained = { path, error ->
                    retained.add(path to error)
                    throw reportingFailure
                },
            )
        val batch =
            manager.create { path, _, _ ->
                replaceWithNonemptyDirectory(path)
                throw failure
            }
        batch.append(ByteArray(4))
        val path = paths().single()
        assertSame(failure, assertThrows<IOException> { batch.complete(1) })
        assertEquals(listOf(path to failure), retained)
        assertTrue(failure.suppressed.any { it is IOException })
        assertTrue(failure.suppressed.any { it === reportingFailure })
        assertThrows<IllegalArgumentException> { manager.unfinished().append(byteArrayOf(1)) }
        batch.close()
        manager.close()
        assertTrue(Files.exists(path))
        assertEquals(1, retained.size)
    }

    @Test
    fun `successful upload with failed deletion fails completion and holds budget`() = runBlocking {
        manager(maxBatchBytes = 4, maxTotalBytes = 4).use { manager ->
            var uploads = 0
            val batch =
                manager.create { path, _, _ ->
                    uploads++
                    replaceWithNonemptyDirectory(path)
                }
            batch.append(ByteArray(4))
            val path = paths().single()
            val failure = assertThrows<IOException> { batch.complete(1) }
            assertEquals(listOf(path to failure), retained)
            assertThrows<IllegalArgumentException> { batch.complete(1) }
            assertThrows<IllegalArgumentException> { batch.append(byteArrayOf()) }
            assertThrows<IllegalArgumentException> { manager.unfinished().append(byteArrayOf(1)) }
            batch.close()
            assertEquals(1, uploads)
            assertTrue(Files.exists(path))
        }
    }

    @Test
    fun `batch close propagates deletion error once and reporting cannot replace it`() {
        val reportingFailure = IllegalStateException("report failed")
        val manager =
            StandardInsertSpoolManager(
                directory,
                hasActiveReader = { false },
                onRetained = { path, failure ->
                    retained.add(path to failure)
                    throw reportingFailure
                },
            )
        val batch = manager.unfinished()
        batch.append(byteArrayOf(1))
        val path = paths().single()
        replaceWithNonemptyDirectory(path)
        val failure = assertThrows<IOException> { batch.close() }
        assertEquals(listOf(path to failure), retained)
        assertTrue(failure.suppressed.any { it === reportingFailure })
        batch.close()
        manager.close()
        assertEquals(1, retained.size)
    }

    @Test
    fun `append IO failure with failed deletion retains full reservation`() {
        manager(maxBatchBytes = 4, maxTotalBytes = 4).use { manager ->
            val batch = manager.unfinished()
            batch.append(ByteArray(2))
            val path = paths().single()
            replaceWithNonemptyDirectory(path)
            val failure = assertThrows<IOException> { batch.append(ByteArray(2)) }
            assertEquals(listOf(path to failure), retained)
            assertTrue(failure.suppressed.any { it is IOException })
            assertThrows<IllegalArgumentException> { manager.unfinished().append(byteArrayOf(1)) }
            batch.close()
            batch.close()
            assertEquals(1, retained.size)
        }
    }

    @Test
    fun `manager close aggregates deletion errors once and still cleans remaining batches`() {
        val manager = manager()
        manager.unfinished().append(byteArrayOf(1))
        val path = paths().single()
        replaceWithNonemptyDirectory(path)
        manager.unfinished().append(byteArrayOf(2))
        val secondPath = paths().single { it != path }
        replaceWithNonemptyDirectory(secondPath)
        manager.unfinished().append(byteArrayOf(3))
        val failure = assertThrows<IOException> { manager.close() }
        assertEquals(1, failure.suppressed.size)
        assertTrue(failure.suppressed.single() is IOException)
        manager.close()
        assertEquals(setOf(path, secondPath), paths().toSet())
        assertEquals(setOf(path, secondPath), retained.map { it.first }.toSet())
        assertSame(failure, retained.first().second)
        assertSame(failure.suppressed.single(), retained.last().second)
    }

    @Test
    fun `manager close racing create append and complete never leaks or unlinks active callback`() {
        val executor = Executors.newFixedThreadPool(3)
        try {
            repeat(100) {
                val manager = manager()
                val barrier = CyclicBarrier(3)
                val results =
                    executor.invokeAll(
                        listOf(
                            Callable {
                                barrier.await()
                                try {
                                    val batch =
                                        manager.create { path, _, _ ->
                                            repeat(10) {
                                                assertTrue(Files.exists(path))
                                                Thread.yield()
                                            }
                                        }
                                    batch.append(byteArrayOf(1))
                                    runBlocking { batch.complete(1) }
                                } catch (failure: IllegalArgumentException) {
                                    assertTrue(failure.message!!.contains("Fusion"))
                                }
                            },
                            Callable {
                                barrier.await()
                                try {
                                    manager.unfinished().append(byteArrayOf(2))
                                } catch (failure: IllegalArgumentException) {
                                    assertTrue(failure.message!!.contains("Fusion"))
                                }
                            },
                            Callable {
                                barrier.await()
                                manager.close()
                            },
                        )
                    )
                results.forEach { it.get(5, TimeUnit.SECONDS) }
                manager.close()
                assertTrue(paths().isEmpty())
            }
        } finally {
            executor.shutdownNow()
        }
        assertTrue(retained.isEmpty())
    }

    private fun replaceWithNonemptyDirectory(path: Path) {
        Files.delete(path)
        Files.createDirectory(path)
        Files.write(path.resolve("prevent-delete"), byteArrayOf(1))
    }

    private class ActiveReaderFailure : IllegalStateException("Reader is still active")
}
