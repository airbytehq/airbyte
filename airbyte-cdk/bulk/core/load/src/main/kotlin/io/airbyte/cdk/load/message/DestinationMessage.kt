/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.json.AirbyteValueToJson
import io.airbyte.cdk.load.data.json.JsonToAirbyteValue
import io.airbyte.cdk.load.message.CheckpointMessage.Checkpoint
import io.airbyte.cdk.load.message.CheckpointMessage.Stats
import io.airbyte.protocol.models.Jsons
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import jakarta.inject.Singleton

/**
 * Internal representation of destination messages. These are intended to be specialized for
 * usability. Data should be marshalled to these from frontline deserialized objects.
 */
sealed interface DestinationMessage {
    fun asProtocolMessage(): AirbyteMessage
}

/** Records. */
sealed interface DestinationStreamAffinedMessage : DestinationMessage {
    val stream: DestinationStream.Descriptor
}

sealed interface DestinationRecordDomainMessage : DestinationStreamAffinedMessage

sealed interface DestinationFileDomainMessage : DestinationStreamAffinedMessage

data class DestinationRecord(
    override val stream: DestinationStream.Descriptor,
    val data: AirbyteValue,
    val emittedAtMs: Long,
    val meta: Meta?,
    val serialized: String,
) : DestinationRecordDomainMessage {
    /** Convenience constructor, primarily intended for use in tests. */
    constructor(
        namespace: String?,
        name: String,
        data: String,
        emittedAtMs: Long,
        changes: MutableList<Change> = mutableListOf(),
    ) : this(
        stream = DestinationStream.Descriptor(namespace, name),
        data = JsonToAirbyteValue().convert(Jsons.deserialize(data), ObjectTypeWithoutSchema),
        emittedAtMs = emittedAtMs,
        meta = Meta(changes),
        serialized = "",
    )

    data class Meta(val changes: MutableList<Change> = mutableListOf()) {
        companion object {
            const val COLUMN_NAME_AB_RAW_ID: String = "_airbyte_raw_id"
            const val COLUMN_NAME_AB_EXTRACTED_AT: String = "_airbyte_extracted_at"
            const val COLUMN_NAME_AB_META: String = "_airbyte_meta"
            const val COLUMN_NAME_AB_GENERATION_ID: String = "_airbyte_generation_id"
            const val COLUMN_NAME_DATA: String = "_airbyte_data"
        }

        fun asProtocolObject(): AirbyteRecordMessageMeta =
            AirbyteRecordMessageMeta()
                .withChanges(changes.map { change -> change.asProtocolObject() })
    }

    data class Change(
        val field: String,
        // Using the raw protocol enums here.
        // By definition, we just want to pass these through directly.
        val change: AirbyteRecordMessageMetaChange.Change,
        val reason: AirbyteRecordMessageMetaChange.Reason,
    ) {
        fun asProtocolObject(): AirbyteRecordMessageMetaChange =
            AirbyteRecordMessageMetaChange().withField(field).withChange(change).withReason(reason)
    }

    override fun asProtocolMessage(): AirbyteMessage =
        AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(
                AirbyteRecordMessage()
                    .withStream(stream.name)
                    .withNamespace(stream.namespace)
                    .withEmittedAt(emittedAtMs)
                    .withData(AirbyteValueToJson().convert(data))
                    .also {
                        if (meta != null) {
                            it.meta = meta.asProtocolObject()
                        }
                    }
            )
}

data class DestinationFile(
    override val stream: DestinationStream.Descriptor,
    val emittedAtMs: Long,
    val serialized: String,
    val fileMessage: AirbyteRecordMessageFile
) : DestinationFileDomainMessage {
    /** Convenience constructor, primarily intended for use in tests. */
    constructor(
        namespace: String?,
        name: String,
        emittedAtMs: Long,
        fileMessage: AirbyteRecordMessageFile
    ) : this(
        stream = DestinationStream.Descriptor(namespace, name),
        emittedAtMs = emittedAtMs,
        serialized = "",
        fileMessage = fileMessage
    )

    class AirbyteRecordMessageFile {
        constructor(
            fileUrl: String? = null,
            bytes: Long? = null,
            fileRelativePath: String? = null,
            modified: Long? = null,
            sourceFileUrl: String? = null
        ) {
            this.fileUrl = fileUrl
            this.bytes = bytes
            this.fileRelativePath = fileRelativePath
            this.modified = modified
            this.sourceFileUrl = sourceFileUrl
        }
        constructor() :
            this(
                fileUrl = null,
                bytes = null,
                fileRelativePath = null,
                modified = null,
                sourceFileUrl = null
            )

        @get:JsonProperty("file_url")
        @set:JsonProperty("file_url")
        @JsonProperty("file_url")
        var fileUrl: String? = null

        @get:JsonProperty("bytes")
        @set:JsonProperty("bytes")
        @JsonProperty("bytes")
        var bytes: Long? = null

        @get:JsonProperty("file_relative_path")
        @set:JsonProperty("file_relative_path")
        @JsonProperty("file_relative_path")
        var fileRelativePath: String? = null

        @get:JsonProperty("modified")
        @set:JsonProperty("modified")
        @JsonProperty("modified")
        var modified: Long? = null

        @get:JsonProperty("source_file_url")
        @set:JsonProperty("source_file_url")
        @JsonProperty("source_file_url")
        var sourceFileUrl: String? = null
    }

    override fun asProtocolMessage(): AirbyteMessage =
        AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(
                AirbyteRecordMessage()
                    .withStream(stream.name)
                    .withNamespace(stream.namespace)
                    .withEmittedAt(emittedAtMs)
                    .withAdditionalProperty("file_url", fileMessage.fileUrl)
                    .withAdditionalProperty("file_relative_path", fileMessage.fileRelativePath)
                    .withAdditionalProperty("source_file_url", fileMessage.sourceFileUrl)
                    .withAdditionalProperty("modified", fileMessage.modified)
                    .withAdditionalProperty("bytes", fileMessage.bytes)
            )
}

private fun statusToProtocolMessage(
    stream: DestinationStream.Descriptor,
    emittedAtMs: Long,
    status: AirbyteStreamStatus,
): AirbyteMessage =
    AirbyteMessage()
        .withType(AirbyteMessage.Type.TRACE)
        .withTrace(
            AirbyteTraceMessage()
                .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                .withEmittedAt(emittedAtMs.toDouble())
                .withStreamStatus(
                    AirbyteStreamStatusTraceMessage()
                        .withStreamDescriptor(stream.asProtocolObject())
                        .withStatus(status)
                )
        )

data class DestinationRecordStreamComplete(
    override val stream: DestinationStream.Descriptor,
    val emittedAtMs: Long,
) : DestinationRecordDomainMessage {
    override fun asProtocolMessage(): AirbyteMessage =
        statusToProtocolMessage(stream, emittedAtMs, AirbyteStreamStatus.COMPLETE)
}

data class DestinationRecordStreamIncomplete(
    override val stream: DestinationStream.Descriptor,
    val emittedAtMs: Long,
) : DestinationRecordDomainMessage {
    override fun asProtocolMessage(): AirbyteMessage =
        statusToProtocolMessage(stream, emittedAtMs, AirbyteStreamStatus.INCOMPLETE)
}

data class DestinationFileStreamComplete(
    override val stream: DestinationStream.Descriptor,
    val emittedAtMs: Long,
) : DestinationFileDomainMessage {
    override fun asProtocolMessage(): AirbyteMessage =
        statusToProtocolMessage(stream, emittedAtMs, AirbyteStreamStatus.COMPLETE)
}

data class DestinationFileStreamIncomplete(
    override val stream: DestinationStream.Descriptor,
    val emittedAtMs: Long,
) : DestinationFileDomainMessage {
    override fun asProtocolMessage(): AirbyteMessage =
        statusToProtocolMessage(stream, emittedAtMs, AirbyteStreamStatus.INCOMPLETE)
}

/** State. */
sealed interface CheckpointMessage : DestinationMessage {
    data class Stats(val recordCount: Long)
    data class Checkpoint(
        val stream: DestinationStream.Descriptor,
        val state: JsonNode,
    ) {
        fun asProtocolObject(): AirbyteStreamState =
            AirbyteStreamState()
                .withStreamDescriptor(stream.asProtocolObject())
                .withStreamState(state)
    }

    val sourceStats: Stats?
    val destinationStats: Stats?

    fun withDestinationStats(stats: Stats): CheckpointMessage
}

data class StreamCheckpoint(
    val checkpoint: Checkpoint,
    override val sourceStats: Stats?,
    override val destinationStats: Stats? = null,
    val additionalProperties: Map<String, Any>
) : CheckpointMessage {
    /** Convenience constructor, intended for use in tests. */
    constructor(
        streamNamespace: String?,
        streamName: String,
        blob: String,
        sourceRecordCount: Long,
        destinationRecordCount: Long? = null,
    ) : this(
        Checkpoint(
            DestinationStream.Descriptor(streamNamespace, streamName),
            state = Jsons.deserialize(blob)
        ),
        Stats(sourceRecordCount),
        destinationRecordCount?.let { Stats(it) },
        additionalProperties = mutableMapOf(),
    )

    override fun withDestinationStats(stats: Stats) =
        StreamCheckpoint(checkpoint, sourceStats, stats, additionalProperties)

    override fun asProtocolMessage(): AirbyteMessage {
        val stateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
                .withStream(checkpoint.asProtocolObject())
                .also {
                    if (sourceStats != null) {
                        it.sourceStats =
                            AirbyteStateStats().withRecordCount(sourceStats.recordCount.toDouble())
                    }
                    if (destinationStats != null) {
                        it.destinationStats =
                            AirbyteStateStats()
                                .withRecordCount(destinationStats.recordCount.toDouble())
                    }
                    additionalProperties.forEach { (key, value) ->
                        it.withAdditionalProperty(key, value)
                    }
                }
        return AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(stateMessage)
    }
}

data class GlobalCheckpoint(
    val state: JsonNode,
    override val sourceStats: Stats?,
    override val destinationStats: Stats? = null,
    val checkpoints: List<Checkpoint> = emptyList(),
    val additionalProperties: MutableMap<String, Any> = mutableMapOf()
) : CheckpointMessage {
    /** Convenience constructor, primarily intended for use in tests. */
    constructor(
        blob: String,
        sourceRecordCount: Long,
    ) : this(state = Jsons.deserialize(blob), Stats(sourceRecordCount))
    override fun withDestinationStats(stats: Stats) =
        GlobalCheckpoint(state, sourceStats, stats, checkpoints, additionalProperties)

    override fun asProtocolMessage(): AirbyteMessage {
        val stateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                .withGlobal(
                    AirbyteGlobalState()
                        .withSharedState(state)
                        .withStreamStates(checkpoints.map { it.asProtocolObject() })
                )
                .also {
                    if (sourceStats != null) {
                        it.sourceStats =
                            AirbyteStateStats().withRecordCount(sourceStats.recordCount.toDouble())
                    }
                    if (destinationStats != null) {
                        it.destinationStats =
                            AirbyteStateStats()
                                .withRecordCount(destinationStats.recordCount.toDouble())
                    }
                    it.additionalProperties.forEach { (key, value) ->
                        it.withAdditionalProperty(key, value)
                    }
                }
        return AirbyteMessage().withType(AirbyteMessage.Type.STATE).withState(stateMessage)
    }
}

/** Catchall for anything unimplemented. */
data object Undefined : DestinationMessage {
    override fun asProtocolMessage(): AirbyteMessage {
        // Arguably we could accept the raw message in the constructor?
        // But that seems weird - when would we ever want to reemit that message?
        throw NotImplementedError(
            "Unrecognized messages cannot be safely converted back to a protocol object."
        )
    }
}

@Singleton
class DestinationMessageFactory(private val catalog: DestinationCatalog) {
    fun fromAirbyteMessage(message: AirbyteMessage, serialized: String): DestinationMessage {
        return when (message.type) {
            AirbyteMessage.Type.RECORD -> {
                val stream =
                    catalog.getStream(
                        namespace = message.record.namespace,
                        name = message.record.stream,
                    )
                // TODO: File transfer check
                if (true) {
                    DestinationRecord(
                        stream = stream.descriptor,
                        data = JsonToAirbyteValue().convert(message.record.data, stream.schema),
                        emittedAtMs = message.record.emittedAt,
                        meta =
                            DestinationRecord.Meta(
                                changes =
                                    message.record.meta
                                        ?.changes
                                        ?.map {
                                            DestinationRecord.Change(
                                                field = it.field,
                                                change = it.change,
                                                reason = it.reason,
                                            )
                                        }
                                        ?.toMutableList()
                                        ?: mutableListOf()
                            ),
                        serialized = serialized
                    )
                } else {
                    DestinationFile(
                        stream = stream.descriptor,
                        emittedAtMs = message.record.emittedAt,
                        serialized = serialized,
                        fileMessage =
                            DestinationFile.AirbyteRecordMessageFile(
                                fileUrl =
                                    message.record.additionalProperties["file_url"] as String?,
                                bytes = message.record.additionalProperties["bytes"] as Long?,
                                fileRelativePath =
                                    message.record.additionalProperties["file_relative_path"]
                                        as String?,
                                modified = message.record.additionalProperties["modified"] as Long?,
                                sourceFileUrl =
                                    message.record.additionalProperties["source_file_url"]
                                        as String?
                            )
                    )
                }
            }
            AirbyteMessage.Type.TRACE -> {
                val status = message.trace.streamStatus
                val stream =
                    catalog.getStream(
                        namespace = status.streamDescriptor.namespace,
                        name = status.streamDescriptor.name,
                    )
                if (message.trace.type == AirbyteTraceMessage.Type.STREAM_STATUS) {
                    // TODO: File transfer FF
                    when (status.status) {
                        AirbyteStreamStatus.COMPLETE ->
                            if (true) {
                                DestinationRecordStreamComplete(
                                    stream.descriptor,
                                    message.trace.emittedAt.toLong()
                                )
                            } else {
                                DestinationFileStreamComplete(
                                    stream.descriptor,
                                    message.trace.emittedAt.toLong()
                                )
                            }
                        AirbyteStreamStatus.INCOMPLETE ->
                            if (true) {
                                DestinationRecordStreamIncomplete(
                                    stream.descriptor,
                                    message.trace.emittedAt.toLong()
                                )
                            } else {
                                DestinationFileStreamIncomplete(
                                    stream.descriptor,
                                    message.trace.emittedAt.toLong()
                                )
                            }
                        else -> Undefined
                    }
                } else {
                    Undefined
                }
            }
            AirbyteMessage.Type.STATE -> {
                when (message.state.type) {
                    AirbyteStateMessage.AirbyteStateType.STREAM ->
                        StreamCheckpoint(
                            checkpoint = fromAirbyteStreamState(message.state.stream),
                            sourceStats =
                                message.state.sourceStats?.recordCount?.let {
                                    Stats(recordCount = it.toLong())
                                },
                            additionalProperties = message.state.additionalProperties
                        )
                    AirbyteStateMessage.AirbyteStateType.GLOBAL ->
                        GlobalCheckpoint(
                            sourceStats =
                                message.state.sourceStats?.recordCount?.let {
                                    Stats(recordCount = it.toLong())
                                },
                            state = message.state.global.sharedState,
                            checkpoints =
                                message.state.global.streamStates.map {
                                    fromAirbyteStreamState(it)
                                },
                            additionalProperties = message.state.additionalProperties
                        )
                    else -> // TODO: Do we still need to handle LEGACY?
                    Undefined
                }
            }
            else -> Undefined
        }
    }

    private fun fromAirbyteStreamState(streamState: AirbyteStreamState): Checkpoint {
        val descriptor = streamState.streamDescriptor
        return Checkpoint(
            stream = DestinationStream.Descriptor(descriptor.namespace, descriptor.name),
            state = streamState.streamState
        )
    }
}
