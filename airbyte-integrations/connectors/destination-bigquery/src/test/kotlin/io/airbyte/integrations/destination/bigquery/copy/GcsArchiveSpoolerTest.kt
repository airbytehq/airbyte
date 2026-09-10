/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.copy

import io.airbyte.cdk.load.file.gcs.GcsBlob
import io.airbyte.cdk.load.file.gcs.GcsClient
import io.mockk.mockk
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.FileNotFoundException
import java.io.IOException
import java.io.InputStream
import java.nio.file.Files
import java.nio.file.Path
import java.util.concurrent.CountDownLatch
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicReference
import java.util.zip.GZIPOutputStream
import kotlin.random.Random
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.TimeoutCancellationException
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import org.junit.jupiter.api.Assertions.assertArrayEquals
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertSame
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.io.TempDir

@Timeout(15)
class GcsArchiveSpoolerTest {
    @TempDir lateinit var directory: Path

    private val blob = GcsBlob("staging/archive.csv.gz", mockk())

    @Test
    fun `copies raw gzip bytes using at most a 64 KiB read buffer`() = runBlocking {
        val compressed = ByteArrayOutputStream()
        GZIPOutputStream(compressed).use { it.write(Random(123).nextBytes(200_000)) }
        val bytes = compressed.toByteArray()
        val largestRead = AtomicInteger()
        val input =
            object : ByteArrayInputStream(bytes) {
                override fun read(target: ByteArray, offset: Int, length: Int): Int {
                    largestRead.accumulateAndGet(length, ::maxOf)
                    return super.read(target, offset, length)
                }
            }
        val client = Client { input }
        val path = path()
        GcsArchiveSpooler(maxBytes = bytes.size.toLong()).use {
            assertEquals(bytes.size.toLong(), it.download(client, blob, path))
        }
        assertArrayEquals(bytes, Files.readAllBytes(path))
        assertEquals(64 * 1024, largestRead.get())
        assertEquals(1, client.attempts.get())
        assertEquals(blob.key, client.key.get())
    }

    @Test
    fun `accepts magic split across reads without parsing gzip`() = runBlocking {
        val bytes = byteArrayOf(0x1f, 0x8b.toByte(), 42)
        val client = Client {
            object : ByteArrayInputStream(bytes) {
                override fun read(target: ByteArray, offset: Int, length: Int): Int =
                    super.read(target, offset, minOf(length, 1))
            }
        }
        val path = path()
        GcsArchiveSpooler().use { assertEquals(3L, it.download(client, blob, path)) }
        assertArrayEquals(bytes, Files.readAllBytes(path))
    }

    @Test
    fun `rejects decoded empty and truncated magic without retry`() = runBlocking {
        GcsArchiveSpooler().use { spooler ->
            for (bytes in listOf("decoded,csv\n".toByteArray(), byteArrayOf(), byteArrayOf(0x1f))) {
                val client = Client { ByteArrayInputStream(bytes) }
                val path = path()
                val error =
                    assertThrows<IllegalStateException> { spooler.download(client, blob, path) }
                assertTrue(error.message!!.contains("gzip magic"))
                assertEquals(1, client.attempts.get())
                assertTrue(Files.exists(path))
            }
        }
    }

    @Test
    fun `retries a partial IOException from the start without append or stale tail`() =
        runBlocking {
            val partial = gzipBytes(500)
            val complete = gzipBytes(20)
            val firstClosed = CountDownLatch(1)
            val path = path()
            Files.write(path, ByteArray(1000))
            val client = Client { attempt ->
                assertEquals(0L, Files.size(path), "Truncate before each GET")
                if (attempt == 1) {
                    object : ByteArrayInputStream(partial) {
                        override fun read(target: ByteArray, offset: Int, length: Int): Int {
                            if (available() == 0)
                                throw IOException("connection reset after partial body")
                            return super.read(target, offset, length)
                        }

                        override fun close() = firstClosed.countDown()
                    }
                } else {
                    assertEquals(0L, firstClosed.count, "Prior reader must close before retry")
                    ByteArrayInputStream(complete)
                }
            }
            GcsArchiveSpooler().use { assertEquals(20L, it.download(client, blob, path)) }
            assertEquals(2, client.attempts.get())
            assertArrayEquals(complete, Files.readAllBytes(path))
        }

    @Test
    fun `limits transient IO failures to three attempts and truncates before failed GET`() =
        runBlocking {
            val path = path()
            val failure = IOException("transient GET failure")
            val client = Client { attempt ->
                assertEquals(0L, Files.size(path))
                if (attempt == 1) {
                    object : ByteArrayInputStream(gzipBytes(20)) {
                        override fun read(target: ByteArray, offset: Int, length: Int): Int {
                            if (available() == 0) throw failure
                            return super.read(target, offset, length)
                        }
                    }
                } else throw failure
            }
            GcsArchiveSpooler().use {
                val error = assertThrows<IOException> { it.download(client, blob, path) }
                assertEquals(failure.javaClass, error.javaClass)
                assertEquals(failure.message, error.message)
            }
            assertEquals(3, client.attempts.get())
            assertEquals(0L, Files.size(path))
        }

    @Test
    fun `fails before writing beyond the byte cap and does not retry`() = runBlocking {
        val path = path()
        val client = Client { ByteArrayInputStream(gzipBytes(100_000)) }
        GcsArchiveSpooler(maxBytes = 66_000).use {
            val error = assertThrows<IllegalStateException> { it.download(client, blob, path) }
            assertTrue(error.message!!.contains("maxBytes (66000)"))
        }
        assertEquals(1, client.attempts.get())
        assertEquals(65_536L, Files.size(path))
    }

    @Test
    fun `does not retry permanent IO or non IO failures`() = runBlocking {
        for (failure in
            listOf(FileNotFoundException("missing"), IllegalArgumentException("bad request"))) {
            val client = Client { throw failure }
            GcsArchiveSpooler().use {
                val error = assertThrows<Exception> { it.download(client, blob, path()) }
                assertEquals(failure.javaClass, error.javaClass)
                assertEquals(failure.message, error.message)
            }
            assertEquals(1, client.attempts.get())
        }
    }

    @Test
    fun `does not create caller path or retry local file failures`() = runBlocking {
        val missing = directory.resolve("caller-did-not-create")
        val client = Client { ByteArrayInputStream(gzipBytes(20)) }
        GcsArchiveSpooler().use { assertThrows<IOException> { it.download(client, blob, missing) } }
        assertEquals(0, client.attempts.get())
        assertFalse(Files.exists(missing))
    }

    @Test
    fun `one timeout covers all retry attempts`() = runBlocking {
        val client = Client { attempt ->
            delay(300)
            if (attempt == 1) throw IOException("retry")
            ByteArrayInputStream(gzipBytes(20))
        }
        GcsArchiveSpooler(downloadTimeoutMillis = 500, cleanupTimeoutMillis = 1000).use {
            assertThrows<TimeoutCancellationException> { it.download(client, blob, path()) }
        }
        assertEquals(2, client.attempts.get())
    }

    @Test
    fun `timeout interrupts and closes blocking read before returning`() = runBlocking {
        val input = BlockingInput(closeReleasesRead = true)
        val client = Client { input }
        val spooler = GcsArchiveSpooler(downloadTimeoutMillis = 500, cleanupTimeoutMillis = 1000)
        try {
            assertThrows<TimeoutCancellationException> { spooler.download(client, blob, path()) }
            assertEquals(0L, input.entered.count)
            assertEquals(0L, input.interrupted.count)
            assertEquals(0L, input.exited.count)
            assertEquals(0L, input.closeEntered.count)
            assertEquals(1, client.attempts.get())
        } finally {
            input.release()
            spooler.close()
        }
    }

    @Test
    fun `cancellation waits for actual reader exit before propagating`() = runBlocking {
        val input = BlockingInput(closeReleasesRead = true)
        val path = path()
        val spooler = GcsArchiveSpooler(cleanupTimeoutMillis = 1000)
        val observed = CompletableDeferred<Throwable>()
        val download = launch {
            try {
                spooler.download(Client { input }, blob, path)
            } catch (e: Throwable) {
                observed.complete(e)
            }
        }
        try {
            input.entered.awaitSuspending()
            download.cancel()
            assertTrue(withTimeout(5000) { observed.await() } is CancellationException)
            download.join()
            assertEquals(0L, input.exited.count)
            assertTrue(Files.exists(path))
        } finally {
            input.release()
            download.cancel()
            download.join()
            spooler.close()
        }
    }

    @Test
    fun `cancelled future does not hide an active reader or blocked close`() = runBlocking {
        assertActiveReaderIsRetained(offThread = false)
    }

    @Test
    fun `tracks reader when client moves callback off worker thread`() = runBlocking {
        assertActiveReaderIsRetained(offThread = true)
    }

    private suspend fun assertActiveReaderIsRetained(offThread: Boolean) =
        kotlinx.coroutines.coroutineScope {
            val input = BlockingInput(blockClose = true)
            val client = Client(offThread) { input }
            val path = path()
            val spooler = GcsArchiveSpooler(cleanupTimeoutMillis = 100)
            val observed = CompletableDeferred<Throwable>()
            val download = launch {
                try {
                    spooler.download(client, blob, path)
                } catch (e: Throwable) {
                    observed.complete(e)
                }
            }
            try {
                input.entered.awaitSuspending()
                download.cancel()
                val error = withTimeout(5000) { observed.await() }
                assertTrue(error is GcsArchiveReaderStillActiveException)
                assertEquals(path, (error as GcsArchiveReaderStillActiveException).path)
                assertTrue(error.cause is CancellationException)
                assertEquals(1L, input.exited.count, "Reader is still inside InputStream.read")
                assertEquals(1L, input.closeExited.count, "close is also still blocked")
                assertTrue(Files.exists(path))
                assertSame(
                    error,
                    assertThrows<GcsArchiveReaderStillActiveException> {
                        spooler.download(client, blob, path())
                    },
                )
                assertEquals(
                    1,
                    client.attempts.get(),
                    "Poisoned spooler must not start another reader",
                )
            } finally {
                input.release()
                download.cancel()
                download.join()
                input.exited.awaitSuspending()
                input.closeExited.awaitSuspending()
                spooler.close()
            }
        }

    @Test
    fun `parent close drains downloads is idempotent and rejects new work`(): Unit = runBlocking {
        val input = BlockingInput(closeReleasesRead = true)
        val spooler = GcsArchiveSpooler(cleanupTimeoutMillis = 1000)
        val observed = CompletableDeferred<Throwable>()
        val download = launch {
            try {
                spooler.download(Client { input }, blob, path())
            } catch (e: Throwable) {
                observed.complete(e)
            }
        }
        try {
            input.entered.awaitSuspending()
            withContext(Dispatchers.IO) { spooler.close() }
            assertTrue(withTimeout(5000) { observed.await() } is CancellationException)
            assertEquals(0L, input.exited.count)
            spooler.close()
            assertThrows<IllegalStateException> { spooler.download(Client { input }, blob, path()) }
        } finally {
            input.release()
            download.cancel()
            download.join()
            spooler.close()
        }
    }

    @Test
    fun `four daemon workers bound concurrent reads and reject a fifth`() = runBlocking {
        val inputs = List(4) { BlockingInput(closeReleasesRead = true) }
        val spooler = GcsArchiveSpooler(cleanupTimeoutMillis = 1000)
        val downloads =
            inputs.map { input -> launch { spooler.download(Client { input }, blob, path()) } }
        try {
            inputs.forEach { it.entered.awaitSuspending() }
            val threads = inputs.map { it.thread.get() }
            assertEquals(4, threads.toSet().size)
            assertTrue(threads.all { it.isDaemon && it.name.startsWith("gcs-archive-reader-") })
            val fifth = Client { ByteArrayInputStream(gzipBytes(20)) }
            assertThrows<IllegalStateException> { spooler.download(fifth, blob, path()) }
            assertEquals(0, fifth.attempts.get())
        } finally {
            inputs.forEach { it.release() }
            downloads.forEach { it.cancel() }
            downloads.forEach { it.join() }
            spooler.close()
        }
    }

    private fun path(): Path = Files.createTempFile(directory, "archive-", ".csv.gz")

    private fun gzipBytes(size: Int): ByteArray =
        ByteArray(size) { it.toByte() }
            .apply {
                this[0] = 0x1f
                this[1] = 0x8b.toByte()
            }

    private class Client(
        private val offThread: Boolean = false,
        private val response: suspend (Int) -> InputStream,
    ) : GcsClient by mockk() {
        val attempts = AtomicInteger()
        val key = AtomicReference<String>()

        override suspend fun <U> get(key: String, block: (InputStream) -> U): U {
            this.key.set(key)
            val input = response(attempts.incrementAndGet())
            return if (offThread) withContext(Dispatchers.IO) { block(input) } else block(input)
        }
    }

    /** A real blocking read which ignores interruption; release every instance in test finally. */
    private class BlockingInput(
        private val closeReleasesRead: Boolean = false,
        private val blockClose: Boolean = false,
    ) : InputStream() {
        val entered = CountDownLatch(1)
        val exited = CountDownLatch(1)
        val interrupted = CountDownLatch(1)
        val closeEntered = CountDownLatch(1)
        val closeExited = CountDownLatch(1)
        val thread = AtomicReference<Thread>()
        private val releaseRead = CountDownLatch(1)
        private val releaseClose = CountDownLatch(1)
        private var headerSent = false

        override fun read(): Int = throw UnsupportedOperationException("Use bounded bulk reads")

        override fun read(target: ByteArray, offset: Int, length: Int): Int {
            if (!headerSent) {
                target[offset] = 0x1f
                target[offset + 1] = 0x8b.toByte()
                headerSent = true
                return 2
            }
            thread.set(Thread.currentThread())
            entered.countDown()
            try {
                awaitIgnoringInterrupts(releaseRead)
                return -1
            } finally {
                exited.countDown()
            }
        }

        override fun close() {
            closeEntered.countDown()
            if (closeReleasesRead) releaseRead.countDown()
            if (blockClose) awaitIgnoringInterrupts(releaseClose)
            closeExited.countDown()
        }

        fun release() {
            releaseRead.countDown()
            releaseClose.countDown()
        }

        private fun awaitIgnoringInterrupts(latch: CountDownLatch) {
            while (true) {
                try {
                    latch.await()
                    return
                } catch (_: InterruptedException) {
                    interrupted.countDown()
                }
            }
        }
    }

    private suspend fun CountDownLatch.awaitSuspending() =
        withTimeout(5000) { while (count != 0L) delay(5) }
}
