/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.copy

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.SystemErrorException
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.json.AirbyteTypeToJsonSchema
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.integrations.destination.snowflake.schema.SnowflakeColumnManager
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path
import java.security.MessageDigest
import java.time.Instant
import java.util.UUID
import java.util.concurrent.Semaphore
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext

data class CsvCopyContext(
    val streamKey: String,
    val generationId: Long,
    val syncId: Long,
    val schemaId: String,
    val runId: UUID,
    val connectionId: UUID,
    val runPath: String,
    val epochSeconds: Long,
)

interface SnowflakeS3Copy : AutoCloseable {
    suspend fun prepare(catalog: DestinationCatalog)
    suspend fun complete(stream: DestinationStream)
    fun context(stream: DestinationStream): CsvCopyContext?
    suspend fun upload(path: Path, context: CsvCopyContext, recordCount: Int, batchId: UUID)
}

object DisabledSnowflakeS3Copy : SnowflakeS3Copy {
    override suspend fun prepare(catalog: DestinationCatalog) = Unit
    override suspend fun complete(stream: DestinationStream) = Unit
    override fun context(stream: DestinationStream): CsvCopyContext? = null
    override suspend fun upload(
        path: Path,
        context: CsvCopyContext,
        recordCount: Int,
        batchId: UUID
    ) = Unit
    override fun close() = Unit
}

@SuppressFBWarnings(
    value = ["NP_NONNULL_PARAM_VIOLATION"],
    justification = "Kotlin coroutine resume stubs pass null placeholders for saved arguments",
)
class EnabledSnowflakeS3Copy(
    private val config: S3CopyConfiguration,
    private val columnManager: SnowflakeColumnManager,
    private val snowflakeConfiguration: SnowflakeConfiguration,
    private val uploader: SnowflakeCopyUploader = S3CsvUploader(config),
    private val configuredCatalog: ConfiguredAirbyteCatalog? = null,
) : SnowflakeS3Copy {
    private val epochSeconds = Instant.now().epochSecond
    private val runId = UUID.randomUUID()
    private val metadata = S3CopyMetadata(config, runId, epochSeconds)
    private val log = KotlinLogging.logger {}
    private val completion = Mutex()
    private val completedStreams = mutableSetOf<DestinationStream>()
    private val slots = Semaphore(4)
    private val closed = AtomicBoolean(false)
    private val shutdownHook = Thread { close() }
    private val contexts = mutableMapOf<DestinationStream, CsvCopyContext>()

    init {
        Runtime.getRuntime().addShutdownHook(shutdownHook)
    }

    override suspend fun prepare(catalog: DestinationCatalog) {
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
        val runPaths =
            catalog.streams.associateWith { stream ->
                S3CopyPaths.run(config, stream.unmappedName, runId, epochSeconds)
            }
        catalog.streams.forEach { stream ->
            val schema = descriptor(stream)
            val schemaId = sha(schema)
            val key = streamKey(stream)
            val runPath = runPaths.getValue(stream)
            putJson("${runPath}schema.json", metadata.schema(stream, schema, schemaId))
            contexts[stream] =
                CsvCopyContext(
                    key,
                    stream.generationId,
                    stream.syncId,
                    schemaId,
                    runId,
                    config.connectionId,
                    runPath,
                    epochSeconds
                )
        }
    }

    override suspend fun complete(stream: DestinationStream) {
        completion.withLock {
            check(!closed.get()) { "Fusion archive is closed" }
            val context =
                checkNotNull(contexts[stream]) { "Fusion stream metadata is not prepared" }
            if (stream in completedStreams) return
            val key = "${context.runPath}batches/stream_complete.json"
            withContext(Dispatchers.IO) { putJson(key, metadata.streamComplete(stream)) }
            completedStreams.add(stream)
            log.info { "Fusion S3 stream complete: run=$runId job_id=${stream.syncId} key=$key" }
        }
    }

    override fun context(stream: DestinationStream) = contexts[stream]

    override suspend fun upload(
        path: Path,
        context: CsvCopyContext,
        recordCount: Int,
        batchId: UUID
    ) {
        withContext(Dispatchers.IO) {
            slots.acquire()
            try {
                val key = "${context.runPath}batches/$batchId.csv.gz"
                uploader.upload(path, key, metadata.batch(context, recordCount, batchId)).get()
            } finally {
                slots.release()
            }
        }
    }

    private fun streamKey(stream: DestinationStream) =
        sha(mapOf("namespace" to stream.unmappedNamespace, "name" to stream.unmappedName))
    private fun sha(value: Any): String =
        MessageDigest.getInstance("SHA-256").digest(Jsons.writeValueAsBytes(value)).joinToString(
            ""
        ) { "%02x".format(it) }
    private fun putJson(key: String, value: Any) {
        uploader.uploadJson(Jsons.writeValueAsBytes(value), key).get()
    }
    private fun descriptor(stream: DestinationStream): Map<String, Any> {
        val columns = LinkedHashMap<String, Any>()
        columnManager.getMetaColumns().forEach { (n, t) ->
            columns[n] = mapOf("type" to t.type, "nullable" to t.nullable)
        }
        stream.tableSchema.columnSchema.finalSchema.forEach { (n, t) ->
            columns[n] = mapOf("type" to t.type, "nullable" to t.nullable)
        }
        // DestinationStream drops configured keys/cursors for append streams; read the input
        // catalog.
        val configured =
            configuredCatalog?.streams?.singleOrNull {
                it.stream.namespace == stream.unmappedNamespace &&
                    it.stream.name == stream.unmappedName
            }
        val primaryKey = configured?.primaryKey.orEmpty()
        val cursor = configured?.cursorField.orEmpty()
        // Preserve the input JSON Schema, including annotations lost by CDK type conversion.
        // Raw mode changes finalSchema, but retains the source fields in inputSchema.
        val sourceSchema =
            configured?.stream?.jsonSchema
                ?: AirbyteTypeToJsonSchema()
                    .convert(ObjectType(LinkedHashMap(stream.tableSchema.columnSchema.inputSchema)))
        return mapOf(
            "source_schema" to sourceSchema,
            "primary_key" to primaryKey,
            "cursor" to cursor,
            "contract_version" to 1,
            "connector" to "destination-snowflake",
            "format" to "snowflake-load-csv-gzip-v1",
            "stream" to
                mapOf("namespace" to stream.unmappedNamespace, "name" to stream.unmappedName),
            "mapped_stream" to
                mapOf(
                    "namespace" to stream.mappedDescriptor.namespace,
                    "name" to stream.mappedDescriptor.name
                ),
            "table" to
                mapOf(
                    "namespace" to stream.tableSchema.tableNames.finalTableName!!.namespace,
                    "name" to stream.tableSchema.tableNames.finalTableName!!.name
                ),
            "mode" to if (snowflakeConfiguration.legacyRawTablesOnly) "raw" else "schema",
            "columns" to columns,
            "input_to_final" to stream.tableSchema.columnSchema.inputToFinalColumnNames,
            "dialect" to
                mapOf(
                    "encoding" to "UTF-8",
                    "separator" to ",",
                    "quote" to "\"",
                    "line_separator" to "LF",
                    "header" to false,
                    "compression" to "gzip"
                )
        )
    }
    override fun close() {
        if (closed.compareAndSet(false, true)) {
            uploader.close()
            runCatching { Runtime.getRuntime().removeShutdownHook(shutdownHook) }
        }
    }
}
