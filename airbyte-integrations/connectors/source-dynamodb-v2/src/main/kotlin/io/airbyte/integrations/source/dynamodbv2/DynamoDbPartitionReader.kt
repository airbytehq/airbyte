/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.EmittedField
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
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive
import software.amazon.awssdk.services.dynamodb.model.AttributeValue
import software.amazon.awssdk.services.dynamodb.model.ScanRequest
import software.amazon.awssdk.services.dynamodb.model.ScanResponse

private val log = KotlinLogging.logger {}

/**
 * Scans a table page by page (`Scan` with `ExclusiveStartKey`), emits every item as a record, and
 * checkpoints at page boundaries.
 *
 * The CDK cancels [run] once `checkpointTargetInterval` has elapsed and then calls [checkpoint];
 * the cancellation is observed between two pages, so the checkpoint always points just after the
 * last page whose items were all emitted. The next round resumes from there with a new reader.
 */
class DynamoDbPartitionReader(
    val partition: DynamoDbPartition,
    val feedBootstrap: StreamFeedBootstrap,
    val sharedState: DynamoDbSharedState,
) : PartitionReader {

    val stream: Stream = partition.stream
    private val fieldIds: Set<String> = stream.fields.map { it.id }.toSet()

    private val numRecords = AtomicLong()
    private val complete = AtomicBoolean(false)
    /** `LastEvaluatedKey` of the last page fully emitted; null before the first page. */
    private val lastEvaluatedKey = AtomicReference(partition.exclusiveStartKey)
    private val cursorTracker: DynamoDbCursor.Tracker? = partition.cursor?.Tracker()

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
        outputMessageRouter =
            OutputMessageRouter(
                feedBootstrap.dataChannelMedium,
                feedBootstrap.dataChannelFormat,
                feedBootstrap.outputConsumer,
                mapOf("partition_id" to partitionId),
                feedBootstrap,
                resources,
            )
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
        var startKey: Map<String, AttributeValue>? = lastEvaluatedKey.get()
        var pages = 0
        // Stop voluntarily once the checkpoint interval has elapsed, at a page boundary; the CDK
        // cancels the run at the same interval, this makes the stop deterministic.
        val deadline: Long =
            System.nanoTime() + sharedState.configuration.checkpointTargetInterval.toNanos()
        log.info {
            "Scanning table '${stream.name}'" +
                (startKey?.let { " from key ${DynamoDbJson.itemToDynamoDbJson(it)}" } ?: "")
        }
        while (true) {
            // Lands the CDK's checkpoint timeout between two pages, never in the middle of one.
            currentCoroutineContext().ensureActive()
            val request: ScanRequest =
                if (startKey == null) baseRequest
                else baseRequest.toBuilder().exclusiveStartKey(startKey).build()
            val response: ScanResponse = sharedState.client.scan(request)
            for (item: Map<String, AttributeValue> in response.items()) {
                accept(toPayload(item), null)
                cursorTracker?.observe(item)
                numRecords.incrementAndGet()
            }
            pages++
            val nextKey: Map<String, AttributeValue>? =
                response.lastEvaluatedKey().takeIf {
                    response.hasLastEvaluatedKey() && it.isNotEmpty()
                }
            if (nextKey == null) {
                lastEvaluatedKey.set(null)
                complete.set(true)
                break
            }
            startKey = nextKey
            lastEvaluatedKey.set(nextKey)
            if (System.nanoTime() >= deadline) {
                log.info {
                    "Pausing the scan of table '${stream.name}' for a checkpoint after " +
                        "${numRecords.get()} record(s) in $pages page(s)."
                }
                return
            }
        }
        log.info {
            "Scanned table '${stream.name}' to the end: ${numRecords.get()} record(s) in $pages page(s)."
        }
    }

    /** Only the attributes present in the item; the CDK fills the other fields with null. */
    private fun toPayload(item: Map<String, AttributeValue>): NativeRecordPayload {
        val payload: NativeRecordPayload = mutableMapOf()
        for ((name: String, value: AttributeValue) in item) {
            if (name !in fieldIds) continue
            val json: JsonNode = DynamoDbJson.toRecordValue(value) ?: continue
            payload[name] = FieldValueEncoder(json, DynamoDbJsonNodeCodec)
        }
        return payload
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        val isComplete: Boolean = complete.get()
        if (isComplete) {
            sharedState.markComplete(stream.id)
        }
        return PartitionReadCheckpoint(
            stateValue(isComplete),
            numRecords.get(),
            when (feedBootstrap.dataChannelMedium) {
                DataChannelMedium.SOCKET -> partitionId
                DataChannelMedium.STDIO -> null
            },
        )
    }

    private fun stateValue(isComplete: Boolean): OpaqueStateValue {
        val cursor: DynamoDbCursor? = partition.cursor
        val tracker: DynamoDbCursor.Tracker? = cursorTracker
        val state: DynamoDbStreamStateValue =
            when {
                cursor == null || tracker == null ->
                    if (isComplete) {
                        DynamoDbStreamStateValue.FULL_REFRESH_COMPLETE
                    } else {
                        DynamoDbStreamStateValue(scan = scanProgress())
                    }
                isComplete ->
                    // Legacy DbStreamState shape: the new cursor is the highest value seen.
                    DynamoDbStreamStateValue(
                        cursorField = listOf(cursor.field),
                        cursor = tracker.max,
                        cursorRecordCount = tracker.maxRecordCount.takeIf { it > 0L },
                    )
                else ->
                    // Still filtering on the saved cursor; the running maximum travels along.
                    DynamoDbStreamStateValue(
                        cursorField = listOf(cursor.field),
                        cursor = cursor.lowerBound,
                        cursorRecordCount = cursor.lowerBoundRecordCount.takeIf { it > 0L },
                        scan =
                            scanProgress()
                                ?.copy(
                                    maxCursor = tracker.max,
                                    maxCursorRecordCount = tracker.maxRecordCount,
                                ),
                    )
            }
        return state.toOpaqueStateValue()
    }

    /**
     * The resume point, or null when no page was read yet (the state then has no `scan` and the
     * next round starts the same scan from the beginning).
     */
    private fun scanProgress(): DynamoDbStreamStateValue.ScanProgress? =
        lastEvaluatedKey.get()?.let {
            DynamoDbStreamStateValue.ScanProgress(DynamoDbJson.itemToDynamoDbJson(it))
        }

    override fun releaseResources() {
        outputMessageRouter?.close()
        outputMessageRouter = null
        acquiredResources.getAndSet(null)?.values?.forEach { it.close() }
    }
}
