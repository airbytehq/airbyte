/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.fusion.testing

import io.airbyte.cdk.fusion.FusionUploader
import java.nio.file.Files
import java.nio.file.Path
import java.util.concurrent.CompletableFuture
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit
import java.util.concurrent.TimeoutException

/** Captures closed-file uploads and lets tests control when each upload succeeds or fails. */
class ControlledFusionUploader : FusionUploader {
    data class Upload(
        val path: Path,
        val key: String,
        val metadata: Map<String, String>,
        val bytes: ByteArray,
        val result: CompletableFuture<Unit>,
    )

    data class JsonUpload(val key: String, val bytes: ByteArray)

    private val lock = Any()
    private val capturedUploads = mutableListOf<Upload>()
    private val capturedJsonUploads = mutableListOf<JsonUpload>()
    private val started = LinkedBlockingQueue<Upload>()
    private var closed = false

    /** Snapshots of all requests, including requests already returned by [awaitUpload]. */
    val uploads: List<Upload>
        get() = synchronized(lock) { capturedUploads.toList() }

    val jsonUploads: List<JsonUpload>
        get() = synchronized(lock) { capturedJsonUploads.toList() }

    override fun upload(
        path: Path,
        key: String,
        metadata: Map<String, String>,
    ): CompletableFuture<Unit> =
        synchronized(lock) {
            check(!closed) { "ControlledFusionUploader is closed" }
            val upload =
                Upload(path, key, metadata.toMap(), Files.readAllBytes(path), CompletableFuture())
            capturedUploads.add(upload)
            started.add(upload)
            upload.result
        }

    override fun uploadJson(bytes: ByteArray, key: String): CompletableFuture<Unit> =
        synchronized(lock) {
            check(!closed) { "ControlledFusionUploader is closed" }
            capturedJsonUploads.add(JsonUpload(key, bytes.copyOf()))
            CompletableFuture.completedFuture(Unit)
        }

    /** Blocks until the next file upload is captured; call from a test thread, not its worker. */
    fun awaitUpload(timeout: Long = 10, unit: TimeUnit = TimeUnit.SECONDS): Upload {
        require(timeout >= 0) { "timeout must be nonnegative" }
        return started.poll(timeout, unit)
            ?: throw TimeoutException("No Fusion file upload started within $timeout $unit")
    }

    /** Releases blocked callers during cleanup. Does not delete files owned by the connector. */
    override fun close() {
        val pending =
            synchronized(lock) {
                if (closed) return
                closed = true
                capturedUploads.toList()
            }
        pending.forEach {
            it.result.completeExceptionally(
                IllegalStateException("ControlledFusionUploader closed before upload completed")
            )
        }
    }
}
