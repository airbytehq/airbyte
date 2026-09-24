/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.EmittedField
import io.airbyte.cdk.output.DataChannelFormat
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.read.generatePartitionId
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.delay
import kotlinx.coroutines.ensureActive
import software.amazon.awssdk.services.dynamodb.model.AttributeValue
import software.amazon.awssdk.services.dynamodb.model.ScanRequest
import software.amazon.awssdk.services.dynamodb.model.ScanResponse

private val log = KotlinLogging.logger {}

/**
 * Scans one segment of a table page by page (`Scan` with `Segment`/`TotalSegments` and
 * `ExclusiveStartKey`), emits every item as a record, and records its progress in the table's
 * shared [DynamoDbTableScan] after every page.
 *
 * The CDK cancels [run] once `checkpointTargetInterval` has elapsed and then calls [checkpoint];
 * the cancellation is observed between two pages, so the registry always points just after the last
 * page whose items were all emitted. The next round resumes every unfinished segment from there
 * with new readers.
 *
 * **Checkpoint freshness.** A checkpoint is a snapshot of the whole table's progress, taken when
 * this reader stops. The CDK applies the checkpoints of a round strictly in partition order, each
 * replacing the stream's state, so the state that survives the round is the snapshot of the round's
 * last partition. Readers start in partition order (each acquires its concurrency slot after the
 * previous one), so the last partition starts last and has the latest deadline: once it has
 * completed its segment it waits, until the round's other readers have stopped or its own deadline
 * passes, before it returns, so that its snapshot is the freshest one and the terminal state is
 * emitted in the round in which the last segment completes. Only the last partition waits, so at
 * most one concurrency slot idles. Every other snapshot is at most one page behind the readers that
 * were still running, which after a crash only causes a re-read, never a gap. Should the last
 * partition's snapshot still predate the completion of another segment (it reached its deadline
 * while waiting), the planner adds a [DynamoDbTerminalStateReader] in the next round.
 */
class DynamoDbPartitionReader(
    val partition: DynamoDbPartition,
    val feedBootstrap: StreamFeedBootstrap,
    val sharedState: DynamoDbSharedState,
) : PartitionReader {

    val stream: Stream = partition.stream
    private val scan: DynamoDbTableScan = partition.scan
    private val segment: Int = partition.segment
    /** The stream's fields with their codecs, in schema order; see [toPayload]. */
    private val fields: List<Pair<EmittedField, DynamoDbJsonNodeCodec>> =
        stream.fields.map { field: EmittedField ->
            field to
                ((field.type as? DynamoDbFieldType)?.codec
                    ?: DynamoDbJsonNodeCodec(field.type.airbyteSchemaType))
        }
    /** On the protobuf channel the slots are typed, see [toPayload]. */
    private val typedChannel: Boolean =
        feedBootstrap.dataChannelFormat == DataChannelFormat.PROTOBUF

    private val numRecords = AtomicLong()
    private val cursorTracker: DynamoDbCursor.Tracker? =
        partition.cursor?.let { cursor: DynamoDbCursor ->
            val saved: DynamoDbTableScan.SegmentCursor = scan.cursor(segment)
            cursor.Tracker(saved.max, saved.recordCount)
        }

    private val partitionId: String = generatePartitionId(4)
    private val acquiredResources = AtomicReference<Map<ResourceType, Resource.Acquired>?>()
    /** Set in [tryAcquireResources], closed in [releaseResources]. */
    private var outputMessageRouter: OutputMessageRouter? = null

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val resourceTypes: List<ResourceType> =
            when (feedBootstrap.dataChannelMedium) {
                DataChannelMedium.STDIO -> listOf(ResourceType.RESOURCE_DB_CONNECTION)
                DataChannelMedium.SOCKET ->
                    listOf(ResourceType.RESOURCE_DB_CONNECTION, ResourceType.RESOURCE_OUTPUT_SOCKET)
            }
        val resources: Map<ResourceType, Resource.Acquired> =
            sharedState.tryAcquireReaderResources(resourceTypes)
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        acquiredResources.set(resources)
        try {
            outputMessageRouter =
                OutputMessageRouter(
                    feedBootstrap.dataChannelMedium,
                    feedBootstrap.dataChannelFormat,
                    feedBootstrap.outputConsumer,
                    mapOf("partition_id" to partitionId),
                    feedBootstrap,
                    resources,
                )
        } catch (e: Exception) {
            // A failure here must not leak the concurrency slot and the socket: the other feeds
            // would wait for them forever instead of the sync failing fast.
            releaseResources()
            throw e
        }
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run() {
        val router: OutputMessageRouter =
            outputMessageRouter
                ?: throw IllegalStateException("run() called before resources were acquired")
        val accept: (NativeRecordPayload, Map<EmittedField, FieldValueChange>?) -> Unit =
            router.recordAcceptors[stream.id]
                ?: throw IllegalStateException("No record acceptor for stream ${stream.id}")
        val baseRequest: ScanRequest = partition.scanRequest(sharedState.scanPageLimit)
        var startKey: Map<String, AttributeValue>? = scan.startKey(segment)
        var pages = 0
        // Stop voluntarily once the checkpoint interval has elapsed, at a page boundary; the CDK
        // cancels the run at the same interval, this makes the stop deterministic.
        val deadline: Long =
            System.nanoTime() + sharedState.configuration.checkpointTargetInterval.toNanos()
        val label: String =
            "table '${stream.name}'" +
                (if (partition.totalSegments > 1) " segment $segment/${partition.totalSegments}"
                else "")
        log.info {
            "Scanning $label" +
                (startKey?.let { " from key ${DynamoDbJson.itemToDynamoDbJson(it)}" } ?: "")
        }
        scan.readerStarted()
        try {
            while (true) {
                // Lands the CDK's checkpoint timeout between two pages, never in the middle of one.
                currentCoroutineContext().ensureActive()
                val request: ScanRequest =
                    if (startKey == null) baseRequest
                    else baseRequest.toBuilder().exclusiveStartKey(startKey).build()
                val response: ScanResponse = sharedState.client.scan(request)
                for (item: Map<String, AttributeValue> in response.items()) {
                    val changes = HashMap<EmittedField, FieldValueChange>(0)
                    accept(toPayload(item, changes), changes.ifEmpty { null })
                    cursorTracker?.observe(item)
                    numRecords.incrementAndGet()
                }
                pages++
                val nextKey: Map<String, AttributeValue>? =
                    response.lastEvaluatedKey().takeIf {
                        response.hasLastEvaluatedKey() && it.isNotEmpty()
                    }
                if (nextKey == null) {
                    scan.recordCompletion(segment, cursorTracker?.cursor())
                    log.info {
                        "Scanned $label to the end: ${numRecords.get()} record(s) in $pages page(s)."
                    }
                    break
                }
                startKey = nextKey
                scan.recordPage(segment, nextKey, cursorTracker?.cursor())
                if (System.nanoTime() >= deadline) {
                    log.info {
                        "Pausing the scan of $label for a checkpoint after " +
                            "${numRecords.get()} record(s) in $pages page(s)."
                    }
                    return
                }
            }
            if (partition.lastInRound) {
                // Checkpoint freshness, see the class comment: let the round's other readers stop
                // first, so that the snapshot the CDK applies last is the most recent one.
                while (scan.runningReaders() > 1 && System.nanoTime() < deadline) {
                    delay(LINGER_MILLIS)
                }
            }
        } finally {
            scan.readerStopped()
        }
    }

    /**
     * Every field of the stream, with an explicit null for each attribute the item lacks (or whose
     * value is the DynamoDB `NULL`). The JSON consumers fill absent fields with null themselves,
     * but the protobuf consumer reuses one record builder per stream and, before Bulk CDK 1.1.12,
     * only overwrote the slots present in the payload, so a sparse payload let an item inherit the
     * previous item's attributes. Explicit nulls keep the connector safe on any CDK version.
     *
     * **Mismatched values.** The schema comes from a sample, so an item may hold a value of another
     * type than its field declares (`flexible` is `S` in one item and `N` in another, say). On the
     * JSON channels the value is emitted as is, like the legacy connector did, and the destination
     * coerces it. On the protobuf channel the slot is typed and cannot hold it: the field is sent
     * as null and the record carries a change (`NULLED`, `SOURCE_SERIALIZATION_ERROR`) for it in
     * [changes], which the destination writes to `_airbyte_meta`.
     */
    private fun toPayload(
        item: Map<String, AttributeValue>,
        changes: MutableMap<EmittedField, FieldValueChange>,
    ): NativeRecordPayload {
        val payload: NativeRecordPayload = mutableMapOf()
        for ((field: EmittedField, codec: DynamoDbJsonNodeCodec) in fields) {
            var json: JsonNode? = item[field.id]?.let(DynamoDbJson::toRecordValue)
            if (typedChannel && json != null && !codec.representable(json)) {
                log.debug {
                    "Table '${stream.name}': value of '${field.id}' is not a ${codec.schemaType}; " +
                        "sending null with a change record."
                }
                json = null
                changes[field] = FieldValueChange.DESERIALIZATION_FAILURE_TOTAL
            }
            payload[field.id] = FieldValueEncoder(json, codec)
        }
        return payload
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        val (state: OpaqueStateValue, terminal: Boolean) = scan.currentState(partition.cursor)
        if (partition.lastInRound) {
            scan.terminalStateApplied = terminal
        }
        return PartitionReadCheckpoint(
            state,
            numRecords.get(),
            when (feedBootstrap.dataChannelMedium) {
                DataChannelMedium.SOCKET -> partitionId
                DataChannelMedium.STDIO -> null
            },
        )
    }

    override fun releaseResources() {
        outputMessageRouter?.close()
        outputMessageRouter = null
        acquiredResources.getAndSet(null)?.values?.forEach { it.close() }
    }

    companion object {
        const val LINGER_MILLIS = 50L
    }
}

/**
 * Emits the terminal state of a table whose every segment is complete, when the state the CDK
 * applied last did not say so yet (see [DynamoDbTableScan.terminalStateApplied]). Reads nothing and
 * needs no resources.
 */
class DynamoDbTerminalStateReader(
    val stream: Stream,
    val scan: DynamoDbTableScan,
    val cursor: DynamoDbCursor?,
    val feedBootstrap: StreamFeedBootstrap,
) : PartitionReader {
    private val partitionId: String = generatePartitionId(4)

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus =
        PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN

    override suspend fun run() {
        log.info { "Table '${stream.name}' is complete; emitting its final state." }
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        val (state: OpaqueStateValue, terminal: Boolean) = scan.currentState(cursor)
        check(terminal) { "Table '${stream.name}' is not complete" }
        scan.terminalStateApplied = true
        return PartitionReadCheckpoint(
            state,
            0L,
            when (feedBootstrap.dataChannelMedium) {
                DataChannelMedium.SOCKET -> partitionId
                DataChannelMedium.STDIO -> null
            },
        )
    }

    override fun releaseResources() {}
}
