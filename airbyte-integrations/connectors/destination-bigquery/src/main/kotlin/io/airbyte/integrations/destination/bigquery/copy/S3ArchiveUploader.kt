/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.copy

import java.io.FilterInputStream
import java.io.InputStream
import java.nio.ByteBuffer
import java.nio.channels.Channels
import java.nio.channels.FileChannel
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.StandardOpenOption
import java.time.Duration
import java.util.Objects
import java.util.Optional
import java.util.UUID
import java.util.concurrent.ArrayBlockingQueue
import java.util.concurrent.CompletableFuture
import java.util.concurrent.CompletionException
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.Future
import java.util.concurrent.ThreadFactory
import java.util.concurrent.ThreadPoolExecutor
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicReference
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.runInterruptible
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import org.reactivestreams.Subscriber
import org.reactivestreams.Subscription
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider
import software.amazon.awssdk.core.async.AsyncRequestBody
import software.amazon.awssdk.core.async.AsyncRequestBodySplitConfiguration
import software.amazon.awssdk.core.async.CloseableAsyncRequestBody
import software.amazon.awssdk.core.async.SdkPublisher
import software.amazon.awssdk.core.client.config.ClientOverrideConfiguration
import software.amazon.awssdk.http.nio.netty.NettyNioAsyncHttpClient
import software.amazon.awssdk.http.urlconnection.UrlConnectionHttpClient
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.retries.StandardRetryStrategy
import software.amazon.awssdk.services.s3.S3AsyncClient
import software.amazon.awssdk.services.s3.S3AsyncClientBuilder
import software.amazon.awssdk.services.s3.model.PutObjectRequest
import software.amazon.awssdk.services.sts.StsClient
import software.amazon.awssdk.services.sts.auth.StsAssumeRoleCredentialsProvider
import software.amazon.awssdk.services.sts.model.AssumeRoleRequest

interface ArchiveUploader {
    suspend fun validateCredentials()

    /**
     * Upload an immutable, closed file, awaiting final object completion. All readers are stopped
     * on return or throw, EXCEPT [ArchiveReaderStillActiveException]: retain its path and disable
     * the enclosing archive service. This exception takes precedence over cancellation during
     * cleanup. The caller owns the file and the overall download/upload/cleanup deadline.
     */
    suspend fun upload(
        path: Path,
        key: String,
        contentType: String,
        metadata: Map<String, String> = emptyMap(),
    )

    fun close()
}

/** Only this exception means that unlinking the spool has not been proven safe. */
class ArchiveReaderStillActiveException(val path: Path, cause: Throwable) :
    IllegalStateException(
        "Archive file readers did not stop; retain spool $path and disable copying",
        cause,
    )

/** Owns AWS clients independently of the existing GCS HMAC/Kotlin SDK beans. */
class S3ArchiveUploader
internal constructor(
    private val bucket: String,
    private val client: S3AsyncClient,
    private val credentials: AwsCredentialsProvider,
    private val ownedResources: List<AutoCloseable>,
    private val cleanupTimeout: Duration = Duration.ofSeconds(10),
    private val bodyFactory: (Path) -> ArchiveFileBody = { ArchiveFileBody(it) },
    installShutdownHook: Boolean = false,
) : ArchiveUploader {
    private constructor(
        config: S3CopyConfiguration,
        clients: Clients,
    ) : this(
        config.bucket,
        clients.s3,
        clients.credentials,
        clients.resources,
        installShutdownHook = true,
    )

    constructor(
        configuration: S3CopyConfiguration
    ) : this(configuration, createClients(configuration))

    private val lock = Any()
    private val closed = AtomicBoolean()
    private val poisoned = AtomicBoolean()
    private val transfers = mutableSetOf<Transfer>()
    private val slots = Semaphore(4)
    private val cleanupWorkers = Executors.newFixedThreadPool(4) { daemon(it, "fusion-s3-cleanup") }
    private val shutdownHook =
        if (installShutdownHook) Thread({ close() }, "fusion-s3-shutdown") else null

    init {
        shutdownHook?.let { Runtime.getRuntime().addShutdownHook(it) }
    }

    override suspend fun validateCredentials() {
        checkAvailable()
        // Resolve the refreshing provider even for an empty catalog; no bucket read permission
        // needed.
        runInterruptible(Dispatchers.IO) { credentials.resolveCredentials() }
        checkAvailable()
    }

    override suspend fun upload(
        path: Path,
        key: String,
        contentType: String,
        metadata: Map<String, String>,
    ) {
        slots.withPermit {
            val transfer =
                synchronized(lock) {
                    checkAvailable()
                    Transfer(bodyFactory(path)).also { transfers.add(it) }
                }
            var failure: Throwable? = null
            try {
                val request =
                    PutObjectRequest.builder()
                        .bucket(bucket)
                        .key(key)
                        .contentType(contentType)
                        .metadata(metadata.toMap())
                        .build()
                withTimeout(Duration.ofMinutes(30).toMillis()) {
                    val future = client.putObject(request, transfer.body)
                    transfer.future.set(future)
                    if (closed.get() || poisoned.get()) future.cancel(true)
                    future.awaitUpload()
                }
            } catch (t: Throwable) {
                failure = t
                throw t
            } finally {
                // Cancelling an SDK future is not a reader-stop signal. The owned executor must
                // drain.
                transfer.future.get()?.cancel(true)
                withContext(NonCancellable + Dispatchers.IO) {
                    try {
                        transfer.body.stop(cleanupWorkers, cleanupTimeout)
                    } catch (cleanupFailure: Throwable) {
                        poisoned.set(true)
                        val unsafe =
                            ArchiveReaderStillActiveException(path, failure ?: cleanupFailure)
                        if (failure != null) unsafe.addSuppressed(cleanupFailure)
                        throw unsafe
                    } finally {
                        synchronized(lock) { transfers.remove(transfer) }
                    }
                }
            }
        }
    }

    private fun checkAvailable() {
        check(!closed.get()) { "Archive uploader is closed" }
        check(!poisoned.get()) { "Archive uploader disabled after a file reader cleanup failure" }
    }

    override fun close() {
        val active =
            synchronized(lock) {
                if (!closed.compareAndSet(false, true)) return
                transfers.toList()
            }
        active.forEach { it.future.get()?.cancel(true) }
        // A daemon and a deadline also bound SDK/provider shutdown, including a stuck HTTP close.
        val closer = Executors.newSingleThreadExecutor { daemon(it, "fusion-s3-close") }
        val result =
            closer.submit {
                var failure: Throwable? = null
                fun attempt(block: () -> Unit) {
                    try {
                        block()
                    } catch (t: Throwable) {
                        if (failure == null) failure = t else failure!!.addSuppressed(t)
                    }
                }
                active.forEach { transfer ->
                    attempt { transfer.body.stop(cleanupWorkers, cleanupTimeout) }
                }
                ownedResources.forEach { resource -> attempt { resource.close() } }
                cleanupWorkers.shutdown()
                failure?.let { throw it }
            }
        closer.shutdown()
        try {
            result.get(cleanupTimeout.toMillis(), TimeUnit.MILLISECONDS)
        } catch (t: Exception) {
            poisoned.set(true)
            if (t is InterruptedException) Thread.currentThread().interrupt()
            throw IllegalStateException("Archive uploader shutdown did not complete cleanly", t)
        } finally {
            shutdownHook?.let {
                if (Thread.currentThread() !== it) {
                    try {
                        Runtime.getRuntime().removeShutdownHook(it)
                    } catch (_: IllegalStateException) {
                        // JVM shutdown is already in progress.
                    }
                }
            }
        }
    }

    private class Transfer(val body: ArchiveFileBody) {
        val future = AtomicReference<CompletableFuture<*>?>()
    }

    private data class Clients(
        val s3: S3AsyncClient,
        val credentials: StsAssumeRoleCredentialsProvider,
        val resources: List<AutoCloseable>,
    )

    companion object {
        internal const val MULTIPART_THRESHOLD = 64L * 1024 * 1024
        internal const val PART_SIZE = 16L * 1024 * 1024

        internal fun s3ClientBuilder(): S3AsyncClientBuilder =
            S3AsyncClient.builder()
                .overrideConfiguration(clientOverrides())
                .httpClientBuilder(
                    NettyNioAsyncHttpClient.builder()
                        .maxConcurrency(16)
                        .connectionTimeout(Duration.ofSeconds(10))
                        .connectionAcquisitionTimeout(Duration.ofSeconds(10))
                        .readTimeout(Duration.ofMinutes(2))
                        .writeTimeout(Duration.ofMinutes(2))
                )
                .multipartEnabled(true)
                .multipartConfiguration {
                    it.thresholdInBytes(MULTIPART_THRESHOLD)
                        .minimumPartSizeInBytes(PART_SIZE)
                        .apiCallBufferSizeInBytes(2 * PART_SIZE)
                }

        private fun clientOverrides(): ClientOverrideConfiguration =
            ClientOverrideConfiguration.builder()
                .retryStrategy(StandardRetryStrategy.builder().maxAttempts(3).build())
                .apiCallAttemptTimeout(Duration.ofMinutes(2))
                .apiCallTimeout(Duration.ofMinutes(7))
                .build()

        private fun createClients(config: S3CopyConfiguration): Clients {
            val resources = mutableListOf<AutoCloseable>()
            try {
                val base = DefaultCredentialsProvider.builder().build().also { resources.add(it) }
                val region = Region.of(config.region)
                val sts =
                    StsClient.builder()
                        .region(region)
                        .credentialsProvider(base)
                        .overrideConfiguration(clientOverrides())
                        .httpClientBuilder(
                            UrlConnectionHttpClient.builder()
                                .connectionTimeout(Duration.ofSeconds(10))
                                .socketTimeout(Duration.ofMinutes(2))
                        )
                        .build()
                        .also { resources.add(it) }
                val request =
                    AssumeRoleRequest.builder()
                        .roleArn(config.roleArn)
                        .roleSessionName("airbyte-bq-fusion-${UUID.randomUUID()}")
                        .apply { config.externalId?.let { externalId(it) } }
                        .build()
                val credentials =
                    StsAssumeRoleCredentialsProvider.builder()
                        .stsClient(sts)
                        .refreshRequest(request)
                        .asyncCredentialUpdateEnabled(true)
                        .build()
                        .also { resources.add(it) }
                val s3 =
                    s3ClientBuilder().region(region).credentialsProvider(credentials).build().also {
                        resources.add(it)
                    }
                return Clients(s3, credentials, resources.reversed())
            } catch (t: Throwable) {
                resources.asReversed().forEach { resource ->
                    try {
                        resource.close()
                    } catch (cleanup: Throwable) {
                        t.addSuppressed(cleanup)
                    }
                }
                throw t
            }
        }
    }
}

/**
 * File-backed streaming body with explicit reader ownership. Each retry opens a fresh stream
 * instead of depending on InputStream mark/reset. Multipart splits into seekable file ranges, so
 * even an incompletely consumed part can retry without buffering whole parts. Late subscriptions
 * cannot reopen the file after stop. Executor termination, not future cancellation, proves reader
 * shutdown.
 */
internal class ArchiveFileBody(
    private val path: Path,
    private val openStream: (Path, Long) -> InputStream = { file, offset ->
        val channel = FileChannel.open(file, StandardOpenOption.READ)
        try {
            Channels.newInputStream(channel.position(offset))
        } catch (t: Throwable) {
            channel.close()
            throw t
        }
    },
) : AsyncRequestBody {
    private val length = Files.size(path)
    private val lock = Any()
    private val cleanupLock = Any()
    private val closeSchedulingLock = Any()
    private val stopped = AtomicBoolean()
    private val streams = mutableSetOf<ReaderSubscription>()
    private val reader = Executors.newSingleThreadExecutor { daemon(it, "fusion-s3-file-reader") }
    // Cancellation must be able to close a stream while the reader is blocked in read(). Coalescing
    // all pending closes into one task bounds the queue even if an underlying close stalls.
    private val streamCloser =
        ThreadPoolExecutor(
            1,
            1,
            0,
            TimeUnit.MILLISECONDS,
            ArrayBlockingQueue<Runnable>(1),
            ThreadFactory { daemon(it, "fusion-s3-stream-close") },
        )
    private var closeScheduled = false
    private var closeRequests = 0L
    private var closeFailure: Throwable? = null
    private var cleanup: Future<*>? = null
    private val wholeFile = RangeBody(0, length)

    override fun contentLength(): Optional<Long> = Optional.of(length)

    override fun subscribe(subscriber: Subscriber<in ByteBuffer>) = wholeFile.subscribe(subscriber)

    override fun splitCloseable(
        configuration: AsyncRequestBodySplitConfiguration
    ): SdkPublisher<CloseableAsyncRequestBody> {
        val partSize = configuration.chunkSizeInBytes()
        require(partSize > 0) { "Multipart part size must be positive" }
        val parts: Sequence<CloseableAsyncRequestBody> =
            generateSequence(0L) { it + partSize }
                .takeWhile { it < length }
                .map { offset -> RangeBody(offset, minOf(partSize, length - offset)) }
        return SdkPublisher.fromIterable(parts.asIterable())
    }

    private inner class RangeBody(val offset: Long, val size: Long) : CloseableAsyncRequestBody {
        val closed = AtomicBoolean()

        override fun contentLength(): Optional<Long> = Optional.of(size)

        override fun subscribe(subscriber: Subscriber<in ByteBuffer>) =
            subscribeRange(subscriber, this)

        override fun close() {
            if (closed.compareAndSet(false, true)) scheduleClose()
        }
    }

    private inner class ReaderSubscription(val input: InputStream, val part: RangeBody) {
        val upstream = AtomicReference<Subscription?>()
        val cancelled = AtomicBoolean()
        val closing = AtomicBoolean()
        var closeStarted = false // Guarded by lock.
        val stream = ArchiveRangeInputStream(input, part.size) { requestClose(this) }

        fun cancel() {
            cancelled.set(true)
            try {
                upstream.get()?.cancel()
            } finally {
                requestClose(this)
            }
        }
    }

    private fun subscribeRange(subscriber: Subscriber<in ByteBuffer>, part: RangeBody) {
        try {
            val subscription =
                synchronized(lock) {
                    check(!stopped.get() && !part.closed.get()) { "Archive file body is closed" }
                    ReaderSubscription(openStream(path, part.offset), part).also { streams.add(it) }
                }
            AsyncRequestBody.fromInputStream(subscription.stream, part.size, reader)
                .subscribe(
                    object : Subscriber<ByteBuffer> {
                        override fun onSubscribe(upstream: Subscription) {
                            subscription.upstream.set(upstream)
                            if (
                                subscription.cancelled.get() || part.closed.get() || stopped.get()
                            ) {
                                subscription.cancel()
                            }
                            subscriber.onSubscribe(
                                object : Subscription {
                                    override fun request(n: Long) {
                                        // File closure can precede delivery of the final buffered
                                        // chunk. Only the upstream subscription governs demand.
                                        upstream.request(n)
                                    }

                                    override fun cancel() = subscription.cancel()
                                }
                            )
                        }

                        override fun onNext(buffer: ByteBuffer) = subscriber.onNext(buffer)

                        override fun onError(t: Throwable) {
                            requestClose(subscription)
                            subscriber.onError(t)
                        }

                        override fun onComplete() {
                            requestClose(subscription)
                            subscriber.onComplete()
                        }
                    }
                )
        } catch (t: Exception) {
            subscriber.onSubscribe(
                object : Subscription {
                    override fun request(n: Long) = Unit

                    override fun cancel() = Unit
                }
            )
            subscriber.onError(t)
        }
    }

    private fun requestClose(subscription: ReaderSubscription) {
        if (subscription.closing.compareAndSet(false, true)) scheduleClose()
    }

    private fun scheduleClose() =
        synchronized(closeSchedulingLock) {
            if (streamCloser.isShutdown) return
            closeRequests++
            if (closeScheduled) return
            closeScheduled = true
            streamCloser.execute {
                while (true) {
                    val generation = synchronized(closeSchedulingLock) { closeRequests }
                    val subscription =
                        synchronized(lock) {
                            streams
                                .firstOrNull {
                                    (it.closing.get() || it.part.closed.get()) && !it.closeStarted
                                }
                                ?.also {
                                    it.closeStarted = true
                                    it.closing.set(true)
                                }
                        }
                    if (subscription == null) {
                        synchronized(closeSchedulingLock) {
                            if (generation == closeRequests) {
                                closeScheduled = false
                                return@execute
                            }
                        }
                        continue
                    }
                    try {
                        if (subscription.part.closed.get() || stopped.get()) subscription.cancel()
                        subscription.input.close()
                        synchronized(lock) { streams.remove(subscription) }
                    } catch (t: Throwable) {
                        synchronized(lock) {
                            if (closeFailure == null) closeFailure = t
                            else closeFailure!!.addSuppressed(t)
                            stopped.set(true)
                        }
                    }
                }
            }
        }

    fun stop(cleanupWorkers: ExecutorService, timeout: Duration) {
        val task =
            synchronized(cleanupLock) {
                stopped.set(true)
                cleanup
                    ?: cleanupWorkers
                        .submit {
                            val deadline = System.nanoTime() + timeout.toNanos()
                            reader.shutdownNow()
                            synchronized(lock) { streams.forEach { it.closing.set(true) } }
                            synchronized(closeSchedulingLock) {
                                scheduleClose()
                                streamCloser.shutdown()
                            }
                            check(
                                streamCloser.awaitTermination(
                                    maxOf(0, deadline - System.nanoTime()),
                                    TimeUnit.NANOSECONDS,
                                )
                            ) {
                                "Archive stream close executor did not terminate"
                            }
                            check(
                                reader.awaitTermination(
                                    maxOf(0, deadline - System.nanoTime()),
                                    TimeUnit.NANOSECONDS,
                                )
                            ) {
                                "Archive file reader executor did not terminate"
                            }
                            synchronized(lock) { closeFailure }?.let { throw it }
                        }
                        .also { cleanup = it }
            }
        // Do not cancel a timed-out cleanup: it can still release the retained resource later.
        task.get(timeout.toMillis(), TimeUnit.MILLISECONDS)
    }
}

/** Enforces the file range independently of SDK read sizing and closes at the last byte. */
internal class ArchiveRangeInputStream(
    input: InputStream,
    private var remaining: Long,
    private val closeAction: (() -> Unit)? = null,
) : FilterInputStream(input) {
    override fun read(): Int {
        if (remaining == 0L) return -1
        val value = `in`.read()
        consumed(if (value < 0) -1 else 1)
        return value
    }

    override fun read(bytes: ByteArray, off: Int, len: Int): Int {
        Objects.checkFromIndexSize(off, len, bytes.size)
        if (len == 0) return 0
        if (remaining == 0L) return -1
        val read = `in`.read(bytes, off, minOf(len.toLong(), remaining).toInt())
        consumed(read)
        return read
    }

    private fun consumed(count: Int) {
        if (count == -1) remaining = 0 else remaining -= count
        if (remaining == 0L) close()
    }

    override fun close() {
        if (closeAction == null) super.close() else closeAction.invoke()
    }
}

private fun daemon(task: Runnable, name: String): Thread =
    Thread(task, name).apply { isDaemon = true }

private suspend fun <T> CompletableFuture<T>.awaitUpload(): T =
    suspendCancellableCoroutine { continuation ->
        continuation.invokeOnCancellation { cancel(true) }
        whenComplete { value, error ->
            if (error == null) continuation.resume(value)
            else
                continuation.resumeWithException(
                    if (error is CompletionException) error.cause ?: error else error
                )
        }
    }
