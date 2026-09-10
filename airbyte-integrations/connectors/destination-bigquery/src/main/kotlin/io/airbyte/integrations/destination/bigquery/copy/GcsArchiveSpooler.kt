/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.copy

import io.airbyte.cdk.load.file.gcs.GcsBlob
import io.airbyte.cdk.load.file.gcs.GcsClient
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.FileNotFoundException
import java.io.IOException
import java.io.InputStream
import java.io.InterruptedIOException
import java.io.OutputStream
import java.net.SocketTimeoutException
import java.nio.file.FileSystemException
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.StandardOpenOption.TRUNCATE_EXISTING
import java.nio.file.StandardOpenOption.WRITE
import java.util.concurrent.ArrayBlockingQueue
import java.util.concurrent.CountDownLatch
import java.util.concurrent.FutureTask
import java.util.concurrent.ThreadPoolExecutor
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.NonCancellable
import kotlinx.coroutines.delay
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.withTimeoutOrNull

/** The caller must retain [path] and poison the archive instead of recycling its transfer slot. */
class GcsArchiveReaderStillActiveException(val path: Path, cause: Throwable? = null) :
    IllegalStateException(
        "GCS archive reader or stream cleanup has not stopped; retain spool $path and stop archiving",
        cause,
    )

/**
 * Copies the existing client's raw gzip response without parsing or recompressing it. The current
 * HMAC/S3 multipart uploader sets no Content-Encoding; the magic check catches decoded responses.
 *
 * The parent owns four transfer slots, creates/deletes the paths, and owns close/shutdown-hook
 * registration for this service. On ordinary failure the path is safe to delete. On
 * [GcsArchiveReaderStillActiveException] it must be retained, and the archive must reject new work.
 */
class GcsArchiveSpooler(
    private val maxBytes: Long = 1024L * 1024 * 1024,
    private val downloadTimeoutMillis: Long = 10 * 60 * 1000L,
    private val cleanupTimeoutMillis: Long = 30 * 1000L,
) : AutoCloseable {
    init {
        require(maxBytes > 0) { "maxBytes must be positive" }
        require(downloadTimeoutMillis > 0) { "downloadTimeoutMillis must be positive" }
        require(cleanupTimeoutMillis > 0) { "cleanupTimeoutMillis must be positive" }
    }

    private val workers = executor("gcs-archive-reader")
    // close() can itself block. Never run it on the caller or on the saturated reader pool.
    private val closers = executor("gcs-archive-close")
    private val lifecycle = Any()
    private val active = mutableSetOf<Download>()
    private var closed = false
    private var poisoned: GcsArchiveReaderStillActiveException? = null
    private val log = KotlinLogging.logger {}

    suspend fun download(client: GcsClient, blob: GcsBlob, path: Path): Long {
        val startedAt = System.nanoTime()
        val download = Download(client, blob, path)
        synchronized(lifecycle) {
            poisoned?.let { throw it }
            check(!closed) { "GCS archive spooler is closed" }
            check(active.size < WORKERS) { "Caller must hold one of four archive transfer slots" }
            active.add(download)
            try {
                workers.execute(download.future)
            } catch (e: RuntimeException) {
                active.remove(download)
                throw e
            }
        }

        try {
            // One deadline for GET, blocking reads, and all three attempts together.
            val bytes = withTimeout(downloadTimeoutMillis) { download.result.await() }
            val elapsedMillis = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - startedAt)
            log.info { "Downloaded GCS archive: bytes=$bytes, durationMillis=$elapsedMillis" }
            return bytes
        } catch (failure: Throwable) {
            download.stop()
            val drained =
                withContext(NonCancellable) {
                    withTimeoutOrNull(cleanupTimeoutMillis) {
                        while (!download.drained()) delay(10)
                        true
                    } ?: false
                }
            if (!drained) {
                val unsafe = GcsArchiveReaderStillActiveException(path, failure)
                synchronized(lifecycle) { poisoned = unsafe }
                throw unsafe
            }
            throw failure
        } finally {
            synchronized(lifecycle) {
                if (download.drained()) active.remove(download)
            }
        }
    }

    override fun close() {
        val downloads =
            synchronized(lifecycle) {
                if (closed) return
                closed = true
                active.toList()
            }
        downloads.forEach { it.stop() }
        workers.shutdownNow()
        closers.shutdown()
        val started = System.nanoTime()
        val budget = TimeUnit.MILLISECONDS.toNanos(cleanupTimeoutMillis)
        var interruption: InterruptedException? = null
        try {
            for (download in downloads) {
                for (latch in listOf(download.stopped, download.closeStopped)) {
                    val remaining = (budget - (System.nanoTime() - started)).coerceAtLeast(0)
                    if (!latch.await(remaining, TimeUnit.NANOSECONDS)) break
                }
            }
        } catch (e: InterruptedException) {
            interruption = e
            Thread.currentThread().interrupt()
        } finally {
            closers.shutdownNow()
        }
        downloads.firstOrNull { !it.drained() }?.let {
            val unsafe = GcsArchiveReaderStillActiveException(it.path, interruption)
            synchronized(lifecycle) { poisoned = unsafe }
            throw unsafe
        }
    }

    private inner class Download(
        private val client: GcsClient,
        private val blob: GcsBlob,
        val path: Path,
    ) {
        val result = CompletableDeferred<Long>()
        val stopped = CountDownLatch(1)
        val closeStopped = CountDownLatch(1)
        private val lock = Any()
        private var started = false
        private var finished = false
        private var running = false
        private var cancelled = false
        private var stream: InputStream? = null

        val future = FutureTask<Unit> {
            synchronized(lock) {
                if (cancelled) return@FutureTask
                started = true
            }
            val outcome = runCatching {
                runBlocking {
                    synchronized(lock) {
                        ensureRunning()
                        running = true
                    }
                    try {
                        copyWithRetries()
                    } finally {
                        synchronized(lock) {
                            running = false
                            if (finished) stopped.countDown()
                        }
                    }
                }
            }
            synchronized(lock) {
                finished = true
                if (!running) stopped.countDown()
            }
            // A cancelled Future is not proof of completion. Also account for clients which invoke
            // their callback on a different thread: runBlocking can exit on interruption first.
            outcome.fold(result::complete, result::completeExceptionally)
            Unit
        }

        fun drained(): Boolean =
            stopped.count == 0L && synchronized(lock) { !cancelled || closeStopped.count == 0L }

        fun stop() =
            synchronized(lock) {
                if (cancelled) return@synchronized
                cancelled = true
                future.cancel(true)
                if (!started) {
                    finished = true
                    stopped.countDown()
                }
                result.completeExceptionally(CancellationException("GCS archive download stopped"))
                val input = stream
                if (input == null || stopped.count == 0L) {
                    closeStopped.countDown()
                } else {
                    // At most one closer per download, on a fixed pool with a bounded queue.
                    closers.execute {
                        try {
                            input.close()
                        } catch (_: Exception) {
                            // Only the stopped latch proves that abort actually released the reader.
                        } finally {
                            closeStopped.countDown()
                        }
                    }
                }
            }

        private fun ensureRunning() =
            synchronized(lock) {
                if (cancelled || finished || Thread.currentThread().isInterrupted) {
                    throw CancellationException("GCS archive download stopped")
                }
            }

        private suspend fun copyWithRetries(): Long {
            repeat(3) { attempt ->
                ensureRunning()
                try {
                    // Truncate even if GET fails before delivering a response body.
                    return spoolOutput(path).use { output ->
                        client.get(blob.key) { input ->
                            synchronized(lock) {
                                ensureRunning()
                                stream = input
                            }
                            input.use { copy(it, output) }
                        }
                    }
                } catch (e: IOException) {
                    ensureRunning()
                    if (attempt == 2 || !isTransient(e)) throw e
                    // Do not log keys, paths, exception messages, or credentials.
                    log.warn {
                        "Retrying GCS archive download after transient I/O failure (attempt ${attempt + 2}/3)"
                    }
                } finally {
                    synchronized(lock) { stream = null }
                }
            }
            error("Unreachable")
        }

        private fun copy(input: InputStream, output: OutputStream): Long {
            val buffer = ByteArray(64 * 1024)
            var size = 0L
            while (true) {
                ensureRunning()
                // Read at most one byte beyond the budget to detect overflow without writing it.
                val remaining = maxBytes - size
                val length = if (remaining >= buffer.size) buffer.size else remaining.toInt() + 1
                val count = input.read(buffer, 0, length)
                ensureRunning()
                if (count < 0) break
                if (count == 0) continue
                check(count <= remaining) { "GCS archive exceeds maxBytes ($maxBytes): $path" }
                for (index in 0 until minOf(count, (2L - size).coerceAtLeast(0).toInt())) {
                    val expected = if (size + index == 0L) 0x1f else 0x8b
                    check(buffer[index].toInt() and 0xff == expected) {
                        "GCS archive response is missing gzip magic (possibly decoded): ${blob.key}"
                    }
                }
                output.write(buffer, 0, count)
                size += count
            }
            check(size >= 2) { "GCS archive response is missing gzip magic: ${blob.key}" }
            return size
        }
    }

    private class SpoolIOException(cause: IOException) : IOException("Cannot write GCS spool", cause)

    private fun spoolOutput(path: Path): OutputStream =
        object : OutputStream() {
            // No CREATE: the caller must create and account for the path first.
            private val delegate = spoolIo { Files.newOutputStream(path, WRITE, TRUNCATE_EXISTING) }

            override fun write(value: Int) = spoolIo { delegate.write(value) }

            override fun write(bytes: ByteArray, offset: Int, length: Int) =
                spoolIo { delegate.write(bytes, offset, length) }

            override fun close() = spoolIo { delegate.close() }
        }

    private inline fun <T> spoolIo(block: () -> T): T =
        try {
            block()
        } catch (e: IOException) {
            throw SpoolIOException(e)
        }

    private fun isTransient(e: IOException): Boolean =
        e !is SpoolIOException &&
            e !is FileNotFoundException &&
            e !is FileSystemException &&
            (e !is InterruptedIOException || e is SocketTimeoutException)

    private companion object {
        const val WORKERS = 4

        fun executor(name: String): ThreadPoolExecutor {
            val sequence = AtomicInteger()
            return ThreadPoolExecutor(
                WORKERS,
                WORKERS,
                0L,
                TimeUnit.MILLISECONDS,
                ArrayBlockingQueue(WORKERS),
                { task -> Thread(task, "$name-${sequence.incrementAndGet()}").apply { isDaemon = true } },
                ThreadPoolExecutor.AbortPolicy(),
            )
        }
    }
}
