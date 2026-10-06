/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Meta.Companion.CHECKPOINT_ID_NAME
import io.airbyte.cdk.load.message.Meta.Companion.CHECKPOINT_INDEX_NAME
import io.airbyte.cdk.load.state.CheckpointKey
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.protocol.models.v0.AdditionalStats
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.StreamDescriptor

/**
 * Checkpoint message types.
 *
 * NOTE: This file was extracted from DestinationMessage.kt for better organization. The checkpoint
 * hierarchy is complex and important - bugs here are hard to catch.
 */

/** State. */
sealed interface CheckpointMessage : DestinationMessage {
    companion object {
        const val COMMITTED_RECORDS_COUNT = "committedRecordsCount"
        const val COMMITTED_BYTES_COUNT = "committedBytesCount"
        const val REJECTED_RECORDS_COUNT = "rejectedRecordsCount"
    }
    data class Stats(
        val recordCount: Long,
        val rejectedRecordCount: Long = 0, // TODO should not have a default?
        val additionalStats: Map<String, Double> = emptyMap(),
    )

    data class Checkpoint(
        val unmappedNamespace: String?,
        val unmappedName: String,
        val state: JsonNode?,
        val additionalProperties: LinkedHashMap<String, Any> = LinkedHashMap()
    ) {
        val unmappedDescriptor = DestinationStream.Descriptor(unmappedNamespace, unmappedName)

        fun asProtocolObject(): AirbyteStreamState =
            AirbyteStreamState()
                .withStreamDescriptor(
                    StreamDescriptor().withNamespace(unmappedNamespace).withName(unmappedName),
                )
                .also { state ->
                    if (this.state != null) {
                        state.streamState = this.state
                    }

                    if (additionalProperties.isNotEmpty()) {
                        additionalProperties.forEach {
                            state.additionalProperties[it.key] = it.value
                        }
                    }
                }

        fun updateStats(committedRecords: Long, bytes: Long, rejectedRecords: Long = 0) {
            additionalProperties.apply {
                put(COMMITTED_RECORDS_COUNT, committedRecords)
                put(COMMITTED_BYTES_COUNT, bytes)
                if (rejectedRecords > 0) {
                    put(REJECTED_RECORDS_COUNT, rejectedRecords)
                }
            }
        }
    }

    val checkpointKey: CheckpointKey?
    val checkpointIdRaw: String?
        get() = checkpointKey?.checkpointId?.value
    val checkpointOrdinalRaw: Int?
        get() = checkpointKey?.checkpointIndex?.value
    val checkpointPartitionIds: List<String>
        get() = checkpointIdRaw?.let { listOf(it) } ?: listOf()
    val checkpoints: List<Checkpoint>

    val sourceStats: Stats?
    val destinationStats: Stats?
    val additionalProperties: Map<String, Any>
    val serializedSizeBytes: Long
    val totalRecords: Long?
    val totalBytes: Long?
    val totalRejectedRecords: Long?
    val additionalStats: MutableMap<String, Double>

    fun updateStats(
        destinationStats: Stats? = null,
        totalRecords: Long? = null,
        totalBytes: Long? = null,
        totalRejectedRecords: Long? = null,
        additionalStats: Map<String, Double> = emptyMap()
    )
    fun withDestinationStats(stats: Stats): CheckpointMessage

    fun decorateStateMessage(message: AirbyteStateMessage) {
        sourceStats?.let {
            message.sourceStats =
                AirbyteStateStats().apply {
                    withRecordCount(it.recordCount.toDouble())
                    if (it.rejectedRecordCount > 0) {
                        withRejectedRecordCount(it.rejectedRecordCount.toDouble())
                    }
                }
        }
        val additionalStatsToAdd = this.additionalStats
        destinationStats?.let {
            message.destinationStats =
                AirbyteStateStats().apply {
                    withRecordCount(it.recordCount.toDouble())
                    if (it.rejectedRecordCount > 0) {
                        withRejectedRecordCount(it.rejectedRecordCount.toDouble())
                    }
                    if (additionalStatsToAdd.isNotEmpty()) {
                        withAdditionalStats(
                            AdditionalStats().apply {
                                additionalStatsToAdd.forEach {
                                    additionalProperties[it.key] = it.value
                                }
                            }
                        )
                    }
                }
        }
        additionalProperties.forEach { (key, value) -> message.withAdditionalProperty(key, value) }
        checkpointKey?.let {
            message.additionalProperties[CHECKPOINT_INDEX_NAME] = it.checkpointIndex.value
            message.additionalProperties[CHECKPOINT_ID_NAME] = it.checkpointId.value
        }

        if (totalRecords != null) {
            message.additionalProperties[COMMITTED_RECORDS_COUNT] = totalRecords
        }
        if (totalBytes != null) {
            message.additionalProperties[COMMITTED_BYTES_COUNT] = totalBytes
        }
        totalRejectedRecords?.let {
            if (it > 0) {
                message.additionalProperties[REJECTED_RECORDS_COUNT] = totalRejectedRecords
            }
        }
    }
}

data class StreamCheckpoint(
    val checkpoint: CheckpointMessage.Checkpoint,
    override val sourceStats: CheckpointMessage.Stats?,
    override var destinationStats: CheckpointMessage.Stats? = null,
    override val additionalProperties: Map<String, Any> = emptyMap(),
    override val serializedSizeBytes: Long,
    override val checkpointKey: CheckpointKey? = null,
    override var totalRecords: Long? = null,
    override var totalBytes: Long? = null,
    override var totalRejectedRecords: Long? = null,
    override var additionalStats: MutableMap<String, Double> = mutableMapOf(),
) : CheckpointMessage {
    /** Convenience constructor, intended for use in tests. */
    constructor(
        unmappedNamespace: String?,
        unmappedName: String,
        blob: String,
        sourceRecordCount: Long,
        additionalProperties: Map<String, Any> = emptyMap(),
        destinationRecordCount: Long? = null,
        checkpointKey: CheckpointKey? = null,
        totalRecords: Long? = null,
        totalBytes: Long? = null,
        additionalStats: MutableMap<String, Double> = mutableMapOf(),
    ) : this(
        CheckpointMessage.Checkpoint(
            unmappedNamespace = unmappedNamespace,
            unmappedName = unmappedName,
            state = blob.deserializeToNode(),
        ),
        CheckpointMessage.Stats(sourceRecordCount),
        destinationRecordCount?.let {
            CheckpointMessage.Stats(recordCount = it, additionalStats = additionalStats)
        },
        additionalProperties,
        serializedSizeBytes = 0L,
        checkpointKey = checkpointKey,
        totalRecords = totalRecords,
        totalBytes = totalBytes,
        additionalStats = additionalStats,
    )

    override val checkpoints: List<CheckpointMessage.Checkpoint>
        get() = emptyList()

    override fun updateStats(
        destinationStats: CheckpointMessage.Stats?,
        totalRecords: Long?,
        totalBytes: Long?,
        totalRejectedRecords: Long?,
        additionalStats: Map<String, Double>
    ) {
        destinationStats?.let { this.destinationStats = it }
        totalRecords?.let { this.totalRecords = it }
        totalBytes?.let { this.totalBytes = it }
        totalRejectedRecords?.let { this.totalRejectedRecords = it }
        this.additionalStats.putAll(additionalStats)
    }
    override fun withDestinationStats(stats: CheckpointMessage.Stats) =
        copy(destinationStats = stats, additionalStats = additionalStats)

    override fun asProtocolMessage(): AirbyteMessage {
        val stateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(checkpoint.asProtocolObject())
        decorateStateMessage(stateMessage)
        return AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(stateMessage)
    }
}

data class GlobalCheckpoint(
    val state: JsonNode?,
    override val sourceStats: CheckpointMessage.Stats?,
    override var destinationStats: CheckpointMessage.Stats? = null,
    override val checkpoints: List<CheckpointMessage.Checkpoint> = emptyList(),
    override val additionalProperties: Map<String, Any>,
    val originalTypeField: AirbyteStateMessage.AirbyteStateType? =
        AirbyteStateMessage.AirbyteStateType.GLOBAL,
    override val serializedSizeBytes: Long,
    override val checkpointKey: CheckpointKey? = null,
    override var totalRecords: Long? = null,
    override var totalBytes: Long? = null,
    override var totalRejectedRecords: Long? = null,
    override var additionalStats: MutableMap<String, Double> = mutableMapOf(),
) : CheckpointMessage {

    override fun updateStats(
        destinationStats: CheckpointMessage.Stats?,
        totalRecords: Long?,
        totalBytes: Long?,
        totalRejectedRecords: Long?,
        additionalStats: Map<String, Double>
    ) {
        destinationStats?.let { this.destinationStats = it }
        totalRecords?.let { this.totalRecords = it }
        totalBytes?.let { this.totalBytes = it }
        totalRejectedRecords?.let { this.totalRejectedRecords = it }
        this.additionalStats.putAll(additionalStats)
    }
    override fun withDestinationStats(stats: CheckpointMessage.Stats) =
        copy(destinationStats = stats)

    override fun asProtocolMessage(): AirbyteMessage {
        val stateMessage =
            AirbyteStateMessage()
                .withType(originalTypeField)
                .withGlobal(
                    AirbyteGlobalState()
                        .withSharedState(state)
                        .withStreamStates(checkpoints.map { it.asProtocolObject() }),
                )
        decorateStateMessage(stateMessage)
        return AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(stateMessage)
    }
}

data class GlobalSnapshotCheckpoint(
    val state: JsonNode?,
    override val sourceStats: CheckpointMessage.Stats?,
    override var destinationStats: CheckpointMessage.Stats? = null,
    override val checkpoints: List<CheckpointMessage.Checkpoint> = emptyList(),
    override val additionalProperties: Map<String, Any>,
    val originalTypeField: AirbyteStateMessage.AirbyteStateType? =
        AirbyteStateMessage.AirbyteStateType.GLOBAL,
    override val serializedSizeBytes: Long,
    override val checkpointKey: CheckpointKey? = null,
    override var totalRecords: Long? = null,
    override var totalBytes: Long? = null,
    override var totalRejectedRecords: Long? = null,
    override var additionalStats: MutableMap<String, Double> = mutableMapOf(),
    val streamCheckpoints: Map<DestinationStream.Descriptor, CheckpointKey>
) : CheckpointMessage {

    override val checkpointPartitionIds: List<String>
        get() = buildList {
            streamCheckpoints.values.mapTo(this) { it.checkpointId.value }
            checkpointKey?.checkpointId?.value?.let { add(it) }
        }

    override fun updateStats(
        destinationStats: CheckpointMessage.Stats?,
        totalRecords: Long?,
        totalBytes: Long?,
        totalRejectedRecords: Long?,
        additionalStats: Map<String, Double>
    ) {
        destinationStats?.let { this.destinationStats = it }
        totalRecords?.let { this.totalRecords = it }
        totalBytes?.let { this.totalBytes = it }
        totalRejectedRecords?.let { this.totalRejectedRecords = it }
        this.additionalStats.putAll(additionalStats)
    }
    override fun withDestinationStats(stats: CheckpointMessage.Stats) =
        copy(destinationStats = stats)

    override fun asProtocolMessage(): AirbyteMessage {
        val stateMessage =
            AirbyteStateMessage()
                .withType(originalTypeField)
                .withGlobal(
                    AirbyteGlobalState()
                        .withSharedState(state)
                        .withStreamStates(checkpoints.map { it.asProtocolObject() }),
                )
        decorateStateMessage(stateMessage)
        return AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(stateMessage)
    }
}
