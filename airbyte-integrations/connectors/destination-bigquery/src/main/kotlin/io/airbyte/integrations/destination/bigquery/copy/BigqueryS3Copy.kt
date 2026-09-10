/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.destination.bigquery.copy

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.file.gcs.GcsBlob
import io.airbyte.cdk.load.file.gcs.GcsClient
import io.airbyte.integrations.destination.bigquery.spec.BatchedStandardInsertConfiguration
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Files
import java.nio.file.Path
import java.util.Collections
import java.util.IdentityHashMap
import java.util.UUID
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.sync.withPermit
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout

data class BigqueryCopyContext(
    val streamKey: String,
    val generationId: Long,
    val syncId: Long,
    val schemaId: String,
    val runId: UUID,
    val runPath: String,
)

interface BigqueryS3Copy : AutoCloseable {
    fun validate(catalog: DestinationCatalog)

    suspend fun prepare(catalog: DestinationCatalog)

    /** False means setup failed/closed; a failed sync must discard any zero-row checkpoints. */
    suspend fun metadataReady(): Boolean

    fun context(stream: DestinationStream): BigqueryCopyContext?

    fun startStandardInsertBatch(context: BigqueryCopyContext): StandardInsertArchiveBatch

    suspend fun copyCompletedGcsObject(
        storageClient: GcsClient,
        remoteObject: GcsBlob,
        context: BigqueryCopyContext,
        loadedRecordCount: Long,
    )
}

object DisabledBigqueryS3Copy : BigqueryS3Copy {
    override fun validate(catalog: DestinationCatalog) = Unit

    override suspend fun prepare(catalog: DestinationCatalog) = Unit

    override suspend fun metadataReady(): Boolean = true

    override fun context(stream: DestinationStream): BigqueryCopyContext? = null

    override fun startStandardInsertBatch(
        context: BigqueryCopyContext
    ): StandardInsertArchiveBatch = error("Cannot start a batch when Fusion S3 copying is disabled")

    override suspend fun copyCompletedGcsObject(
        storageClient: GcsClient,
        remoteObject: GcsBlob,
        context: BigqueryCopyContext,
        loadedRecordCount: Long,
    ) = Unit

    override fun close() = Unit
}

/** One process owns one run and four transfer slots, including socket partitions. */
@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION"],
    justification = "Kotlin coroutine resume stubs pass null placeholders for saved arguments",
)
class EnabledBigqueryS3Copy(
    private val config: S3CopyConfiguration,
    private val bigqueryConfiguration: BigqueryConfiguration,
    private val metadata: BigqueryCopyMetadata,
    private val runId: UUID,
    private val uploaderFactory: () -> ArchiveUploader = { S3ArchiveUploader(config) },
    private val spooler: GcsArchiveSpooler = GcsArchiveSpooler(),
    private val spoolDirectory: Path? = null,
    private val operationTimeoutMillis: Long = 30 * 60 * 1000L,
    standardInsertMaxBatchBytes: Long = 1L shl 30,
    standardInsertMaxTotalBytes: Long = 4L shl 30,
) : BigqueryS3Copy {
    private val log = KotlinLogging.logger {}
    private val resources = Any()
    private var uploaderInstance: ArchiveUploader? = null
    private val ready = CompletableDeferred<Boolean>()
    private val uploader: ArchiveUploader
        get() {
            synchronized(resources) {
                checkHealthy()
                uploaderInstance?.let {
                    return it
                }
            }
            val created = uploaderFactory()
            val selected =
                synchronized(resources) {
                    if (closed.get() || poisoned.get()) null
                    else uploaderInstance ?: created.also { uploaderInstance = it }
                }
            // close() may have run while the factory was building its clients.
            if (selected !== created) created.close()
            return selected ?: error("Fusion S3 archive closed while constructing uploader")
        }

    private val slots = Semaphore(4)
    private val preparation = Mutex()
    private val closed = AtomicBoolean(false)
    private val poisoned = AtomicBoolean(false)
    private val copiedObjects = AtomicLong()
    private val copiedBytes = AtomicLong()
    private val failures = AtomicLong()
    private val retainedBytes = AtomicLong()
    private val standardInsertSpools =
        StandardInsertSpoolManager(
            directory = spoolDirectory,
            maxBatchBytes = standardInsertMaxBatchBytes,
            maxTotalBytes = standardInsertMaxTotalBytes,
            hasActiveReader = ::hasActiveReader,
            onRetained = { path, failure ->
                poisoned.set(true)
                retainedBytes.addAndGet(runCatching { Files.size(path) }.getOrDefault(0))
                log.error(failure) {
                    "Fusion archive retaining standard insert spool $path and disabling further transfers"
                }
            },
        )
    @Volatile private var contexts: Map<DestinationStream.Descriptor, BigqueryCopyContext>? = null
    private val shutdownHook = Thread({ close() }, "bigquery-fusion-shutdown")

    init {
        Runtime.getRuntime().addShutdownHook(shutdownHook)
    }

    override fun validate(catalog: DestinationCatalog) {
        checkHealthy()
        val duplicates =
            catalog.streams.groupingBy { it.unmappedName }.eachCount().filterValues { it > 1 }
        if (duplicates.isNotEmpty()) {
            throw SystemErrorException(
                "Fusion S3 routing requires unique stream names across namespaces in a connection: ${duplicates.keys}"
            )
        }
        catalog.streams.forEach { stream ->
            if (
                stream.minimumGenerationId != 0L &&
                    stream.minimumGenerationId != stream.generationId
            ) {
                throw SystemErrorException(
                    "Cannot execute a hybrid refresh - current generation ${stream.generationId}; minimum generation ${stream.minimumGenerationId}"
                )
            }
        }
    }

    override suspend fun prepare(catalog: DestinationCatalog) {
        preparation.withLock {
            validate(catalog)
            if (contexts != null) return
            try {
                withTimeout(operationTimeoutMillis) {
                    uploader.validateCredentials()
                    val prepared =
                        catalog.streams.associate { stream ->
                            val descriptor = metadata.descriptor(stream)
                            val runPath = metadata.runPath(stream)
                            putJson("$runPath/schema.json", descriptor)
                            if (stream.minimumGenerationId > 0) {
                                putJson("$runPath/generation-cutoff.json", metadata.cutoff(stream))
                            }
                            stream.mappedDescriptor to
                                BigqueryCopyContext(
                                    metadata.streamKey(stream),
                                    stream.generationId,
                                    stream.syncId,
                                    descriptor.getValue("schema_id") as String,
                                    runId,
                                    runPath,
                                )
                        }
                    contexts = prepared
                    checkHealthy()
                    ready.complete(true)
                    log.info {
                        "Fusion S3 run metadata complete: run=$runId streams=${prepared.size} bucket=${config.bucket}"
                    }
                }
            } catch (t: Throwable) {
                poisoned.set(true)
                ready.complete(false)
                throw archiveFailure("Fusion S3 run metadata preparation failed", t)
            }
        }
    }

    override suspend fun metadataReady(): Boolean =
        ready.await() && !closed.get() && !poisoned.get()

    override fun context(stream: DestinationStream): BigqueryCopyContext {
        checkHealthy()
        return contexts?.get(stream.mappedDescriptor)
            ?: throw SystemErrorException(
                "Fusion S3 run metadata is not prepared for ${stream.mappedDescriptor}"
            )
    }

    override fun startStandardInsertBatch(
        context: BigqueryCopyContext
    ): StandardInsertArchiveBatch {
        checkHealthy()
        check(bigqueryConfiguration.loadingMethod is BatchedStandardInsertConfiguration) {
            "NDJSON archive batches require BigQuery batched standard inserts"
        }
        check(contexts?.values?.contains(context) == true) { "Unknown Fusion run context" }
        val batchId = UUID.randomUUID()
        val key = "${context.runPath}/batches/$batchId.jsonl"
        return standardInsertSpools.create { path, inputRecordCount, loadedRecordCount ->
            val started = System.nanoTime()
            try {
                withTimeout(operationTimeoutMillis) {
                    slots.withPermit {
                        checkHealthy()
                        log.info {
                            "Fusion S3 archive started: run=$runId batch=$batchId key=$key slot_wait_ms=${(System.nanoTime() - started) / 1_000_000}"
                        }
                        val bytes = Files.size(path)
                        uploader.upload(
                            path,
                            key,
                            "application/x-ndjson",
                            batchMetadata(context, batchId, loadedRecordCount) +
                                ("input-record-count" to inputRecordCount.toString()),
                        )
                        copiedObjects.incrementAndGet()
                        copiedBytes.addAndGet(bytes)
                        log.info {
                            "Fusion S3 archive complete: run=$runId batch=$batchId key=$key bytes=$bytes input_records=$inputRecordCount loaded_records=$loadedRecordCount duration_ms=${(System.nanoTime() - started) / 1_000_000}"
                        }
                    }
                }
            } catch (t: Throwable) {
                failures.incrementAndGet()
                log.error(t) {
                    "Fusion S3 archive failed: run=$runId batch=$batchId key=$key; batch cannot complete"
                }
                throw archiveFailure("Fusion S3 archive failed for run=$runId batch=$batchId", t)
            }
        }
    }

    private fun batchMetadata(
        context: BigqueryCopyContext,
        batchId: UUID,
        loadedRecordCount: Long,
    ): Map<String, String> =
        mapOf(
            "format-version" to "1",
            "workspace-id" to config.workspaceId.toString(),
            "source-id" to config.sourceId.toString(),
            "connection-id" to config.connectionId.toString(),
            "stream-key" to context.streamKey,
            "generation-id" to context.generationId.toString(),
            "sync-id" to context.syncId.toString(),
            "run-id" to runId.toString(),
            "batch-id" to batchId.toString(),
            "schema-id" to context.schemaId,
            "loaded-record-count" to loadedRecordCount.toString(),
        )

    override suspend fun copyCompletedGcsObject(
        storageClient: GcsClient,
        remoteObject: GcsBlob,
        context: BigqueryCopyContext,
        loadedRecordCount: Long,
    ) {
        checkHealthy()
        check(bigqueryConfiguration.loadingMethod is GcsStagingConfiguration) {
            "GCS object copying requires BigQuery GCS staging"
        }
        check(contexts?.values?.contains(context) == true) { "Unknown Fusion run context" }
        val batchId = UUID.randomUUID()
        val key = "${context.runPath}/batches/$batchId.csv.gz"
        val started = System.nanoTime()
        try {
            withTimeout(operationTimeoutMillis) {
                slots.withPermit {
                    checkHealthy()
                    val slotWaitMillis = (System.nanoTime() - started) / 1_000_000
                    log.info {
                        "Fusion S3 archive started: run=$runId batch=$batchId key=$key slot_wait_ms=$slotWaitMillis"
                    }
                    withSpool { path ->
                        val bytes = spooler.download(storageClient, remoteObject, path)
                        uploader.upload(
                            path,
                            key,
                            "application/gzip",
                            batchMetadata(context, batchId, loadedRecordCount),
                        )
                        copiedObjects.incrementAndGet()
                        copiedBytes.addAndGet(bytes)
                        log.info {
                            "Fusion S3 archive complete: run=$runId batch=$batchId key=$key bytes=$bytes loaded_records=$loadedRecordCount duration_ms=${(System.nanoTime() - started) / 1_000_000}"
                        }
                    }
                }
            }
        } catch (t: Throwable) {
            failures.incrementAndGet()
            log.error(t) {
                "Fusion S3 archive failed: run=$runId batch=$batchId key=$key; retaining GCS object"
            }
            throw archiveFailure("Fusion S3 archive failed for run=$runId batch=$batchId", t)
        }
    }

    private suspend fun putJson(key: String, value: Any) {
        withSpool { path ->
            withContext(Dispatchers.IO) { Files.write(path, metadata.serialize(value)) }
            uploader.upload(path, key, "application/json")
        }
    }

    private suspend fun withSpool(block: suspend (Path) -> Unit) {
        val path =
            if (spoolDirectory == null) Files.createTempFile("bigquery-fusion-", ".csv.gz")
            else Files.createTempFile(spoolDirectory, "bigquery-fusion-", ".csv.gz")
        var retain = false
        try {
            block(path)
        } catch (t: Throwable) {
            retain = hasActiveReader(t)
            throw t
        } finally {
            if (retain) {
                poisoned.set(true)
                retainedBytes.addAndGet(runCatching { Files.size(path) }.getOrDefault(0))
                log.error {
                    "Fusion archive reader did not stop; retaining spool $path and disabling further transfers"
                }
            } else {
                try {
                    Files.deleteIfExists(path)
                } catch (t: Throwable) {
                    poisoned.set(true)
                    retainedBytes.addAndGet(runCatching { Files.size(path) }.getOrDefault(0))
                    throw t
                }
            }
        }
    }

    private fun checkHealthy() {
        check(!closed.get()) { "Fusion S3 archive is closed" }
        check(!poisoned.get()) {
            "Fusion S3 archive cannot continue after incomplete preparation or cleanup"
        }
    }

    /** Preserve the retention signal even when a coroutine or SDK wraps a cleanup failure. */
    private fun hasActiveReader(failure: Throwable): Boolean {
        val visited = Collections.newSetFromMap(IdentityHashMap<Throwable, Boolean>())
        val pending = ArrayDeque<Throwable>()
        pending.add(failure)
        while (pending.isNotEmpty()) {
            val current = pending.removeFirst()
            if (!visited.add(current)) continue
            if (
                current is ArchiveReaderStillActiveException ||
                    current is GcsArchiveReaderStillActiveException
            )
                return true
            current.cause?.let(pending::add)
            pending.addAll(current.suppressed)
        }
        return false
    }

    private fun archiveFailure(message: String, cause: Throwable): Throwable =
        if (cause is CancellationException || cause is Error || cause is SystemErrorException) cause
        else SystemErrorException(message, cause)

    override fun close() {
        if (closed.compareAndSet(false, true)) {
            ready.complete(false)
            var failure: Throwable? = null
            fun closeResource(close: () -> Unit) {
                try {
                    close()
                } catch (error: Throwable) {
                    val first = failure
                    if (first == null) failure = error
                    else if (first !== error) first.addSuppressed(error)
                }
            }
            closeResource { standardInsertSpools.close() }
            closeResource { spooler.close() }
            closeResource { synchronized(resources) { uploaderInstance }?.close() }
            runCatching { Runtime.getRuntime().removeShutdownHook(shutdownHook) }
            log.info {
                "Fusion S3 archive totals: run=$runId objects=${copiedObjects.get()} bytes=${copiedBytes.get()} failures=${failures.get()} retained_spool_bytes=${retainedBytes.get()}"
            }
            failure?.let { throw it }
        }
    }
}
