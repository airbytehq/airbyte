/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.copy

import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.StandardOpenOption.APPEND
import java.nio.file.StandardOpenOption.WRITE
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive

interface StandardInsertArchiveBatch : AutoCloseable {
    fun append(bytes: ByteArray)

    suspend fun complete(loadedRecordCount: Long)
}

/**
 * Share one manager across the process's standard-insert streams. Byte reservations never wait for
 * capacity or acquire transfer permits: interleaved batches must all be able to accept records.
 * Upload callbacks own their readers and must signal any reader that outlives a failed callback via
 * [hasActiveReader]. Retained files remain charged to the manager, including after close.
 */
internal class StandardInsertSpoolManager(
    private val directory: Path? = null,
    private val maxBatchBytes: Long = 1L shl 30,
    private val maxTotalBytes: Long = 4L shl 30,
    private val hasActiveReader: (Throwable) -> Boolean,
    private val onRetained: (Path, Throwable) -> Unit,
) : AutoCloseable {
    init {
        require(maxBatchBytes > 0) { "Fusion standard-insert maxBatchBytes must be positive" }
        require(maxTotalBytes > 0) { "Fusion standard-insert maxTotalBytes must be positive" }
    }

    // Covers file mutation as well as accounting. No descriptors survive an append call, and no
    // suspend functions or caller callbacks run under this lock.
    private val lifecycle = Any()
    private val batches = mutableSetOf<Batch>()
    private var totalBytes = 0L
    private var closed = false

    fun create(
        upload: suspend (path: Path, inputRecordCount: Long, loadedRecordCount: Long) -> Unit
    ): StandardInsertArchiveBatch =
        synchronized(lifecycle) {
            require(!closed) { "Fusion standard-insert spool manager is closed" }
            Batch(upload).also { batches.add(it) }
        }

    override fun close() {
        val retained =
            synchronized(lifecycle) {
                if (closed) return
                closed = true
                batches.toList().mapNotNull { it.closeLocked() }
            }
        retained.forEach { it.report() }
        retained.firstOrNull()?.let { first ->
            retained.drop(1).forEach { suppress(first.failure, it.failure) }
            throw first.failure
        }
    }

    private enum class State {
        OPEN,
        UPLOADING,
        COMPLETED,
        FAILED,
    }

    private inner class Batch(private val upload: suspend (Path, Long, Long) -> Unit) :
        StandardInsertArchiveBatch {
        private var state = State.OPEN
        private var batchClosed = false
        private var path: Path? = null
        private var bytes = 0L
        private var inputRecordCount = 0L

        override fun append(bytes: ByteArray) {
            var retained: Retained? = null
            try {
                synchronized(lifecycle) {
                    requireOpen()
                    try {
                        val size = bytes.size.toLong()
                        require(size <= maxBatchBytes - this.bytes) {
                            "Fusion standard-insert spool exceeds maxBatchBytes ($maxBatchBytes)"
                        }
                        require(size <= maxTotalBytes - totalBytes) {
                            "Fusion standard-insert spools exceed maxTotalBytes ($maxTotalBytes)"
                        }
                        val target = path ?: newPath().also { path = it }
                        // Reserve before writing: a partial write or failed close still consumes
                        // budget until deletion is known to have succeeded.
                        this.bytes += size
                        totalBytes += size
                        Files.newOutputStream(target, WRITE, APPEND).use { it.write(bytes) }
                        inputRecordCount++
                    } catch (failure: Throwable) {
                        state = State.FAILED
                        retained = cleanupLocked(failure)
                        throw failure
                    }
                }
            } finally {
                retained?.report()
            }
        }

        override suspend fun complete(loadedRecordCount: Long) {
            var retained: Retained? = null
            val target =
                try {
                    synchronized(lifecycle) {
                        requireNotClosed()
                        if (state == State.COMPLETED) return
                        requireOpen()
                        try {
                            require(loadedRecordCount >= 0) {
                                "Fusion standard-insert loadedRecordCount must be nonnegative"
                            }
                            if (inputRecordCount == 0L) {
                                require(loadedRecordCount == 0L) {
                                    "Fusion standard-insert cannot load records from an empty batch"
                                }
                                state = State.COMPLETED
                                batches.remove(this)
                                return
                            }
                            // append has already closed the writer. Claim cleanup before releasing
                            // the lock so even close racing callback startup cannot unlink the
                            // file.
                            state = State.UPLOADING
                            requireNotNull(path)
                        } catch (failure: Throwable) {
                            state = State.FAILED
                            retained = cleanupLocked(failure)
                            throw failure
                        }
                    }
                } finally {
                    retained?.report()
                }

            var failure: Throwable? = null
            var retain = false
            try {
                currentCoroutineContext().ensureActive()
                upload(target, inputRecordCount, loadedRecordCount)
                currentCoroutineContext().ensureActive()
            } catch (error: Throwable) {
                failure = error
                retain =
                    try {
                        hasActiveReader(error)
                    } catch (inspectionFailure: Throwable) {
                        // If reader status cannot be established, deletion is unsafe.
                        suppress(error, inspectionFailure)
                        true
                    }
            } finally {
                val notice =
                    synchronized(lifecycle) {
                        if (failure == null) {
                            try {
                                requireNotClosed()
                            } catch (closedFailure: IllegalArgumentException) {
                                failure = closedFailure
                            }
                        }
                        state = if (failure == null) State.COMPLETED else State.FAILED
                        cleanupLocked(failure, retain).also { if (it != null) state = State.FAILED }
                    }
                notice?.report()
                if (failure == null && notice != null) failure = notice.failure
            }
            failure?.let { throw it }
        }

        override fun close() {
            val retained = synchronized(lifecycle) { closeLocked() }
            retained?.report()
            if (retained != null) throw retained.failure
        }

        fun closeLocked(): Retained? {
            if (batchClosed) return null
            batchClosed = true
            // The callback's finally is the only owner of cleanup once upload has been claimed.
            return if (state == State.UPLOADING) null else cleanupLocked()
        }

        private fun requireNotClosed() {
            require(!closed && !batchClosed) { "Fusion standard-insert archive batch is closed" }
        }

        private fun requireOpen() {
            requireNotClosed()
            require(state == State.OPEN) {
                "Fusion standard-insert archive batch cannot accept work in state $state"
            }
        }

        private fun newPath(): Path =
            if (directory == null) Files.createTempFile("bigquery-fusion-", ".jsonl")
            else Files.createTempFile(directory, "bigquery-fusion-", ".jsonl")

        /**
         * Must hold lifecycle; retained paths are detached so close can never retry their deletion.
         */
        private fun cleanupLocked(failure: Throwable? = null, retain: Boolean = false): Retained? {
            batches.remove(this)
            val target = path ?: return null
            path = null
            if (retain) return Retained(target, requireNotNull(failure))
            try {
                Files.deleteIfExists(target)
                totalBytes -= bytes
                bytes = 0
            } catch (deletionFailure: Throwable) {
                if (failure != null) suppress(failure, deletionFailure)
                return Retained(target, failure ?: deletionFailure)
            }
            return null
        }
    }

    private inner class Retained(private val path: Path, val failure: Throwable) {
        fun report() {
            try {
                onRetained(path, failure)
            } catch (notificationFailure: Throwable) {
                // Reporting and teardown must not replace the original upload/append exception.
                suppress(failure, notificationFailure)
            }
        }
    }

    private fun suppress(original: Throwable, secondary: Throwable) {
        if (original !== secondary) original.addSuppressed(secondary)
    }
}
