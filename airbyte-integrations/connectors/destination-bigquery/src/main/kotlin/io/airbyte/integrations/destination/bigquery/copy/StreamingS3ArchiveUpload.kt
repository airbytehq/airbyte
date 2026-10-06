/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.destination.bigquery.copy

import java.io.OutputStream
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.StandardOpenOption.APPEND
import java.nio.file.StandardOpenOption.WRITE
import java.time.Duration
import java.util.concurrent.CompletableFuture
import java.util.concurrent.CompletionException
import java.util.concurrent.ExecutorService
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlinx.coroutines.*
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import software.amazon.awssdk.services.s3.S3AsyncClient
import software.amazon.awssdk.services.s3.model.*

interface StreamingArchiveUpload : AutoCloseable {
    fun append(bytes: ByteArray)
    fun seal()
    suspend fun finish()
    override fun close()
}

/**
 * Shared disk accounting includes queued, uploading, and retained files. Reservations never wait.
 */
internal class StreamingArchiveDiskBudget(private val maximum: Long = 4L shl 30) {
    private var used = 0L
    init {
        require(maximum > 0)
    }
    @Synchronized
    fun reserve(bytes: Long) {
        check(bytes <= maximum - used) {
            "Fusion streaming archive exceeds shared disk budget ($maximum)"
        }
        used += bytes
    }
    @Synchronized
    fun release(bytes: Long) {
        used -= bytes
    }
    @Synchronized fun retainedBytes(): Long = used
}

/**
 * append writes exact bytes to bounded disk parts. Full parts upload immediately; seal starts the
 * last part and CompleteMultipartUpload independently of the BigQuery job. Only finish is an ACK
 * barrier. Initial object metadata cannot contain record counts that are unknown during append.
 */
internal class StreamingS3ArchiveUpload(
    private val client: S3AsyncClient,
    private val bucket: String,
    private val key: String,
    private val contentType: String,
    metadata: Map<String, String>,
    private val directory: Path? = null,
    private val budget: StreamingArchiveDiskBudget,
    private val globalParts: Semaphore,
    private val cleanupWorkers: ExecutorService,
    private val cleanupTimeout: Duration = Duration.ofSeconds(10),
    private val bodyFactory: (Path) -> ArchiveFileBody = { ArchiveFileBody(it) },
    private val checkAvailable: () -> Unit = {},
    private val onUnsafe: (Throwable) -> Unit = {},
    private val onClosed: () -> Unit = {},
    private val partSize: Long = S3ArchiveUploader.PART_SIZE,
) : StreamingArchiveUpload {
    private val metadata = metadata.toMap()
    private val lock = Any()
    private val appendLock = Any()
    private val log = io.github.oshai.kotlinlogging.KotlinLogging.logger {}
    private val root = SupervisorJob()
    private val scope = CoroutineScope(root + Dispatchers.IO)
    private val parts = mutableListOf<Deferred<CompletedPart>>()
    private val localParts = Semaphore(2)
    private val result = CompletableFuture<Unit>()
    private val failure = AtomicReference<Throwable?>()
    private val unsafe = AtomicReference<Throwable?>()
    private val closed = AtomicBoolean()
    private val closeResult = CompletableFuture<Unit>()
    private val completed = AtomicBoolean()
    private val abort = AtomicReference<CompletableFuture<AbortMultipartUploadResponse>?>()
    private var creation: CompletableFuture<CreateMultipartUploadResponse>? = null
    private var sealed = false
    private var current: Path? = null
    private var writer: OutputStream? = null
    private var currentSize = 0L
    private var total = 0L

    init {
        require(partSize > 0 && partSize <= Long.MAX_VALUE / 10_000)
        require("input-record-count" !in metadata && "loaded-record-count" !in metadata) {
            "Streaming archive metadata must omit record counts until they are known"
        }
    }

    override fun append(bytes: ByteArray) {
        try {
            synchronized(appendLock) {
                synchronized(lock) {
                    checkOpen()
                    check(!sealed) { "Fusion streaming archive is sealed" }
                    check(bytes.size.toLong() <= 10_000L * partSize - total) {
                        "Fusion streaming archive exceeds the multipart size limit (${10_000L * partSize})"
                    }
                }
                var offset = 0
                while (offset < bytes.size) {
                    // Never wait holding the lifecycle lock: failures and close must drain readers.
                    val pending =
                        synchronized(lock) {
                            if (current == null) parts.filter { !it.isCompleted } else emptyList()
                        }
                    if (pending.size >= 2) runBlocking { pending.first().await() }
                    synchronized(lock) {
                        checkOpen()
                        val count =
                            minOf(bytes.size - offset.toLong(), partSize - currentSize).toInt()
                        if (current == null) {
                            val path = newPath()
                            current = path
                            writer = Files.newOutputStream(path, WRITE, APPEND).buffered()
                        }
                        budget.reserve(count.toLong())
                        currentSize += count
                        total += count
                        requireNotNull(writer).write(bytes, offset, count)
                        offset += count
                        if (currentSize == partSize) submitPart()
                    }
                }
            }
        } catch (t: Throwable) {
            fail(t)
            closeAfterFailure(t)
        }
    }

    // Caller holds lock. The file has no open writer and will never be mutated after submission.
    private fun submitPart() {
        val path = requireNotNull(current)
        val size = currentSize
        writer?.close()
        writer = null
        val number = parts.size + 1
        val initiation =
            creation
                ?: client
                    .createMultipartUpload(
                        CreateMultipartUploadRequest.builder()
                            .bucket(bucket)
                            .key(key)
                            .contentType(contentType)
                            .checksumAlgorithm(ChecksumAlgorithm.CRC32)
                            .checksumType(ChecksumType.COMPOSITE)
                            .metadata(metadata)
                            .build()
                    )
                    .also { future ->
                        creation = future
                        // Do not lose a late upload ID when cancellation races
                        // CreateMultipartUpload.
                        future.whenComplete { response, _ ->
                            if (response != null && (closed.get() || failure.get() != null))
                                abortRemote(response.uploadId())
                        }
                    }
        current = null
        currentSize = 0
        val task =
            scope.async(start = CoroutineStart.UNDISPATCHED) {
                var retain = false
                try {
                    localParts.withPermit {
                        globalParts.withPermit {
                            checkOpen()
                            val uploadId = initiation.awaitStreaming(cancel = false).uploadId()
                            ensureActive()
                            val body = bodyFactory(path)
                            try {
                                if (number == 1)
                                    log.info {
                                        "Fusion streaming archive started: key=$key part=$number part_bytes=$size"
                                    }
                                val response =
                                    client
                                        .uploadPart(
                                            UploadPartRequest.builder()
                                                .bucket(bucket)
                                                .key(key)
                                                .uploadId(uploadId)
                                                .partNumber(number)
                                                .checksumAlgorithm(ChecksumAlgorithm.CRC32)
                                                .contentLength(size)
                                                .build(),
                                            body,
                                        )
                                        .awaitStreaming()
                                CompletedPart.builder()
                                    .partNumber(number)
                                    .eTag(response.eTag())
                                    .checksumCRC32(response.checksumCRC32())
                                    .checksumCRC32C(response.checksumCRC32C())
                                    .checksumCRC64NVME(response.checksumCRC64NVME())
                                    .checksumSHA1(response.checksumSHA1())
                                    .checksumSHA256(response.checksumSHA256())
                                    .build()
                            } finally {
                                // Keep permits until readers stop; future cancellation is
                                // insufficient.
                                withContext(NonCancellable + Dispatchers.IO) {
                                    try {
                                        body.stop(cleanupWorkers, cleanupTimeout)
                                    } catch (t: Throwable) {
                                        retain = true
                                        val error = ArchiveReaderStillActiveException(path, t)
                                        unsafe.compareAndSet(null, error)
                                        onUnsafe(error)
                                        throw error
                                    }
                                }
                            }
                        }
                    }
                } finally {
                    if (!retain)
                        withContext(NonCancellable + Dispatchers.IO) { deletePart(path, size) }
                }
            }
        parts.add(task)
        task.invokeOnCompletion { error -> if (error != null) fail(error) }
    }

    override fun seal() {
        try {
            synchronized(appendLock) {
                synchronized(lock) {
                    failure.get()?.let { throw it }
                    check(!closed.get()) { "Fusion streaming archive is closed" }
                    if (sealed) return
                    sealed = true
                    if (currentSize > 0) submitPart()
                    if (parts.isEmpty()) {
                        completed.set(true)
                        result.complete(Unit)
                        return
                    }
                    val submitted = parts.toList()
                    val initiation = requireNotNull(creation)
                    scope.launch {
                        try {
                            val uploaded = submitted.awaitAll()
                            ensureActive()
                            client
                                .completeMultipartUpload(
                                    CompleteMultipartUploadRequest.builder()
                                        .bucket(bucket)
                                        .key(key)
                                        .uploadId(
                                            initiation.awaitStreaming(cancel = false).uploadId()
                                        )
                                        .checksumType(ChecksumType.COMPOSITE)
                                        .multipartUpload(
                                            CompletedMultipartUpload.builder()
                                                .parts(uploaded)
                                                .build()
                                        )
                                        .build()
                                )
                                .awaitStreaming()
                            completed.set(true)
                            result.complete(Unit)
                        } catch (t: Throwable) {
                            fail(t)
                        }
                    }
                }
            }
        } catch (t: Throwable) {
            fail(t)
            throw t
        }
    }

    override suspend fun finish() {
        try {
            seal()
            result.awaitStreaming(cancel = false)
        } catch (t: Throwable) {
            // Return cleanup errors across the dispatcher boundary before attaching them. Throwing
            // the recovered primary inside withContext can copy it and lose its suppressed errors.
            val cleanup =
                withContext(NonCancellable + Dispatchers.IO) {
                    runCatching { close() }.exceptionOrNull()
                }
            if (cleanup is ArchiveReaderStillActiveException) {
                if (cleanup !== t) cleanup.addSuppressed(t)
                throw cleanup
            }
            if (cleanup != null && cleanup !== t) t.addSuppressed(cleanup)
            throw t
        }
    }

    private fun checkOpen() {
        checkAvailable()
        failure.get()?.let { throw it }
        check(!closed.get()) { "Fusion streaming archive is closed" }
    }

    private fun fail(error: Throwable) {
        if (failure.compareAndSet(null, error)) {
            root.invokeOnCompletion {
                synchronized(lock) {
                    creation?.whenComplete { response, _ ->
                        if (response != null) abortRemote(response.uploadId())
                    }
                }
            }
            root.cancel(CancellationException("Fusion streaming archive failed", error))
            result.completeExceptionally(error)
        }
    }

    private fun abortRemote(uploadId: String) =
        synchronized(abort) {
            if (abort.get() == null && !completed.get()) {
                val request =
                    try {
                        client.abortMultipartUpload(
                            AbortMultipartUploadRequest.builder()
                                .bucket(bucket)
                                .key(key)
                                .uploadId(uploadId)
                                .build()
                        )
                    } catch (t: Throwable) {
                        CompletableFuture.failedFuture(t)
                    }
                abort.set(request)
                request.whenComplete { _, error -> if (error != null) onUnsafe(error) }
            }
        }

    override fun close() {
        if (!closed.compareAndSet(false, true)) {
            awaitClosed()
            return
        }
        if (!completed.get()) fail(CancellationException("Fusion streaming archive closed"))
        root.cancel()
        try {
            runBlocking { withTimeout(cleanupTimeout.toMillis() * 2) { root.join() } }
            synchronized(lock) {
                try {
                    writer?.close()
                    writer = null
                } catch (t: Throwable) {
                    unsafe.compareAndSet(null, t)
                    onUnsafe(t)
                    throw t
                }
                current?.let { deletePart(it, currentSize) }
                current = null
                currentSize = 0
            }
            unsafe.get()?.let { throw it }
            // join may resume before the root completion callback has issued Abort. Ensure
            // a known ID is aborted here as well, then await that same idempotent request.
            synchronized(lock) {
                creation
                    ?.takeIf { it.isDone && !it.isCompletedExceptionally && !it.isCancelled }
                    ?.getNow(null)
                    ?.let { response -> if (!completed.get()) abortRemote(response.uploadId()) }
            }
            // Create may still be in flight. Its callback aborts the late ID, without opening
            // files.
            abort.get()?.get(cleanupTimeout.toMillis(), java.util.concurrent.TimeUnit.MILLISECONDS)
            closeResult.complete(Unit)
        } catch (t: Throwable) {
            closeResult.completeExceptionally(t)
            throw t
        } finally {
            onClosed()
        }
    }

    private fun awaitClosed() {
        try {
            closeResult.get(
                cleanupTimeout.toMillis() * 4,
                java.util.concurrent.TimeUnit.MILLISECONDS
            )
        } catch (t: java.util.concurrent.ExecutionException) {
            throw (t.cause ?: t)
        }
    }

    private fun closeAfterFailure(error: Throwable): Nothing {
        try {
            close()
        } catch (cleanup: Throwable) {
            if (cleanup is ArchiveReaderStillActiveException) {
                if (cleanup !== error) cleanup.addSuppressed(error)
                throw cleanup
            }
            if (cleanup !== error) error.addSuppressed(cleanup)
        }
        throw error
    }

    private fun deletePart(path: Path, size: Long) {
        try {
            Files.deleteIfExists(path)
            budget.release(size)
        } catch (t: Throwable) {
            unsafe.compareAndSet(null, t)
            onUnsafe(t)
            throw t
        }
    }

    private fun newPath(): Path =
        if (directory == null) Files.createTempFile("bigquery-fusion-part-", ".jsonl")
        else Files.createTempFile(directory, "bigquery-fusion-part-", ".jsonl")
}

private suspend fun <T> CompletableFuture<T>.awaitStreaming(cancel: Boolean = true): T =
    suspendCancellableCoroutine { continuation ->
        if (cancel) continuation.invokeOnCancellation { cancel(true) }
        whenComplete { value, error ->
            if (error == null) continuation.resume(value)
            else
                continuation.resumeWithException(
                    if (error is CompletionException) error.cause ?: error else error
                )
        }
    }
