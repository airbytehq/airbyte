/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.write.storage_write

import com.google.api.core.ApiFuture
import com.google.api.gax.retrying.RetrySettings
import com.google.api.gax.rpc.NotFoundException
import com.google.cloud.bigquery.storage.v1.AppendRowsResponse
import com.google.cloud.bigquery.storage.v1.BatchCommitWriteStreamsRequest
import com.google.cloud.bigquery.storage.v1.BigQueryWriteClient
import com.google.cloud.bigquery.storage.v1.CreateWriteStreamRequest
import com.google.cloud.bigquery.storage.v1.Exceptions
import com.google.cloud.bigquery.storage.v1.ProtoRows
import com.google.cloud.bigquery.storage.v1.StreamWriter
import com.google.cloud.bigquery.storage.v1.TableName
import com.google.cloud.bigquery.storage.v1.WriteStream
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.orchestration.db.direct_load_table.DirectLoadTableExecutionConfig
import io.airbyte.cdk.load.orchestration.db.legacy_typing_deduping.TableCatalogByDescriptor
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.StorageWriteApiConfiguration
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryLoadRows
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import io.micronaut.context.condition.Condition
import io.micronaut.context.condition.ConditionContext
import jakarta.inject.Named
import jakarta.inject.Singleton
import java.time.Duration
import java.util.concurrent.ExecutionException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

private val log = KotlinLogging.logger {}

/**
 * Writes one batch of a stream into its table through a PENDING write stream of the Storage Write
 * API: rows are appended while the batch accumulates, and [finish] commits them at once, so a batch
 * is all or nothing as a load job is. A batch abandoned without [finish] is never committed.
 *
 * Appends carry offsets, so the client library's retries and reconnects cannot write a row twice.
 *
 * A row must fit in one append request. A larger one fails the sync: replaying it would fail again,
 * and such a table needs the GCS staging loading method.
 */
class BigQueryStorageWriteLoader(
    private val writeClient: BigQueryWriteClient,
    private val table: TableName,
    private val rows: BigQueryProtoRows,
) : DirectLoader {
    private var writer: StreamWriter? = null
    private var request: ProtoRows.Builder = ProtoRows.newBuilder()
    private var requestBytes = 0L
    private var offset = 0L
    private var bytes = 0L
    private var requests = 0
    private val appends = ArrayDeque<ApiFuture<AppendRowsResponse>>()

    override suspend fun accept(record: DestinationRecordRaw): DirectLoader.DirectLoadResult {
        val row = rows.encode(record)
        if (row.size() > MAX_ROW_BYTES) {
            throw ConfigErrorException(
                "A record for table ${table.dataset}.${table.table} is ${row.size()} bytes as a row; the Storage Write API loading method writes rows of up to $MAX_ROW_BYTES bytes. Use the GCS Staging loading method for this connection.",
            )
        }
        if (request.serializedRowsCount > 0 && requestBytes + row.size() > REQUEST_BYTES) {
            append()
        }
        request.addSerializedRows(row)
        requestBytes += row.size()
        // rely on the CDK to tell us when to finish()
        return DirectLoader.Incomplete
    }

    override suspend fun finish() {
        withContext(Dispatchers.IO) {
            if (request.serializedRowsCount > 0) {
                append()
            }
            writer?.let { commit(it) }
        }
    }

    override fun close() {
        writer?.let {
            log.info { "Abandoning uncommitted write stream ${it.streamName} of ${table.table}." }
            it.close()
        }
        writer = null
    }

    private fun append() {
        val writer = writer ?: open().also { writer = it }
        val count = request.serializedRowsCount
        appends.addLast(writer.append(request.build(), offset))
        offset += count
        bytes += requestBytes
        requests++
        request = ProtoRows.newBuilder()
        requestBytes = 0
        // Fail the batch at the first failed append rather than at its end.
        while (appends.firstOrNull()?.isDone == true) {
            await(appends.removeFirst())
        }
    }

    private fun open(): StreamWriter {
        val stream = createWriteStream()
        return StreamWriter.newBuilder(stream.name, writeClient)
            .setWriterSchema(rows.schema)
            .setMaxInflightBytes(MAX_INFLIGHT_BYTES)
            .setRetrySettings(RETRY_SETTINGS)
            // The destination usually runs outside Google Cloud; requests cross the internet.
            .setCompressorName("gzip")
            .build()
    }

    /**
     * The API does not find a table that was dropped and created again under its name for minutes.
     * A refresh replaces the final table that way; the next sync waits for it here.
     */
    private fun createWriteStream(): WriteStream {
        val request =
            CreateWriteStreamRequest.newBuilder()
                .setParent(table.toString())
                .setWriteStream(WriteStream.newBuilder().setType(WriteStream.Type.PENDING))
                .build()
        val deadline = System.nanoTime() + TABLE_NOT_FOUND_WAIT.toNanos()
        var delay = Duration.ofSeconds(5)
        while (true) {
            try {
                return writeClient.createWriteStream(request)
            } catch (e: NotFoundException) {
                if (System.nanoTime() + delay.toNanos() > deadline) throw e
                log.warn {
                    "The Storage Write API does not find table ${table.dataset}.${table.table} yet; retrying in ${delay.seconds} s."
                }
                Thread.sleep(delay.toMillis())
                delay = minOf(delay.multipliedBy(2), Duration.ofMinutes(1))
            }
        }
    }

    private fun commit(writer: StreamWriter) {
        while (appends.isNotEmpty()) {
            await(appends.removeFirst())
        }
        writer.close()
        this.writer = null
        val finalized = writeClient.finalizeWriteStream(writer.streamName)
        check(finalized.rowCount == offset) {
            "Write stream ${writer.streamName} of ${table.table} holds ${finalized.rowCount} rows; $offset were appended."
        }
        val commit =
            writeClient.batchCommitWriteStreams(
                BatchCommitWriteStreamsRequest.newBuilder()
                    .setParent(table.toString())
                    .addWriteStreams(writer.streamName)
                    .build(),
            )
        if (!commit.hasCommitTime()) {
            throw RuntimeException(
                "Failed to commit write stream ${writer.streamName} to table ${table.table}: " +
                    commit.streamErrorsList.joinToString { "${it.code}: ${it.errorMessage}" },
            )
        }
        log.info {
            "Committed $offset rows ($bytes bytes in $requests requests) to table ${table.dataset}.${table.table}."
        }
    }

    private fun await(append: ApiFuture<AppendRowsResponse>) {
        try {
            append.get()
        } catch (e: ExecutionException) {
            // A resent request whose rows the stream already holds.
            if (e.cause is Exceptions.OffsetAlreadyExists) return
            throw RuntimeException(
                "Failed to append rows to table ${table.dataset}.${table.table}",
                e.cause,
            )
        }
    }

    companion object {
        const val REQUEST_BYTES = 8L * 1024 * 1024
        // An append request is at most 20 MB; this leaves room for the request's own fields.
        const val MAX_ROW_BYTES = 18L * 1024 * 1024
        private val TABLE_NOT_FOUND_WAIT: Duration = Duration.ofMinutes(10)
        // Per open loader; a sync has up to one open loader per stream and input partition.
        private const val MAX_INFLIGHT_BYTES = 32L * 1024 * 1024
        private val RETRY_SETTINGS: RetrySettings =
            RetrySettings.newBuilder()
                .setInitialRetryDelayDuration(Duration.ofMillis(500))
                .setRetryDelayMultiplier(2.0)
                .setMaxRetryDelayDuration(Duration.ofMinutes(1))
                .setMaxAttempts(8)
                .build()
    }
}

class BigqueryConfiguredForStorageWriteApi : Condition {
    override fun matches(context: ConditionContext<*>): Boolean {
        val config = context.beanContext.getBean(BigqueryConfiguration::class.java)
        return config.loadingMethod is StorageWriteApiConfiguration
    }
}

@Requires(condition = BigqueryConfiguredForStorageWriteApi::class)
@Singleton
class BigQueryStorageWriteLoaderFactory(
    private val catalog: DestinationCatalog,
    private val writeClient: BigQueryWriteClient,
    private val config: BigqueryConfiguration,
    private val tableCatalog: TableCatalogByDescriptor,
    private val streamStateStore: StreamStateStore<DirectLoadTableExecutionConfig>,
    @Named("dataChannelFormat") private val dataChannelFormat: DataChannelFormat,
) : DirectLoaderFactory<BigQueryStorageWriteLoader> {
    override fun create(
        streamDescriptor: DestinationStream.Descriptor,
        part: Int,
    ): BigQueryStorageWriteLoader {
        val stream = catalog.getStream(streamDescriptor)
        // The coordinating StreamLoader picks the table (the final one, or a temp table) at stream
        // start.
        val tableName = waitForStateStore(streamDescriptor).tableName
        // One per loader: the protobuf row generator reuses its row buffer, and loaders of a
        // stream run concurrently, one per input partition.
        val loadRows =
            BigQueryLoadRows.of(
                stream,
                tableCatalog[streamDescriptor]!!.columnNameMapping,
                dataChannelFormat,
            )
        return BigQueryStorageWriteLoader(
            writeClient,
            TableName.of(config.projectId, tableName.namespace, tableName.name),
            BigQueryProtoRows(loadRows),
        )
    }

    private fun waitForStateStore(
        streamDescriptor: DestinationStream.Descriptor,
    ): DirectLoadTableExecutionConfig {
        repeat(STATE_STORE_WAIT_SECONDS) {
            streamStateStore.get(streamDescriptor)?.let {
                return it
            }
            Thread.sleep(1000)
        }
        throw RuntimeException(
            "Timeout waiting for StreamStateStore to be populated for stream $streamDescriptor. This indicates a coordination issue between workers.",
        )
    }

    companion object {
        private const val STATE_STORE_WAIT_SECONDS = 60 * 60
    }
}
