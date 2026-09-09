package io.airbyte.integrations.destination.snowflake.copy

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.SystemErrorException
import io.airbyte.integrations.destination.snowflake.schema.SnowflakeColumnManager
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfiguration
import io.airbyte.cdk.load.util.Jsons
import java.nio.file.Path
import java.security.MessageDigest
import java.util.UUID
import java.util.concurrent.Semaphore
import java.util.concurrent.atomic.AtomicBoolean
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

data class CsvCopyContext(
    val streamKey: String, val generationId: Long, val syncId: Long, val schemaId: String,
    val runId: UUID, val connectionId: UUID,
    val runPath: String,
)

interface SnowflakeS3Copy : AutoCloseable {
    suspend fun prepare(catalog: DestinationCatalog)
    fun context(stream: DestinationStream): CsvCopyContext?
    suspend fun upload(path: Path, context: CsvCopyContext, recordCount: Int, batchId: UUID)
}

object DisabledSnowflakeS3Copy : SnowflakeS3Copy {
    override suspend fun prepare(catalog: DestinationCatalog) = Unit
    override fun context(stream: DestinationStream): CsvCopyContext? = null
    override suspend fun upload(path: Path, context: CsvCopyContext, recordCount: Int, batchId: UUID) = Unit
    override fun close() = Unit
}

class EnabledSnowflakeS3Copy(
    private val config: S3CopyConfiguration,
    private val columnManager: SnowflakeColumnManager,
    private val snowflakeConfiguration: SnowflakeConfiguration,
) : SnowflakeS3Copy {
    private val runId = UUID.randomUUID()
    private val uploader = S3CsvUploader(config)
    private val slots = Semaphore(4)
    private val closed = AtomicBoolean(false)
    private val shutdownHook = Thread { close() }
    private val contexts = mutableMapOf<DestinationStream, CsvCopyContext>()

    init { Runtime.getRuntime().addShutdownHook(shutdownHook) }

    override suspend fun prepare(catalog: DestinationCatalog) {
        catalog.streams.forEach { stream ->
            if (stream.minimumGenerationId != 0L && stream.minimumGenerationId != stream.generationId) {
                throw SystemErrorException(
                    "Cannot execute a hybrid refresh - current generation ${stream.generationId}; minimum generation ${stream.minimumGenerationId}"
                )
            }
        }
        catalog.streams.forEach { stream ->
            val schema = descriptor(stream)
            val schemaId = sha(schema)
            val key = streamKey(stream)
            val runPath = S3CopyPaths.run(config, stream.unmappedName, runId)
            putJson("$runPath/schema.json", schema + mapOf("schema_id" to schemaId, "generation_id" to stream.generationId, "sync_id" to stream.syncId, "run_id" to runId, "workspace_id" to config.workspaceId, "connection_id" to config.connectionId))
            if (stream.minimumGenerationId > 0) {
                putJson("$runPath/generation-cutoff.json", cutoff(stream, key))
            }
            contexts[stream] = CsvCopyContext(key, stream.generationId, stream.syncId, schemaId, runId, config.connectionId, runPath)
        }
    }

    override fun context(stream: DestinationStream) = contexts[stream]

    override suspend fun upload(path: Path, context: CsvCopyContext, recordCount: Int, batchId: UUID) {
        withContext(Dispatchers.IO) {
            slots.acquire()
            try {
                val key = "${context.runPath}/batches/$batchId.csv.gz"
                uploader.upload(path, key, mapOf(
                    "format-version" to "1", "connection-id" to config.connectionId.toString(),
                    "workspace-id" to config.workspaceId.toString(),
                    "stream-key" to context.streamKey, "generation-id" to context.generationId.toString(),
                    "sync-id" to context.syncId.toString(), "run-id" to runId.toString(),
                    "batch-id" to batchId.toString(), "schema-id" to context.schemaId,
                    "record-count" to recordCount.toString(),
                )).get()
            } finally { slots.release() }
        }
    }

    private fun streamKey(stream: DestinationStream) = sha(mapOf("namespace" to stream.unmappedNamespace, "name" to stream.unmappedName))
    private fun sha(value: Any): String = MessageDigest.getInstance("SHA-256").digest(Jsons.writeValueAsBytes(value)).joinToString("") { "%02x".format(it) }
    private fun putJson(key: String, value: Any) { uploader.uploadJson(Jsons.writeValueAsBytes(value), key).get() }
    private fun descriptor(stream: DestinationStream): Map<String, Any> {
        val columns = LinkedHashMap<String, Any>()
        columnManager.getMetaColumns().forEach { (n, t) -> columns[n] = mapOf("type" to t.type, "nullable" to t.nullable) }
        stream.tableSchema.columnSchema.finalSchema.forEach { (n, t) -> columns[n] = mapOf("type" to t.type, "nullable" to t.nullable) }
        return mapOf("contract_version" to 1, "connector" to "destination-snowflake", "format" to "snowflake-load-csv-gzip-v1", "stream" to mapOf("namespace" to stream.unmappedNamespace, "name" to stream.unmappedName), "mapped_stream" to mapOf("namespace" to stream.mappedDescriptor.namespace, "name" to stream.mappedDescriptor.name), "table" to mapOf("namespace" to stream.tableSchema.tableNames.finalTableName!!.namespace, "name" to stream.tableSchema.tableNames.finalTableName!!.name), "mode" to if (snowflakeConfiguration.legacyRawTablesOnly) "raw" else "schema", "columns" to columns, "input_to_final" to stream.tableSchema.columnSchema.inputToFinalColumnNames, "dialect" to mapOf("encoding" to "UTF-8", "separator" to ",", "quote" to "\"", "line_separator" to "LF", "header" to false, "compression" to "gzip"))
    }
    private fun cutoff(stream: DestinationStream, key: String) = mapOf("format_version" to 1, "event_type" to "generation_cutoff_requested", "event_id" to UUID.randomUUID(), "connection_id" to config.connectionId, "stream_key" to key, "stream" to mapOf("namespace" to stream.unmappedNamespace, "name" to stream.unmappedName), "mapped_stream" to mapOf("namespace" to stream.mappedDescriptor.namespace, "name" to stream.mappedDescriptor.name), "generation_id" to stream.generationId, "minimum_generation_id" to stream.minimumGenerationId, "sync_id" to stream.syncId, "run_id" to runId, "requested_effect" to "discard_records_with_generation_id_less_than_minimum")
    override fun close() {
        if (closed.compareAndSet(false, true)) {
            uploader.close()
            runCatching { Runtime.getRuntime().removeShutdownHook(shutdownHook) }
        }
    }
}
