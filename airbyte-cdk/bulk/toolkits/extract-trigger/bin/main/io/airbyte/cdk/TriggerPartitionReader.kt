/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.discover.CommonMetaField
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldOrMetaField
import io.airbyte.cdk.output.DataChannelMedium.SOCKET
import io.airbyte.cdk.output.DataChannelMedium.STDIO
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.output.sockets.FieldValueEncoder
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.read.JdbcPartition
import io.airbyte.cdk.read.JdbcPartitionReader
import io.airbyte.cdk.read.JdbcSharedState
import io.airbyte.cdk.read.JdbcStreamState
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.SelectQuerier
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.UnlimitedTimePartitionReader
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference

/** Base class for Trigger-based CDC implementations of [PartitionReader] using JDBC. */
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "lateinit usage")
abstract class TriggerPartitionReader<P : JdbcPartition<*>>(
    val partition: P,
    protected val config: TriggerTableConfig,
) : UnlimitedTimePartitionReader {
    private val nullValueEncoder = FieldValueEncoder(null, NullCodec)

    lateinit var outputMessageRouter: OutputMessageRouter
    lateinit var outputRoute: ((NativeRecordPayload, Map<Field, FieldValueChange>?) -> Unit)
    private val charPool: List<Char> = ('a'..'z') + ('A'..'Z') + ('0'..'9')

    private fun generatePartitionId(length: Int): String =
        (1..length).map { charPool.random() }.joinToString("")

    protected var partitionId: String = generatePartitionId(4)
    val streamState: JdbcStreamState<*> = partition.streamState
    val stream: Stream = streamState.stream
    val sharedState: JdbcSharedState = streamState.sharedState
    val selectQuerier: SelectQuerier = sharedState.selectQuerier

    private val acquiredResources =
        AtomicReference<Map<ResourceType, JdbcPartitionReader.AcquiredResource>>()

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val resourceTypes =
            when (streamState.streamFeedBootstrap.dataChannelMedium) {
                STDIO -> listOf(ResourceType.RESOURCE_DB_CONNECTION)
                SOCKET ->
                    listOf(ResourceType.RESOURCE_DB_CONNECTION, ResourceType.RESOURCE_OUTPUT_SOCKET)
            }
        val resources: Map<ResourceType, JdbcPartitionReader.AcquiredResource> =
            partition.tryAcquireResourcesForReader(resourceTypes)
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        acquiredResources.set(resources)

        outputMessageRouter =
            OutputMessageRouter(
                streamState.streamFeedBootstrap.dataChannelMedium,
                streamState.streamFeedBootstrap.dataChannelFormat,
                streamState.streamFeedBootstrap.outputConsumer,
                mapOf("partition_id" to partitionId),
                streamState.streamFeedBootstrap,
                acquiredResources
                    .get()
                    .filter { it.value.resource != null }
                    .map { it.key to it.value.resource!! }
                    .toMap()
            )
        outputRoute = outputMessageRouter.recordAcceptors[stream.id]!!

        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    fun out(row: SelectQuerier.ResultRow) {
        val triggerStreamState = streamState as TriggerStreamState
        if (triggerStreamState.isReadingFromTriggerTable) {
            val decoratedPayload = decorateTriggerBasedCdcRecord(row)
            outputRoute(decoratedPayload, emptyMap())
        } else {
            outputRoute(row.data, row.changes)
        }
    }

    override fun releaseResources() {
        if (::outputMessageRouter.isInitialized) {
            outputMessageRouter.close()
        }
        acquiredResources.getAndSet(null)?.forEach { it.value.close() }
        partitionId = generatePartitionId(4)
    }

    protected fun outputPendingMessages() {
        if (streamState.streamFeedBootstrap.dataChannelMedium == STDIO) {
            return
        }
        while (PartitionReader.pendingStates.isNotEmpty()) {
            var pendingMessage = PartitionReader.pendingStates.poll() ?: break
            when (pendingMessage) {
                is AirbyteStateMessage -> {
                    outputMessageRouter.acceptNonRecord(pendingMessage)
                }
                is AirbyteStreamStatusTraceMessage -> {
                    outputMessageRouter.acceptNonRecord(pendingMessage)
                }
            }
        }
    }

    private fun decorateTriggerBasedCdcRecord(row: SelectQuerier.ResultRow): NativeRecordPayload {
        val isDelete: Boolean =
            (row.data[TriggerTableConfig.OPERATION_TYPE_FIELD.id]!!.fieldValue as? String)
                ?.uppercase() == "DELETE"
        val data = createChangePayload(row.data, isDelete)
        val validatedRecord = validateDataFieldName(data, stream.schema)
        val transactionTimestamp = row.data[config.CURSOR_FIELD.id]
        validatedRecord[CommonMetaField.CDC_UPDATED_AT.id] = transactionTimestamp!!
        validatedRecord[CommonMetaField.CDC_DELETED_AT.id] =
            if (isDelete) transactionTimestamp else nullValueEncoder
        validatedRecord[config.CURSOR_FIELD.id] = transactionTimestamp
        return validatedRecord
    }

    private fun createChangePayload(
        data: NativeRecordPayload,
        isDelete: Boolean,
    ): NativeRecordPayload {
        val payload: NativeRecordPayload = mutableMapOf()
        val suffix = if (isDelete) "_before" else "_after"
        stream.schema.forEach {
            val fieldName = TriggerTableConfig.TRIGGER_TABLE_PREFIX + it.id + suffix
            payload[it.id] = data[fieldName]!!
        }
        return payload
    }

    // Validate the data field name with the schema field name so they have the same case.
    private fun validateDataFieldName(
        payload: NativeRecordPayload,
        schema: Set<FieldOrMetaField>,
    ): NativeRecordPayload {
        val validatedPayload: NativeRecordPayload = mutableMapOf()
        for (field in schema) {
            val value =
                payload.keys.find { it.equals(field.id, ignoreCase = true) }?.let { payload[it] }
                    ?: throw IllegalArgumentException("Field '${field.id}' not found")
            validatedPayload[field.id] = value
        }
        return validatedPayload
    }
}

/**
 * Trigger-based implementation of [PartitionReader] which reads the [partition] in its entirety.
 */
class TriggerNonResumablePartitionReader<P : JdbcPartition<*>>(
    partition: P,
    config: TriggerTableConfig,
    val deleteQuerier: DeleteQuerier
) : TriggerPartitionReader<P>(partition, config) {
    val runComplete = AtomicBoolean(false)
    val numRecords = AtomicLong()

    override suspend fun run() {
        outputPendingMessages()

        // Check if partition is for trigger based CDC. We don't do cleanup for user defined cursor
        if (
            partition is TriggerCursorIncrementalPartition &&
                partition.triggerCdcPartitionState == TriggerCdcPartitionState.INCREMENTAL
        ) {
            val latestCheckpoint = partition.cursorLowerBound.asText()
            val namespace = TriggerTableConfig.TRIGGER_TABLE_NAMESPACE
            val fullyQualifiedName = "\"${namespace}\".\"${partition.triggerTableName}\""
            val whereClause = "\"${config.CURSOR_FIELD.id}\" < '${latestCheckpoint}'"
            deleteQuerier.executeDelete("DELETE FROM $fullyQualifiedName WHERE $whereClause")
        }

        selectQuerier
            .executeQuery(
                q = partition.nonResumableQuery,
                parameters =
                    SelectQuerier.Parameters(
                        reuseResultObject = true,
                        fetchSize = streamState.fetchSize,
                    ),
            )
            .use { result: SelectQuerier.Result ->
                for (row in result) {
                    out(row)
                    numRecords.incrementAndGet()
                }
            }
        runComplete.set(true)
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        // Sanity check.
        if (!runComplete.get()) throw RuntimeException("cannot checkpoint non-resumable read")
        // The run method executed to completion without a LIMIT clause.
        // This implies that the partition boundary has been reached.
        return PartitionReadCheckpoint(
            partition.completeState,
            numRecords.get(),
            when (streamState.streamFeedBootstrap.dataChannelMedium) {
                SOCKET -> partitionId
                STDIO -> null
            }
        )
    }
}
