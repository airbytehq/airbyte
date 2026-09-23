/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2.readapi

import com.google.api.gax.grpc.GrpcCallContext
import com.google.api.gax.rpc.ApiCallContext
import com.google.api.gax.rpc.ApiException
import com.google.api.gax.rpc.FailedPreconditionException
import com.google.api.gax.rpc.NotFoundException
import com.google.api.gax.rpc.PermissionDeniedException
import com.google.api.gax.rpc.ServerStream
import com.google.cloud.bigquery.storage.v1.ReadRowsRequest
import com.google.cloud.bigquery.storage.v1.ReadRowsResponse
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.TransientErrorException
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.output.DataChannelMedium.SOCKET
import io.airbyte.cdk.output.DataChannelMedium.STDIO
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.generatePartitionId
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import org.apache.arrow.compression.CommonsCompressionFactory
import org.apache.arrow.memory.RootAllocator
import org.apache.arrow.vector.VectorLoader
import org.apache.arrow.vector.VectorSchemaRoot
import org.apache.arrow.vector.ipc.ReadChannel
import org.apache.arrow.vector.ipc.message.ArrowRecordBatch
import org.apache.arrow.vector.ipc.message.MessageSerializer
import org.apache.arrow.vector.types.pojo.Schema
import org.apache.arrow.vector.util.ByteArrayReadableSeekableByteChannel

private val log = KotlinLogging.logger {}

/**
 * Reads one read stream of a Storage Read API session from a row offset to its end, emitting the
 * rows as records, and checkpoints the table's progress.
 *
 * A plain [PartitionReader]: the CDK stops it at its checkpoint interval, the progress reached is
 * checkpointed (the row offset of this and every other in-flight read stream), and the next round
 * of partitions resumes each read stream at its offset. Cancellation is honoured between Arrow
 * batches.
 */
class BigQueryReadApiPartitionReader(
    private val table: BigQueryReadApiTable,
    val work: BigQueryReadApiState.ReadStreamWork,
) : PartitionReader {

    private var partitionId: String = generatePartitionId(4)
    private val acquiredResources = AtomicReference<Map<ResourceType, Resource.Acquired>>()
    private lateinit var outputMessageRouter: OutputMessageRouter
    private lateinit var outputRoute:
        ((NativeRecordPayload, Map<EmittedField, FieldValueChange>?) -> Unit)

    val numRecords = AtomicLong()
    val runComplete = AtomicBoolean(false)

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val resourceTypes: List<ResourceType> =
            when (table.streamFeedBootstrap.dataChannelMedium) {
                STDIO -> listOf(ResourceType.RESOURCE_DB_CONNECTION)
                SOCKET ->
                    listOf(ResourceType.RESOURCE_DB_CONNECTION, ResourceType.RESOURCE_OUTPUT_SOCKET)
            }
        val resources: Map<ResourceType, Resource.Acquired> =
            table.resourceAcquirer.tryAcquire(resourceTypes)
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        acquiredResources.set(resources)
        outputMessageRouter =
            OutputMessageRouter(
                table.streamFeedBootstrap.dataChannelMedium,
                table.streamFeedBootstrap.dataChannelFormat,
                table.streamFeedBootstrap.outputConsumer,
                mapOf("partition_id" to partitionId),
                table.streamFeedBootstrap,
                resources,
            )
        outputRoute = outputMessageRouter.recordAcceptors[table.stream.id]!!
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run() {
        outputPendingMessages()
        val startOffset: Long = work.offset
        log.info {
            "Reading read stream #${work.index} of '${table.stream.label}' from row offset " +
                "$startOffset (${work.name})."
        }
        val request: ReadRowsRequest =
            ReadRowsRequest.newBuilder().setReadStream(work.name).setOffset(startOffset).build()
        val allocator = RootAllocator()
        var root: VectorSchemaRoot? = null
        var responses: ServerStream<ReadRowsResponse>? = null
        try {
            responses = table.client.readRowsCallable().call(request, callContext(table.constants))
            var loader: VectorLoader? = null
            var decoder: BigQueryArrowRecordDecoder? = null
            val payload: NativeRecordPayload = mutableMapOf()
            val changes: MutableMap<EmittedField, FieldValueChange> = mutableMapOf()
            var rowsRead = 0L
            for (response: ReadRowsResponse in responses) {
                if (root == null) {
                    val schemaBytes: ByteArray =
                        if (response.hasArrowSchema()) {
                            response.arrowSchema.serializedSchema.toByteArray()
                        } else {
                            table.progress.session.arrowSchema
                                ?: throw IllegalStateException(
                                    "The first ReadRows response of ${work.name} carries no Arrow " +
                                        "schema and the session was created by another process."
                                )
                        }
                    val schema: Schema =
                        MessageSerializer.deserializeSchema(
                            ReadChannel(ByteArrayReadableSeekableByteChannel(schemaBytes))
                        )
                    val created: VectorSchemaRoot = VectorSchemaRoot.create(schema, allocator)
                    root = created
                    loader = VectorLoader(created, CommonsCompressionFactory.INSTANCE)
                    decoder = BigQueryArrowRecordDecoder(created, table.stream.fields)
                }
                val loadedRoot: VectorSchemaRoot = root
                if (response.hasArrowRecordBatch()) {
                    val batch: ArrowRecordBatch =
                        MessageSerializer.deserializeRecordBatch(
                            ReadChannel(
                                ByteArrayReadableSeekableByteChannel(
                                    response.arrowRecordBatch.serializedRecordBatch.toByteArray()
                                )
                            ),
                            allocator,
                        )
                    try {
                        loader!!.load(batch)
                    } finally {
                        batch.close()
                    }
                    val rowCount: Int = loadedRoot.rowCount
                    for (row in 0 until rowCount) {
                        decoder!!.decode(row, payload, changes)
                        outputRoute(payload, changes.ifEmpty { null })
                    }
                    numRecords.addAndGet(rowCount.toLong())
                    rowsRead += rowCount
                    table.progress.recordRows(work.index, startOffset + rowsRead)
                }
                // Honour the CDK's checkpoint-interval timeout between batches.
                currentCoroutineContext().ensureActive()
            }
            table.progress.markComplete(work.index)
            runComplete.set(true)
            log.info {
                "Completed read stream #${work.index} of '${table.stream.label}': " +
                    "$rowsRead rows from offset $startOffset."
            }
        } catch (e: PermissionDeniedException) {
            throw ConfigErrorException(
                BigQueryReadSession.permissionDeniedMessage(table.jobProjectId),
                e,
            )
        } catch (e: NotFoundException) {
            throw expired(e)
        } catch (e: FailedPreconditionException) {
            throw expired(e)
        } catch (e: ApiException) {
            // Any other API failure (deadline, unavailable, internal, ...): the offset reached so
            // far
            // is checkpointed by the CDK only when run() returns, so let the next attempt resume
            // the
            // read stream from the last checkpointed offset.
            throw TransientErrorException(
                "ReadRows on read stream ${work.name} of '${table.stream.label}' failed: ${e.message}",
                e,
            )
        } finally {
            try {
                responses?.cancel()
            } catch (_: RuntimeException) {}
            root?.close()
            allocator.close()
        }
    }

    /**
     * The session (and its read streams) is gone: the table is started over on the next attempt.
     */
    private fun expired(e: Exception): TransientErrorException =
        TransientErrorException(
            "Read stream ${work.name} of '${table.stream.label}' is no longer readable " +
                "(the BigQuery read session expired or was deleted); the table will be read " +
                "again from the start: ${e.message}",
            e,
        )

    companion object {
        /** Per-call gRPC settings of `ReadRows`: fail a read stream that stops delivering. */
        fun callContext(constants: BigQueryReadApiConstants): ApiCallContext {
            // gax still takes threeten durations here.
            val idle: org.threeten.bp.Duration =
                org.threeten.bp.Duration.ofSeconds(
                    constants.readRowsIdleTimeoutSeconds.coerceAtLeast(1L)
                )
            return GrpcCallContext.createDefault()
                .withStreamIdleTimeout(idle)
                .withStreamWaitTimeout(idle)
        }
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        val state =
            if (table.progress.isComplete) table.terminalState
            else table.progress.snapshot().toOpaqueStateValue()
        return PartitionReadCheckpoint(
            state,
            numRecords.get(),
            when (table.streamFeedBootstrap.dataChannelMedium) {
                SOCKET -> partitionId
                STDIO -> null
            },
        )
    }

    override fun releaseResources() {
        if (::outputMessageRouter.isInitialized) {
            outputMessageRouter.close()
        }
        acquiredResources.getAndSet(null)?.forEach { it.value.close() }
        partitionId = generatePartitionId(4)
    }

    /** Same as the JDBC readers: flush pending states and statuses through the acquired socket. */
    private fun outputPendingMessages() {
        if (table.streamFeedBootstrap.dataChannelMedium == STDIO) {
            return
        }
        while (PartitionReader.pendingStates.isNotEmpty()) {
            val pendingMessage = PartitionReader.pendingStates.poll() ?: break
            when (pendingMessage) {
                is AirbyteStateMessage -> outputMessageRouter.acceptNonRecord(pendingMessage)
                is AirbyteStreamStatusTraceMessage ->
                    outputMessageRouter.acceptNonRecord(pendingMessage)
            }
        }
    }
}
