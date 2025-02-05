/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueDeepCoercingMapper
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.message.CheckpointMessage.Checkpoint
import io.airbyte.cdk.load.message.CheckpointMessage.Stats
import io.airbyte.cdk.load.util.deserializeToNode
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
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.math.BigInteger
import java.time.OffsetDateTime

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

data class Meta(
    val changes: List<Change> = mutableListOf(),
) {
    companion object {
        const val COLUMN_NAME_AB_RAW_ID: String = "_airbyte_raw_id"
        const val COLUMN_NAME_AB_EXTRACTED_AT: String = "_airbyte_extracted_at"
        const val COLUMN_NAME_AB_META: String = "_airbyte_meta"
        const val COLUMN_NAME_AB_GENERATION_ID: String = "_airbyte_generation_id"
        const val COLUMN_NAME_DATA: String = "_airbyte_data"
        val COLUMN_NAMES =
            setOf(
                COLUMN_NAME_AB_RAW_ID,
                COLUMN_NAME_AB_EXTRACTED_AT,
                COLUMN_NAME_AB_META,
                COLUMN_NAME_AB_GENERATION_ID,
            )

        fun getMetaValue(metaColumnName: String, value: String): AirbyteValue {
            if (!COLUMN_NAMES.contains(metaColumnName)) {
                throw IllegalArgumentException("Invalid meta column name: $metaColumnName")
            }
            fun toObjectValue(value: JsonNode): AirbyteValue {
                if (value.isTextual) {
                    return toObjectValue(value.textValue().deserializeToNode())
                }
                return value.toAirbyteValue()
            }
            return when (metaColumnName) {
                COLUMN_NAME_AB_RAW_ID -> StringValue(value)
                COLUMN_NAME_AB_EXTRACTED_AT -> {
                    // Some destinations represent extractedAt as a long epochMillis,
                    // and others represent it as a timestamp string.
                    // Handle both cases here.
                    try {
                        IntegerValue(BigInteger(value))
                    } catch (e: Exception) {
                        TimestampWithTimezoneValue(
                            OffsetDateTime.parse(
                                value,
                                AirbyteValueDeepCoercingMapper.DATE_TIME_FORMATTER
                            )
                        )
                    }
                }
                COLUMN_NAME_AB_META -> toObjectValue(value.deserializeToNode())
                COLUMN_NAME_AB_GENERATION_ID -> IntegerValue(BigInteger(value))
                COLUMN_NAME_DATA -> toObjectValue(value.deserializeToNode())
                else ->
                    throw NotImplementedError(
                        "Column name $metaColumnName is not yet supported. This is probably a bug."
                    )
            }
        }
    }

    fun asProtocolObject(): AirbyteRecordMessageMeta =
        AirbyteRecordMessageMeta().withChanges(changes.map { change -> change.asProtocolObject() })

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
}

data class DestinationRecord(
    override val stream: DestinationStream.Descriptor,
    val message: AirbyteMessage,
    val serialized: String,
    val schema: AirbyteType
) : DestinationRecordDomainMessage {
    override fun asProtocolMessage(): AirbyteMessage = message

    fun asRecordSerialized(): DestinationRecordSerialized =
        DestinationRecordSerialized(stream, serialized)
    fun asRecordMarshaledToAirbyteValue(): DestinationRecordAirbyteValue {
        return DestinationRecordAirbyteValue(
            stream,
            message.record.data.toAirbyteValue(),
            message.record.emittedAt,
            Meta(
                message.record.meta?.changes?.map { Meta.Change(it.field, it.change, it.reason) }
                    ?: emptyList()
            )
        )
    }
}

/**
 * Represents a record already in its serialized state. The intended use is for conveying records
 * from stdin to the spill file, where reserialization is not necessary.
 */
data class DestinationRecordSerialized(
    val stream: DestinationStream.Descriptor,
    val serialized: String
)

/** Represents a record both deserialized AND marshaled to airbyte value. The marshaling */
data class DestinationRecordAirbyteValue(
    val stream: DestinationStream.Descriptor,
    val data: AirbyteValue,
    val emittedAtMs: Long,
    val meta: Meta?,
)

data class DestinationFile(
    override val stream: DestinationStream.Descriptor,
    val emittedAtMs: Long,
    val serialized: String,
    val fileMessage: AirbyteRecordMessageFile
) : DestinationFileDomainMessage {
    /** Convenience constructor, primarily intended for use in tests. */
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

    override fun asProtocolMessage(): AirbyteMessage {
        val file =
            mapOf(
                "file_url" to fileMessage.fileUrl,
                "file_relative_path" to fileMessage.fileRelativePath,
                "source_file_url" to fileMessage.sourceFileUrl,
                "modified" to fileMessage.modified,
                "bytes" to fileMessage.bytes,
            )

        return AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(
                AirbyteRecordMessage()
                    .withStream(stream.name)
                    .withNamespace(stream.namespace)
                    .withEmittedAt(emittedAtMs)
                    .withAdditionalProperty("file", file)
            )
    }
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
        val state: JsonNode?,
    ) {
        fun asProtocolObject(): AirbyteStreamState =
            AirbyteStreamState().withStreamDescriptor(stream.asProtocolObject()).also {
                if (state != null) {
                    it.streamState = state
                }
            }
    }

    val sourceStats: Stats?
    val destinationStats: Stats?
    val additionalProperties: Map<String, Any>

    fun withDestinationStats(stats: Stats): CheckpointMessage

    fun decorateStateMessage(message: AirbyteStateMessage) {
        if (sourceStats != null) {
            message.sourceStats =
                AirbyteStateStats().withRecordCount(sourceStats!!.recordCount.toDouble())
        }
        if (destinationStats != null) {
            message.destinationStats =
                AirbyteStateStats().withRecordCount(destinationStats!!.recordCount.toDouble())
        }
        additionalProperties.forEach { (key, value) -> message.withAdditionalProperty(key, value) }
    }
}

data class StreamCheckpoint(
    val checkpoint: Checkpoint,
    override val sourceStats: Stats?,
    override val destinationStats: Stats? = null,
    override val additionalProperties: Map<String, Any> = emptyMap(),
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
            state = blob.deserializeToNode()
        ),
        Stats(sourceRecordCount),
        destinationRecordCount?.let { Stats(it) },
        emptyMap(),
    )

    override fun withDestinationStats(stats: Stats) = copy(destinationStats = stats)

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
    override val sourceStats: Stats?,
    override val destinationStats: Stats? = null,
    val checkpoints: List<Checkpoint> = emptyList(),
    override val additionalProperties: Map<String, Any>,
    val originalTypeField: AirbyteStateMessage.AirbyteStateType? =
        AirbyteStateMessage.AirbyteStateType.GLOBAL,
) : CheckpointMessage {
    /** Convenience constructor, primarily intended for use in tests. */
    constructor(
        blob: String,
        sourceRecordCount: Long,
    ) : this(
        state = blob.deserializeToNode(),
        Stats(sourceRecordCount),
        additionalProperties = emptyMap(),
    )
    override fun withDestinationStats(stats: Stats) = copy(destinationStats = stats)

    override fun asProtocolMessage(): AirbyteMessage {
        val stateMessage =
            AirbyteStateMessage()
                .withType(originalTypeField)
                .withGlobal(
                    AirbyteGlobalState()
                        .withSharedState(state)
                        .withStreamStates(checkpoints.map { it.asProtocolObject() })
                )
        decorateStateMessage(stateMessage)
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
class DestinationMessageFactory(
    private val catalog: DestinationCatalog,
    @Value("\${airbyte.destination.core.file-transfer.enabled}")
    private val fileTransferEnabled: Boolean,
) {
    fun fromAirbyteMessage(
        message: AirbyteMessage,
        serialized: String,
    ): DestinationMessage {
        fun toLong(value: Any?, name: String): Long? {
            return value?.let {
                when (it) {
                    // you can't cast java.lang.Integer -> java.lang.Long
                    // so instead we have to do this manual pattern match
                    is Int -> it.toLong()
                    is Long -> it
                    else ->
                        throw IllegalArgumentException(
                            "Unexpected value for $name: $it (${it::class.qualifiedName})"
                        )
                }
            }
        }

        return when (message.type) {
            AirbyteMessage.Type.RECORD -> {
                val stream =
                    catalog.getStream(
                        namespace = message.record.namespace,
                        name = message.record.stream,
                    )
                if (fileTransferEnabled) {
                    try {
                        @Suppress("UNCHECKED_CAST")
                        val fileMessage =
                            message.record.additionalProperties["file"] as Map<String, Any>

                        DestinationFile(
                            stream = stream.descriptor,
                            emittedAtMs = message.record.emittedAt,
                            serialized = serialized,
                            fileMessage =
                                DestinationFile.AirbyteRecordMessageFile(
                                    fileUrl = fileMessage["file_url"] as String?,
                                    bytes = toLong(fileMessage["bytes"], "message.record.bytes"),
                                    fileRelativePath = fileMessage["file_relative_path"] as String?,
                                    modified =
                                        toLong(fileMessage["modified"], "message.record.modified"),
                                    sourceFileUrl = fileMessage["source_file_url"] as String?
                                )
                        )
                    } catch (e: Exception) {
                        throw IllegalArgumentException(
                            "Failed to construct file message: ${e.message}"
                        )
                    }
                } else {
                    DestinationRecord(stream.descriptor, message, serialized, stream.schema)
                }
            }
            AirbyteMessage.Type.TRACE -> {
                val status = message.trace.streamStatus
                val stream =
                    catalog.getStream(
                        namespace = status.streamDescriptor.namespace,
                        name = status.streamDescriptor.name,
                    )
                if (
                    message.trace.type == null ||
                        message.trace.type == AirbyteTraceMessage.Type.STREAM_STATUS
                ) {
                    when (status.status) {
                        AirbyteStreamStatus.COMPLETE ->
                            if (fileTransferEnabled) {
                                DestinationFileStreamComplete(
                                    stream.descriptor,
                                    message.trace.emittedAt?.toLong() ?: 0L
                                )
                            } else {
                                DestinationRecordStreamComplete(
                                    stream.descriptor,
                                    message.trace.emittedAt?.toLong() ?: 0L
                                )
                            }
                        AirbyteStreamStatus.INCOMPLETE ->
                            if (fileTransferEnabled) {
                                DestinationFileStreamIncomplete(
                                    stream.descriptor,
                                    message.trace.emittedAt?.toLong() ?: 0L
                                )
                            } else {
                                DestinationRecordStreamIncomplete(
                                    stream.descriptor,
                                    message.trace.emittedAt?.toLong() ?: 0L
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
                            additionalProperties = message.state.additionalProperties,
                        )
                    null,
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
                            additionalProperties = message.state.additionalProperties,
                            originalTypeField = message.state.type,
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
            state = runCatching { streamState.streamState }.getOrNull()
        )
    }
}
