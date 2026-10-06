/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.destination.bigquery.copy

import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.io.ByteArrayOutputStream
import java.nio.ByteBuffer
import java.nio.file.Files
import java.nio.file.Path
import java.time.Duration
import java.util.concurrent.CompletableFuture
import java.util.concurrent.CountDownLatch
import java.util.concurrent.Executors
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir
import org.reactivestreams.Subscriber
import org.reactivestreams.Subscription
import software.amazon.awssdk.core.async.AsyncRequestBody
import software.amazon.awssdk.services.s3.S3AsyncClient
import software.amazon.awssdk.services.s3.model.*

class StreamingS3ArchiveUploadTest {
    @TempDir lateinit var directory: Path

    @Test
    fun `parts upload during append and seal completes asynchronously with exact ordered bytes`() =
        runBlocking {
            Fixture().use { f ->
                f.session.append("abcd".toByteArray())
                val first = f.nextPart()
                assertArrayEquals("abcd".toByteArray(), first.bytes.get(5, TimeUnit.SECONDS))
                verify(exactly = 0) {
                    f.client.completeMultipartUpload(any<CompleteMultipartUploadRequest>())
                }
                first.succeed()
                f.session.append("efghi".toByteArray())
                val second = f.nextPart()
                f.session.seal()
                val third = f.nextPart()
                third.succeed()
                second.succeed()
                assertTrue(f.completing.await(5, TimeUnit.SECONDS))
                assertEquals(
                    listOf(1, 2, 3),
                    f.completionRequest!!.multipartUpload().parts().map { it.partNumber() }
                )
                assertEquals(
                    listOf("checksum-1", "checksum-2", "checksum-3"),
                    f.completionRequest!!.multipartUpload().parts().map { it.checksumCRC32() }
                )
                assertArrayEquals("efgh".toByteArray(), second.bytes.get(5, TimeUnit.SECONDS))
                assertArrayEquals("i".toByteArray(), third.bytes.get(5, TimeUnit.SECONDS))
                val finishing = async { f.session.finish() }
                yield()
                assertFalse(finishing.isCompleted)
                f.completion.complete(CompleteMultipartUploadResponse.builder().build())
                withTimeout(5000) { finishing.await() }
                f.session.finish()
                f.session.close()
                assertEquals(0, f.budget.retainedBytes())
                assertEquals(0, Files.list(directory).use { it.count() })
                verify(exactly = 0) {
                    f.client.abortMultipartUpload(any<AbortMultipartUploadRequest>())
                }
                verify(exactly = 1) {
                    f.client.createMultipartUpload(
                        match<CreateMultipartUploadRequest> {
                            it.metadata() == mapOf("batch-id" to "batch") &&
                                it.contentType() == "application/x-ndjson"
                        }
                    )
                }
            }
        }

    @Test
    fun `append backpressures at two outstanding parts without holding lifecycle lock`() {
        Fixture().use { f ->
            val producer = Executors.newSingleThreadExecutor()
            try {
                val appended = producer.submit { f.session.append("abcdefghijkl".toByteArray()) }
                val first = f.nextPart()
                val second = f.nextPart()
                assertNull(f.requests.poll(100, TimeUnit.MILLISECONDS))
                assertFalse(appended.isDone)
                assertEquals(8, f.budget.retainedBytes())
                first.succeed()
                val third = f.nextPart()
                appended.get(5, TimeUnit.SECONDS)
                assertArrayEquals("ijkl".toByteArray(), third.bytes.get(5, TimeUnit.SECONDS))
                second.succeed()
                third.succeed()
            } finally {
                producer.shutdownNow()
            }
        }
    }

    @Test
    fun `close deletes queued part cancelled before reader starts`() {
        val gate = Semaphore(1, 1)
        val opened = AtomicInteger()
        Fixture(
                gate = gate,
                bodyFactory = {
                    opened.incrementAndGet()
                    ArchiveFileBody(it)
                }
            )
            .use { f ->
                f.session.append("abcd".toByteArray())
                assertEquals(4, f.budget.retainedBytes())
                f.session.close()
                assertEquals(0, opened.get())
                assertEquals(0, f.budget.retainedBytes())
                assertEquals(0, Files.list(directory).use { it.count() })
                verify(exactly = 0) {
                    f.client.uploadPart(any<UploadPartRequest>(), any<AsyncRequestBody>())
                }
                verify(exactly = 1) {
                    f.client.abortMultipartUpload(any<AbortMultipartUploadRequest>())
                }
            }
    }

    @Test
    fun `closing while append waits cancels producer and drains all files`() {
        Fixture().use { f ->
            val producer = Executors.newSingleThreadExecutor()
            try {
                val appended = producer.submit { f.session.append("abcdefghijkl".toByteArray()) }
                f.nextPart()
                f.nextPart()
                f.session.close()
                assertThrows(java.util.concurrent.ExecutionException::class.java) {
                    appended.get(5, TimeUnit.SECONDS)
                }
                assertEquals(0, f.budget.retainedBytes())
                assertEquals(0, Files.list(directory).use { it.count() })
            } finally {
                producer.shutdownNow()
            }
        }
    }

    @Test
    fun `late create response after cancellation is aborted without opening readers`() {
        val creation = CompletableFuture<CreateMultipartUploadResponse>()
        Fixture(creation = creation).use { f ->
            f.session.append("abcd".toByteArray())
            f.session.close()
            assertFalse(creation.isCancelled)
            creation.complete(CreateMultipartUploadResponse.builder().uploadId("late-id").build())
            verify(exactly = 1) {
                f.client.abortMultipartUpload(
                    match<AbortMultipartUploadRequest> { it.uploadId() == "late-id" }
                )
            }
            assertEquals(0, f.budget.retainedBytes())
        }
    }

    @Test
    fun `small partial and empty sessions do not open S3 before sealing`() = runBlocking {
        Fixture().use { f ->
            f.session.append("abc".toByteArray())
            verify(exactly = 0) {
                f.client.createMultipartUpload(any<CreateMultipartUploadRequest>())
            }
            f.session.seal()
            f.nextPart().succeed()
            assertTrue(f.completing.await(5, TimeUnit.SECONDS))
            f.completion.complete(CompleteMultipartUploadResponse.builder().build())
            f.session.finish()
        }
        Fixture().use { f ->
            f.session.append(byteArrayOf())
            f.session.finish()
            f.session.finish()
            verify(exactly = 0) {
                f.client.createMultipartUpload(any<CreateMultipartUploadRequest>())
            }
        }
    }

    @Test
    fun `part failure aborts and preserves original failure when abort also fails`() = runBlocking {
        Fixture(ignoreCloseFailure = true).use { f ->
            val original = IllegalStateException("part rejected")
            val abortFailure = IllegalStateException("abort rejected")
            every { f.client.abortMultipartUpload(any<AbortMultipartUploadRequest>()) } returns
                CompletableFuture.failedFuture(abortFailure)
            f.session.append("abcd".toByteArray())
            f.nextPart().response.completeExceptionally(original)
            val actual = runCatching { f.session.finish() }.exceptionOrNull()
            assertInstanceOf(IllegalStateException::class.java, actual)
            assertEquals(original.message, actual!!.message)
            val causes = generateSequence(actual) { it.cause }.toList()
            assertTrue(
                causes.any { it.suppressed.isNotEmpty() },
                causes.joinToString {
                    "${it.javaClass.simpleName}: ${it.message}; suppressed=${it.suppressed.toList()}"
                }
            )
            verify(exactly = 0) {
                f.client.completeMultipartUpload(any<CompleteMultipartUploadRequest>())
            }
            assertEquals(0, f.budget.retainedBytes())
        }
    }

    @Test
    fun `shared disk cap fails without losing reservation for other session`() {
        val budget = StreamingArchiveDiskBudget(5)
        Fixture(budget = budget).use { first ->
            Fixture(budget = budget).use { second ->
                first.session.append("abc".toByteArray())
                assertThrows(IllegalStateException::class.java) {
                    second.session.append("def".toByteArray())
                }
                assertEquals(3, budget.retainedBytes())
                first.session.close()
                assertEquals(0, budget.retainedBytes())
            }
        }
    }

    @Test
    fun `shared part gate limits concurrent sessions and queued files drain on close`() {
        val gate = Semaphore(1)
        Fixture(gate = gate).use { first ->
            Fixture(gate = gate).use { second ->
                first.session.append("abcd".toByteArray())
                val part = first.nextPart()
                second.session.append("efgh".toByteArray())
                assertNull(second.requests.poll(100, TimeUnit.MILLISECONDS))
                part.succeed()
                assertArrayEquals(
                    "efgh".toByteArray(),
                    second.nextPart().bytes.get(5, TimeUnit.SECONDS)
                )
            }
        }
        assertEquals(0, Files.list(directory).use { it.count() })
    }

    @Test
    fun `undrained reader retains immutable part and budget and reports unsafe cleanup`() =
        runBlocking {
            val entered = CountDownLatch(1)
            val release = CountDownLatch(1)
            val f =
                Fixture(
                    bodyFactory = { path ->
                        ArchiveFileBody(path) { _, _ ->
                            object : java.io.InputStream() {
                                override fun read(): Int {
                                    entered.countDown()
                                    while (release.count > 0) {
                                        try {
                                            release.await()
                                        } catch (_: InterruptedException) {
                                            /* Deliberately ignore cancellation. */
                                        }
                                    }
                                    return -1
                                }
                                override fun close() = Unit
                            }
                        }
                    }
                )
            try {
                f.session.append("abcd".toByteArray())
                val part = f.nextPart()
                assertTrue(entered.await(5, TimeUnit.SECONDS))
                part.response.completeExceptionally(IllegalStateException("upload rejected"))
                val error = runCatching { f.session.finish() }.exceptionOrNull()
                assertInstanceOf(ArchiveReaderStillActiveException::class.java, error)
                assertEquals(4, f.budget.retainedBytes())
                assertEquals(1, Files.list(directory).use { it.count() })
                assertFalse(f.unsafe.isEmpty())
            } finally {
                release.countDown()
                runCatching { f.close() }
            }
        }

    @Test
    fun `completion failure aborts without releasing successful finish`() = runBlocking {
        Fixture().use { f ->
            f.session.append("abc".toByteArray())
            f.session.seal()
            f.nextPart().succeed()
            assertTrue(f.completing.await(5, TimeUnit.SECONDS))
            f.completion.completeExceptionally(IllegalStateException("complete rejected"))
            val error = runCatching { f.session.finish() }.exceptionOrNull()
            assertEquals("complete rejected", error?.message)
            verify(exactly = 1) {
                f.client.abortMultipartUpload(any<AbortMultipartUploadRequest>())
            }
            assertEquals(0, f.budget.retainedBytes())
        }
    }

    @Test
    fun `finish cancellation drains files and aborts unfinished multipart`() = runBlocking {
        Fixture().use { f ->
            f.session.append("abcd".toByteArray())
            val part = f.nextPart()
            val finishing = launch { f.session.finish() }
            yield()
            finishing.cancelAndJoin()
            assertTrue(part.response.isCancelled)
            assertEquals(0, f.budget.retainedBytes())
            assertEquals(0, Files.list(directory).use { it.count() })
            verify(exactly = 1) {
                f.client.abortMultipartUpload(any<AbortMultipartUploadRequest>())
            }
        }
    }

    @Test
    fun `uploader owns and closes all unsealed streaming sessions`() {
        Fixture().use { f ->
            val uploader = S3ArchiveUploader("bucket", f.client, mockk(), emptyList())
            val first =
                uploader.startStreaming("first", "application/x-ndjson", emptyMap(), directory)
            val second =
                uploader.startStreaming("second", "application/x-ndjson", emptyMap(), directory)
            first.append("abc".toByteArray())
            second.append("def".toByteArray())
            assertEquals(2, Files.list(directory).use { it.count() })
            uploader.close()
            assertEquals(0, Files.list(directory).use { it.count() })
            assertThrows(IllegalStateException::class.java) { first.append("more".toByteArray()) }
            assertThrows(IllegalStateException::class.java) {
                uploader.startStreaming("late", "application/x-ndjson", emptyMap(), directory)
            }
        }
    }

    private inner class Fixture(
        val ignoreCloseFailure: Boolean = false,
        val budget: StreamingArchiveDiskBudget = StreamingArchiveDiskBudget(64),
        gate: Semaphore = Semaphore(8),
        creation: CompletableFuture<CreateMultipartUploadResponse> =
            CompletableFuture.completedFuture(
                CreateMultipartUploadResponse.builder().uploadId("id").build()
            ),
        bodyFactory: (Path) -> ArchiveFileBody = { ArchiveFileBody(it) },
    ) : AutoCloseable {
        val client = mockk<S3AsyncClient>()
        val requests = LinkedBlockingQueue<Part>()
        val unsafe = java.util.concurrent.CopyOnWriteArrayList<Throwable>()
        val completion = CompletableFuture<CompleteMultipartUploadResponse>()
        val completing = CountDownLatch(1)
        @Volatile var completionRequest: CompleteMultipartUploadRequest? = null
        private val cleanup = Executors.newFixedThreadPool(2)
        val session: StreamingS3ArchiveUpload
        init {
            every { client.createMultipartUpload(any<CreateMultipartUploadRequest>()) } returns
                creation
            every { client.abortMultipartUpload(any<AbortMultipartUploadRequest>()) } returns
                CompletableFuture.completedFuture(AbortMultipartUploadResponse.builder().build())
            every { client.completeMultipartUpload(any<CompleteMultipartUploadRequest>()) } answers
                {
                    completionRequest = firstArg()
                    completing.countDown()
                    completion
                }
            every { client.uploadPart(any<UploadPartRequest>(), any<AsyncRequestBody>()) } answers
                {
                    val request = firstArg<UploadPartRequest>()
                    val part = Part(request.partNumber())
                    secondArg<AsyncRequestBody>()
                        .subscribe(
                            object : Subscriber<ByteBuffer> {
                                private val bytes = ByteArrayOutputStream()
                                override fun onSubscribe(s: Subscription) =
                                    s.request(Long.MAX_VALUE)
                                override fun onNext(value: ByteBuffer) {
                                    val chunk = ByteArray(value.remaining())
                                    value.get(chunk)
                                    bytes.write(chunk)
                                }
                                override fun onError(t: Throwable) {
                                    part.bytes.completeExceptionally(t)
                                }
                                override fun onComplete() {
                                    part.bytes.complete(bytes.toByteArray())
                                }
                            }
                        )
                    requests.add(part)
                    part.response
                }
            session =
                StreamingS3ArchiveUpload(
                    client,
                    "bucket",
                    "key",
                    "application/x-ndjson",
                    mapOf("batch-id" to "batch"),
                    directory,
                    budget = budget,
                    globalParts = gate,
                    cleanupWorkers = cleanup,
                    cleanupTimeout = Duration.ofSeconds(1),
                    bodyFactory = bodyFactory,
                    onUnsafe = { unsafe.add(it) },
                    partSize = 4
                )
        }
        fun nextPart(): Part =
            requireNotNull(requests.poll(5, TimeUnit.SECONDS)) { "No UploadPart request arrived" }
        override fun close() {
            try {
                if (ignoreCloseFailure) runCatching { session.close() } else session.close()
            } finally {
                cleanup.shutdownNow()
                check(cleanup.awaitTermination(5, TimeUnit.SECONDS))
            }
        }
    }

    private class Part(val number: Int) {
        val bytes = CompletableFuture<ByteArray>()
        val response = CompletableFuture<UploadPartResponse>()
        fun succeed() {
            bytes.get(5, TimeUnit.SECONDS)
            response.complete(
                UploadPartResponse.builder()
                    .eTag("etag-$number")
                    .checksumCRC32("checksum-$number")
                    .build()
            )
        }
    }
}
