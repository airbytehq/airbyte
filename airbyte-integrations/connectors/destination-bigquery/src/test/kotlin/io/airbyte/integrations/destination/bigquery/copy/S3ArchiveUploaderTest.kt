/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.copy

import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.io.ByteArrayOutputStream
import java.io.InputStream
import java.nio.ByteBuffer
import java.nio.file.Files
import java.nio.file.Path
import java.time.Duration
import java.util.concurrent.CompletableFuture
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.supervisorScope
import kotlinx.coroutines.withContext
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import org.reactivestreams.Subscriber
import org.reactivestreams.Subscription
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider
import software.amazon.awssdk.core.async.AsyncRequestBody
import software.amazon.awssdk.core.async.AsyncRequestBodySplitConfiguration
import software.amazon.awssdk.core.async.CloseableAsyncRequestBody
import software.amazon.awssdk.services.s3.S3AsyncClient
import software.amazon.awssdk.services.s3.model.PutObjectRequest
import software.amazon.awssdk.services.s3.model.PutObjectResponse

class S3ArchiveUploaderTest {
    @TempDir lateinit var directory: Path

    @Test
    fun `range clamps oversized reads and returns EOF after closing at boundary`() {
        val source = java.io.ByteArrayInputStream(byteArrayOf(1, 2, 3, 4, 5))
        val range = ArchiveRangeInputStream(source, 3)
        val buffer = ByteArray(10)
        assertEquals(1, range.read())
        assertEquals(2, range.read(buffer, 1, 9))
        assertArrayEquals(byteArrayOf(2, 3), buffer.copyOfRange(1, 3))
        assertEquals(2, source.available())
        assertEquals(-1, range.read())
        assertEquals(-1, range.read(buffer))
        assertEquals(0, range.read(buffer, 0, 0))
    }

    @Test
    fun `empty range never reads source and zero length reads return zero`() {
        val source = java.io.ByteArrayInputStream(byteArrayOf(1, 2, 3))
        ArchiveRangeInputStream(source, 0).use { range ->
            assertEquals(0, range.read(ByteArray(1), 0, 0))
            assertEquals(-1, range.read(ByteArray(1)))
            assertEquals(-1, range.read())
            assertEquals(3, source.available())
        }
    }

    private val client = mockk<S3AsyncClient>(relaxed = true)
    private val credentials =
        mockk<AwsCredentialsProvider> {
            every { resolveCredentials() } returns AwsBasicCredentials.create("test", "test")
        }

    private fun uploader(
        timeout: Duration = Duration.ofSeconds(2),
        factory: (Path) -> ArchiveFileBody = { ArchiveFileBody(it) },
    ) = S3ArchiveUploader("archive", client, credentials, listOf(client), timeout, factory)

    private fun file(): Path =
        Files.write(directory.resolve("payload.csv.gz"), byteArrayOf(31, -117, 0, -1, 13, 10))

    @Test
    fun `normal last byte close preserves demand for buffered final chunk and completion`() {
        val path = Files.write(directory.resolve("two-chunks.csv.gz"), byteArrayOf(11, 22))
        val descriptorClosed = CountDownLatch(1)
        val cleanup = Executors.newSingleThreadExecutor()
        val body =
            ArchiveFileBody(path) { file, _ ->
                object : java.io.FilterInputStream(Files.newInputStream(file)) {
                    override fun read(bytes: ByteArray, off: Int, len: Int): Int =
                        `in`.read(bytes, off, minOf(1, len))

                    override fun close() {
                        super.close()
                        descriptorClosed.countDown()
                    }
                }
            }
        try {
            val subscription = AtomicReference<Subscription>()
            val chunks = java.util.concurrent.LinkedBlockingQueue<ByteArray>()
            val completed = CompletableFuture<Unit>()
            body.subscribe(
                object : Subscriber<ByteBuffer> {
                    override fun onSubscribe(s: Subscription) {
                        subscription.set(s)
                        s.request(1)
                    }

                    override fun onNext(buffer: ByteBuffer) {
                        chunks.add(ByteArray(buffer.remaining()).also { buffer.get(it) })
                    }

                    override fun onError(t: Throwable) {
                        completed.completeExceptionally(t)
                    }

                    override fun onComplete() {
                        completed.complete(Unit)
                    }
                }
            )
            assertArrayEquals(byteArrayOf(11), chunks.poll(5, TimeUnit.SECONDS))
            // The reader has read/closed the file, but its final chunk still awaits demand.
            assertTrue(descriptorClosed.await(5, TimeUnit.SECONDS))
            assertFalse(completed.isDone)
            subscription.get().request(1)
            assertArrayEquals(byteArrayOf(22), chunks.poll(5, TimeUnit.SECONDS))
            subscription.get().request(1)
            completed.get(5, TimeUnit.SECONDS)
            assertTrue(chunks.isEmpty())
        } finally {
            try {
                body.stop(cleanup, Duration.ofSeconds(2))
            } finally {
                cleanup.shutdownNow()
            }
        }
    }

    @Test
    fun `partial subscription cancel closes descriptor and permits retry before root cleanup`() {
        verifyPartialSubscriptionRelease(closePart = false)
    }

    @Test
    fun `part close releases blocked subscription and rejects reopening only that part`() {
        verifyPartialSubscriptionRelease(closePart = true)
    }

    @Test
    fun `stalled subscription close cannot make root cleanup wait indefinitely`() {
        val closing = CountDownLatch(1)
        val releaseClose = CountDownLatch(1)
        val closed = CountDownLatch(1)
        val cleanup = Executors.newSingleThreadExecutor()
        val body =
            ArchiveFileBody(file()) { path, _ ->
                object : java.io.FilterInputStream(Files.newInputStream(path)) {
                    override fun close() {
                        closing.countDown()
                        while (releaseClose.count > 0) {
                            try {
                                releaseClose.await()
                            } catch (_: InterruptedException) {
                                /* Stalled close. */
                            }
                        }
                        super.close()
                        closed.countDown()
                    }
                }
            }
        try {
            val bytes = CompletableFuture<ByteArray>()
            consume(body, bytes)
            bytes.get(5, TimeUnit.SECONDS)
            assertTrue(closing.await(5, TimeUnit.SECONDS))
            val start = System.nanoTime()
            val failure =
                runCatching { body.stop(cleanup, Duration.ofMillis(100)) }.exceptionOrNull()
            assertTrue(
                failure is java.util.concurrent.TimeoutException ||
                    failure is java.util.concurrent.ExecutionException
            )
            assertTrue(System.nanoTime() - start < TimeUnit.SECONDS.toNanos(2))
            assertEquals(1L, closed.count)
        } finally {
            releaseClose.countDown()
            assertTrue(closed.await(5, TimeUnit.SECONDS))
            cleanup.shutdown()
            assertTrue(cleanup.awaitTermination(5, TimeUnit.SECONDS))
        }
    }

    private fun verifyPartialSubscriptionRelease(closePart: Boolean) {
        val expected = ByteArray(256 * 1024) { (it xor (it ushr 9) xor (it ushr 17)).toByte() }
        val path = Files.write(directory.resolve("partial.csv.gz"), expected)
        val partSize = expected.size / 2
        val opened = AtomicInteger()
        val enteredRead = CountDownLatch(1)
        val releaseRead = CountDownLatch(1)
        val exitedRead = CountDownLatch(1)
        val descriptorClosed = CountDownLatch(1)
        val cleanup = Executors.newSingleThreadExecutor()
        val body =
            ArchiveFileBody(path) { file, offset ->
                val input =
                    java.nio.channels.Channels.newInputStream(
                        java.nio.channels.FileChannel.open(file).position(offset)
                    )
                if (opened.incrementAndGet() != 1) input
                else
                    object : java.io.FilterInputStream(input) {
                        private var first = true

                        override fun read(bytes: ByteArray, off: Int, len: Int): Int {
                            if (first) {
                                first = false
                                return `in`.read(bytes, off, minOf(16, len))
                            }
                            enteredRead.countDown()
                            try {
                                while (releaseRead.count > 0) {
                                    try {
                                        releaseRead.await()
                                    } catch (_: InterruptedException) {
                                        /* close must release this read */
                                    }
                                }
                                throw java.io.IOException("closed while reading")
                            } finally {
                                exitedRead.countDown()
                            }
                        }

                        override fun close() {
                            try {
                                super.close()
                                descriptorClosed.countDown()
                            } finally {
                                releaseRead.countDown()
                            }
                        }
                    }
            }
        try {
            val parts = mutableListOf<CloseableAsyncRequestBody>()
            val ready = CompletableFuture<Unit>()
            body
                .splitCloseable(
                    AsyncRequestBodySplitConfiguration.builder()
                        .chunkSizeInBytes(partSize.toLong())
                        .build()
                )
                .subscribe(
                    object : Subscriber<CloseableAsyncRequestBody> {
                        override fun onSubscribe(s: Subscription) = s.request(Long.MAX_VALUE)

                        override fun onNext(part: CloseableAsyncRequestBody) {
                            parts.add(part)
                        }

                        override fun onError(t: Throwable) {
                            ready.completeExceptionally(t)
                        }

                        override fun onComplete() {
                            ready.complete(Unit)
                        }
                    }
                )
            ready.get(5, TimeUnit.SECONDS)
            val subscription = AtomicReference<Subscription>()
            parts[1].subscribe(
                object : Subscriber<ByteBuffer> {
                    override fun onSubscribe(s: Subscription) {
                        subscription.set(s)
                        s.request(Long.MAX_VALUE)
                    }

                    override fun onNext(buffer: ByteBuffer) = Unit

                    override fun onError(t: Throwable) = Unit

                    override fun onComplete() = Unit
                }
            )
            assertTrue(enteredRead.await(5, TimeUnit.SECONDS))
            if (closePart) parts[1].close() else subscription.get().cancel()
            assertTrue(
                descriptorClosed.await(5, TimeUnit.SECONDS),
                "Cancelled subscription retained its descriptor",
            )
            assertTrue(
                exitedRead.await(5, TimeUnit.SECONDS),
                "Cancelled reader still blocked the single executor",
            )
            if (closePart) {
                val rejected = CompletableFuture<ByteArray>()
                consume(parts[1], rejected)
                assertTrue(rejected.isCompletedExceptionally)
                assertEquals(1, opened.get())
            }
            val retried = CompletableFuture<ByteArray>()
            consume(parts[if (closePart) 0 else 1], retried)
            assertArrayEquals(
                if (closePart) expected.copyOfRange(0, partSize)
                else expected.copyOfRange(partSize, expected.size),
                retried.get(5, TimeUnit.SECONDS),
            )
            assertEquals(2, opened.get())
            // All assertions above run with the root body still open.
        } finally {
            releaseRead.countDown()
            try {
                body.stop(cleanup, Duration.ofSeconds(2))
            } finally {
                cleanup.shutdownNow()
            }
        }
    }

    @Test
    fun `upload streams exact bytes and headers and waits for final S3 response`() = runBlocking {
        val path = file()
        val finalResponse = CompletableFuture<PutObjectResponse>()
        val received = CompletableFuture<ByteArray>()
        val request = CompletableFuture<PutObjectRequest>()
        every { client.putObject(any<PutObjectRequest>(), any<AsyncRequestBody>()) } answers
            {
                request.complete(firstArg())
                consume(secondArg(), received)
                finalResponse
            }
        val uploader = uploader()
        try {
            val metadata = mutableMapOf("batch-id" to "batch")
            val operation = async {
                uploader.upload(path, "fusion/path.csv.gz", "application/gzip", metadata)
            }
            val bytes = withContext(Dispatchers.IO) { received.get(5, TimeUnit.SECONDS) }
            assertArrayEquals(Files.readAllBytes(path), bytes)
            assertFalse(operation.isCompleted)
            metadata["batch-id"] = "changed"
            assertEquals("batch", request.get().metadata()["batch-id"])
            assertEquals("application/gzip", request.get().contentType())
            assertNull(request.get().contentEncoding())
            assertEquals("archive", request.get().bucket())
            assertEquals("fusion/path.csv.gz", request.get().key())
            finalResponse.complete(PutObjectResponse.builder().build())
            operation.await()
            Files.delete(path)
        } finally {
            uploader.close()
        }
    }

    @Test
    fun `body retry subscriptions start at byte zero and late subscriptions cannot reopen file`() {
        val path = file()
        var opens = 0
        val body =
            ArchiveFileBody(path) { file, _ ->
                opens++
                Files.newInputStream(file)
            }
        val cleanup = Executors.newSingleThreadExecutor()
        try {
            repeat(3) {
                val read = CompletableFuture<ByteArray>()
                consume(body, read)
                assertArrayEquals(Files.readAllBytes(path), read.get(5, TimeUnit.SECONDS))
            }
            body.stop(cleanup, Duration.ofSeconds(2))
            Files.delete(path)
            val late = CompletableFuture<ByteArray>()
            consume(body, late)
            assertTrue(late.isCompletedExceptionally)
            assertEquals(3, opens)
        } finally {
            cleanup.shutdownNow()
        }
    }

    @Test
    fun `S3 failure closes the opened stream before throwing`() = runBlocking {
        val closed = AtomicBoolean()
        val received = CompletableFuture<ByteArray>()
        val failed = CompletableFuture<PutObjectResponse>()
        val failure = IllegalStateException("S3 refused object")
        every { client.putObject(any<PutObjectRequest>(), any<AsyncRequestBody>()) } answers
            {
                consume(secondArg(), received)
                received.whenComplete { _, _ -> failed.completeExceptionally(failure) }
                failed
            }
        val uploader =
            uploader(
                factory = { path ->
                    ArchiveFileBody(path) { file, _ ->
                        object : java.io.FilterInputStream(Files.newInputStream(file)) {
                            override fun close() {
                                super.close()
                                closed.set(true)
                            }
                        }
                    }
                }
            )
        try {
            val actual =
                runCatching { uploader.upload(file(), "key", "application/gzip") }.exceptionOrNull()
            assertInstanceOf(IllegalStateException::class.java, actual)
            assertEquals(failure.message, actual!!.message)
            assertTrue(closed.get())
        } finally {
            uploader.close()
        }
    }

    @Test
    fun `cancellation closes and drains a reader even though S3 future is already cancelled`() =
        runBlocking {
            val stream = BlockingStream(releaseOnClose = true)
            val future = CompletableFuture<PutObjectResponse>()
            every { client.putObject(any<PutObjectRequest>(), any<AsyncRequestBody>()) } answers
                {
                    consume(secondArg(), CompletableFuture())
                    future
                }
            val uploader = uploader(factory = { path -> ArchiveFileBody(path) { _, _ -> stream } })
            try {
                val operation = launch { uploader.upload(file(), "key", "application/gzip") }
                withContext(Dispatchers.IO) {
                    assertTrue(stream.entered.await(5, TimeUnit.SECONDS))
                }
                operation.cancelAndJoin()
                assertTrue(future.isCancelled)
                assertTrue(stream.closed.get())
                assertEquals(0L, stream.exited.count)
                assertTrue(operation.isCancelled)
            } finally {
                stream.release.countDown()
                uploader.close()
            }
        }

    @Test
    fun `undrained cancellation signals retained path and prevents new uploads`() = runBlocking {
        supervisorScope {
            val path = file()
            val stream = BlockingStream(releaseOnClose = false)
            val future = CompletableFuture<PutObjectResponse>()
            every { client.putObject(any<PutObjectRequest>(), any<AsyncRequestBody>()) } answers
                {
                    consume(secondArg(), CompletableFuture())
                    future
                }
            val uploader =
                uploader(Duration.ofMillis(100)) { p -> ArchiveFileBody(p) { _, _ -> stream } }
            try {
                // Capture the cleanup exception inside the cancelled coroutine, before await can
                // mask it.
                val observed = CompletableFuture<Throwable>()
                val operation = launch {
                    try {
                        uploader.upload(path, "key", "application/gzip")
                    } catch (t: Throwable) {
                        observed.complete(t)
                    }
                }
                withContext(Dispatchers.IO) {
                    assertTrue(stream.entered.await(5, TimeUnit.SECONDS))
                }
                operation.cancelAndJoin()
                val failure = observed.get(5, TimeUnit.SECONDS)
                assertInstanceOf(ArchiveReaderStillActiveException::class.java, failure)
                assertEquals(path, (failure as ArchiveReaderStillActiveException).path)
                assertInstanceOf(CancellationException::class.java, failure.cause)
                assertEquals(1L, stream.exited.count)
                assertTrue(Files.exists(path))
                assertInstanceOf(
                    IllegalStateException::class.java,
                    runCatching { uploader.upload(path, "second", "application/gzip") }
                        .exceptionOrNull(),
                )
                verify(exactly = 1) {
                    client.putObject(any<PutObjectRequest>(), any<AsyncRequestBody>())
                }
            } finally {
                stream.release.countDown()
                assertTrue(stream.exited.await(5, TimeUnit.SECONDS))
                uploader.close()
            }
        }
    }

    @Test
    fun `validate resolves assumed credentials without requiring bucket read and close is idempotent`():
        Unit = runBlocking {
        val uploader = uploader()
        uploader.validateCredentials()
        verify(exactly = 1) { credentials.resolveCredentials() }
        verify(exactly = 0) { client.putObject(any<PutObjectRequest>(), any<AsyncRequestBody>()) }
        uploader.close()
        uploader.close()
        verify(exactly = 1) { client.close() }
        assertInstanceOf(
            IllegalStateException::class.java,
            runCatching { uploader.upload(file(), "key", "application/gzip") }.exceptionOrNull(),
        )
    }

    private class BlockingStream(private val releaseOnClose: Boolean) : InputStream() {
        val entered = CountDownLatch(1)
        val release = CountDownLatch(1)
        val exited = CountDownLatch(1)
        val closed = AtomicBoolean()

        override fun read(): Int {
            entered.countDown()
            while (release.count > 0) {
                try {
                    release.await()
                } catch (_: InterruptedException) {
                    /* Simulate a stuck reader. */
                }
            }
            exited.countDown()
            return -1
        }

        override fun close() {
            closed.set(true)
            if (releaseOnClose) release.countDown()
        }
    }

    private fun consume(body: AsyncRequestBody, result: CompletableFuture<ByteArray>) {
        val bytes = ByteArrayOutputStream()
        body.subscribe(
            object : Subscriber<ByteBuffer> {
                private lateinit var subscription: Subscription

                override fun onSubscribe(s: Subscription) {
                    subscription = s
                    s.request(1)
                }

                override fun onNext(buffer: ByteBuffer) {
                    val chunk = ByteArray(buffer.remaining())
                    buffer.get(chunk)
                    bytes.write(chunk)
                    subscription.request(1)
                }

                override fun onError(t: Throwable) {
                    result.completeExceptionally(t)
                }

                override fun onComplete() {
                    result.complete(bytes.toByteArray())
                }
            }
        )
    }
}
