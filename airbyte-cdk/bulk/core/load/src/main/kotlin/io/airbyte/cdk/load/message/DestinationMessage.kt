/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueCoercer.DATE_TIME_FORMATTER
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.data.toAirbyteValues
import io.airbyte.cdk.load.message.CheckpointMessage.Checkpoint
import io.airbyte.cdk.load.message.CheckpointMessage.Stats
import io.airbyte.cdk.load.message.Meta.Companion.CHECKPOINT_ID_NAME
import io.airbyte.cdk.load.message.Meta.Companion.CHECKPOINT_INDEX_NAME
import io.airbyte.cdk.load.message.Meta.Companion.getEmittedAtMs
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointKey
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageFileReference
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.*
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.math.BigInteger
import java.time.Instant
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.util.*
import kotlin.collections.LinkedHashMap

/**
 * Internal representation of destination messages. These are intended to be specialized for
 * usability. Data should be unmarshalled to these from front-line deserialized objects.
 */
sealed interface DestinationMessage {
    fun asProtocolMessage(): AirbyteMessage
}

/** Records. */
sealed interface DestinationStreamAffinedMessage : DestinationMessage {
    val stream: DestinationStream
}

sealed interface DestinationRecordDomainMessage : DestinationStreamAffinedMessage

sealed interface DestinationFileDomainMessage : DestinationStreamAffinedMessage

data class Meta(
    val changes: List<Change> = mutableListOf(),
) {
    enum class AirbyteMetaFields(val fieldName: String, val type: AirbyteType) {
        RAW_ID(COLUMN_NAME_AB_RAW_ID, StringType),
        EXTRACTED_AT(COLUMN_NAME_AB_EXTRACTED_AT, IntegerType),
        META(
            COLUMN_NAME_AB_META,
            ObjectType(
                linkedMapOf(
                    "sync_id" to FieldType(IntegerType, nullable = false),
                    "changes" to
                        FieldType(
                            nullable = false,
                            type =
                                ArrayType(
                                    FieldType(
                                        nullable = false,
                                        type =
                                            ObjectType(
                                                linkedMapOf(
                                                    "field" to
                                                        FieldType(
                                                            StringType,
                                                            nullable = false,
                                                        ),
                                                    "change" to
                                                        FieldType(
                                                            StringType,
                                                            nullable = false,
                                                        ),
                                                    "reason" to
                                                        FieldType(
                                                            StringType,
                                                            nullable = false,
                                                        ),
                                                ),
                                            ),
                                    ),
                                ),
                        ),
                ),
            ),
        ),
        GENERATION_ID(COLUMN_NAME_AB_META, IntegerType),
    }

    companion object {
        const val CHECKPOINT_ID_NAME: String = "partition_id"
        const val CHECKPOINT_INDEX_NAME: String = "id"

        const val AIRBYTE_META_SYNC_ID = "sync_id"
        const val AIRBYTE_META_CHANGES = "changes"

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

        /**
         * A legacy column name. Destinations with "typing and deduping" used this in the raw tables
         * to indicate when a record went through T+D.
         */
        const val COLUMN_NAME_AB_LOADED_AT: String = "_airbyte_loaded_at"

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
                                DATE_TIME_FORMATTER,
                            ),
                        )
                    }
                }
                COLUMN_NAME_AB_META -> toObjectValue(value.deserializeToNode())
                COLUMN_NAME_AB_GENERATION_ID -> IntegerValue(BigInteger(value))
                COLUMN_NAME_DATA -> toObjectValue(value.deserializeToNode())
                else ->
                    throw NotImplementedError(
                        "Column name $metaColumnName is not yet supported. This is probably a bug.",
                    )
            }
        }

        fun getEmittedAtMs(
            emittedAtMs: Long,
            extractedAtAsTimestampWithTimezone: Boolean
        ): AirbyteValue {
            return if (extractedAtAsTimestampWithTimezone) {
                TimestampWithTimezoneValue(
                    OffsetDateTime.ofInstant(Instant.ofEpochMilli(emittedAtMs), ZoneOffset.UTC)
                )
            } else {
                IntegerValue(emittedAtMs)
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
        val reason: Reason,
    ) {
        fun asProtocolObject(): AirbyteRecordMessageMetaChange =
            AirbyteRecordMessageMetaChange().withField(field).withChange(change).withReason(reason)
    }
}

data class DestinationRecord(
    override val stream: DestinationStream,
    val message: DestinationRecordSource,
    val serializedSizeBytes: Long,
    val checkpointId: CheckpointId? = null,
    val airbyteRawId: UUID,
) : DestinationRecordDomainMessage {
    override fun asProtocolMessage(): AirbyteMessage =
        AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(
                AirbyteRecordMessage()
                    .withNamespace(stream.unmappedNamespace)
                    .withStream(stream.unmappedName)
                    .withEmittedAt(message.emittedAtMs)
                    .withData(message.asJsonRecord(stream.airbyteValueProxyFieldAccessors))
                    .also {
                        if (checkpointId != null) {
                            it.additionalProperties[CHECKPOINT_ID_NAME] = checkpointId.value
                        }
                    }
                    .withMeta(
                        AirbyteRecordMessageMeta()
                            .withChanges(
                                message.sourceMeta.changes.map { change ->
                                    Meta.Change(
                                            field = change.field,
                                            change = change.change,
                                            reason = change.reason,
                                        )
                                        .asProtocolObject()
                                },
                            ),
                    )
            )

    fun asDestinationRecordRaw(): DestinationRecordRaw {
        return DestinationRecordRaw(
            stream = stream,
            rawData = message,
            serializedSizeBytes = serializedSizeBytes,
            checkpointId = checkpointId,
            airbyteRawId = airbyteRawId,
        )
    }
}

/**
 * Represents a record already in its serialized state. The intended use is for conveying records
 * from stdin to the spill file, where reserialization is not necessary.
 */
data class DestinationRecordSerialized(val stream: DestinationStream, val serialized: String)

/** Represents a record both deserialized AND marshaled to airbyte value. The marshaling */
data class DestinationRecordAirbyteValue(
    val stream: DestinationStream,
    val data: AirbyteValue,
    val emittedAtMs: Long,
    val meta: Meta?,
    val serializedSizeBytes: Long = 0L
)

data class EnrichedDestinationRecordAirbyteValue(
    val stream: DestinationStream,
    val declaredFields: LinkedHashMap<String, EnrichedAirbyteValue>,
    val undeclaredFields: LinkedHashMap<String, JsonNode>,
    val emittedAtMs: Long,
    /**
     * The airbyte_meta field as received by the destination connector. Note that this field is NOT
     * updated by [EnrichedAirbyteValue.nullify] / [EnrichedAirbyteValue.truncate].
     *
     * If you want an up-to-date view of airbyte_meta, including any changes that were done to the
     * values within the destination connector, you should use [airbyteMeta].
     */
    val sourceMeta: Meta,
    val serializedSizeBytes: Long = 0L,
    private val extractedAtAsTimestampWithTimezone: Boolean = false,
    val airbyteRawId: UUID,
) {
    val airbyteMeta: EnrichedAirbyteValue
        get() =
            EnrichedAirbyteValue(
                ObjectValue(
                    linkedMapOf(
                        Meta.AIRBYTE_META_SYNC_ID to IntegerValue(stream.syncId),
                        Meta.AIRBYTE_META_CHANGES to
                            ArrayValue(
                                (sourceMeta.changes.toAirbyteValues()) +
                                    declaredFields
                                        .map { it.value.changes.toAirbyteValues() }
                                        .flatten(),
                            ),
                    ),
                ),
                Meta.AirbyteMetaFields.META.type,
                name = Meta.COLUMN_NAME_AB_META,
                airbyteMetaField = Meta.AirbyteMetaFields.META,
            )

    val airbyteMetaFields: Map<String, EnrichedAirbyteValue>
        get() =
            mapOf(
                Meta.COLUMN_NAME_AB_RAW_ID to
                    EnrichedAirbyteValue(
                        StringValue(airbyteRawId.toString()),
                        Meta.AirbyteMetaFields.RAW_ID.type,
                        name = Meta.COLUMN_NAME_AB_RAW_ID,
                        airbyteMetaField = Meta.AirbyteMetaFields.RAW_ID,
                    ),
                Meta.COLUMN_NAME_AB_EXTRACTED_AT to
                    EnrichedAirbyteValue(
                        getEmittedAtMs(emittedAtMs, extractedAtAsTimestampWithTimezone),
                        Meta.AirbyteMetaFields.EXTRACTED_AT.type,
                        name = Meta.COLUMN_NAME_AB_EXTRACTED_AT,
                        airbyteMetaField = Meta.AirbyteMetaFields.EXTRACTED_AT,
                    ),
                Meta.COLUMN_NAME_AB_META to airbyteMeta,
                Meta.COLUMN_NAME_AB_GENERATION_ID to
                    EnrichedAirbyteValue(
                        IntegerValue(stream.generationId),
                        Meta.AirbyteMetaFields.GENERATION_ID.type,
                        name = Meta.COLUMN_NAME_AB_GENERATION_ID,
                        airbyteMetaField = Meta.AirbyteMetaFields.GENERATION_ID,
                    ),
            )

    val allTypedFields: Map<String, EnrichedAirbyteValue>
        get() = declaredFields + airbyteMetaFields
}

data class FileReference(
    val stagingFileUrl: String,
    val sourceFileRelativePath: String,
    val fileSizeBytes: Long,
) {
    companion object {
        fun fromProtocol(proto: AirbyteRecordMessageFileReference): FileReference =
            FileReference(
                proto.stagingFileUrl,
                proto.sourceFileRelativePath,
                proto.fileSizeBytes,
            )
    }
}

data class DestinationFile(
    override val stream: DestinationStream,
    val emittedAtMs: Long,
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
                sourceFileUrl = null,
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
                    .withStream(stream.unmappedName)
                    .withNamespace(stream.unmappedNamespace)
                    .withEmittedAt(emittedAtMs)
                    .withAdditionalProperty("file", file),
            )
    }
}

private fun statusToProtocolMessage(
    destinationStream: DestinationStream,
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
                        .withStreamDescriptor(
                            StreamDescriptor()
                                .withNamespace(destinationStream.unmappedNamespace)
                                .withName(destinationStream.unmappedName)
                        )
                        .withStatus(status),
                ),
        )

data class DestinationRecordStreamComplete(
    override val stream: DestinationStream,
    val emittedAtMs: Long,
) : DestinationRecordDomainMessage {
    override fun asProtocolMessage(): AirbyteMessage =
        statusToProtocolMessage(stream, emittedAtMs, AirbyteStreamStatus.COMPLETE)
}

data class DestinationFileStreamComplete(
    override val stream: DestinationStream,
    val emittedAtMs: Long,
) : DestinationFileDomainMessage {
    override fun asProtocolMessage(): AirbyteMessage =
        statusToProtocolMessage(stream, emittedAtMs, AirbyteStreamStatus.COMPLETE)
}

/** State. */
sealed interface CheckpointMessage : DestinationMessage {
    companion object {
        private const val COMMITTED_RECORDS_COUNT = "committedRecordsCount"
        private const val COMMITTED_BYTES_COUNT = "committedBytesCount"
    }
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

    val checkpointKey: CheckpointKey?

    val sourceStats: Stats?
    val destinationStats: Stats?
    val additionalProperties: Map<String, Any>
    val serializedSizeBytes: Long
    val totalRecords: Long?
    val totalBytes: Long?

    fun withDestinationStats(stats: Stats): CheckpointMessage
    fun withTotalRecords(totalRecords: Long): CheckpointMessage
    fun withTotalBytes(totalBytes: Long): CheckpointMessage

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
    }
}

data class StreamCheckpoint(
    val checkpoint: Checkpoint,
    override val sourceStats: Stats?,
    override val destinationStats: Stats? = null,
    override val additionalProperties: Map<String, Any> = emptyMap(),
    override val serializedSizeBytes: Long,
    override val checkpointKey: CheckpointKey? = null,
    override val totalRecords: Long? = null,
    override val totalBytes: Long? = null
) : CheckpointMessage {
    /** Convenience constructor, intended for use in tests. */
    constructor(
        streamNamespace: String?,
        streamName: String,
        blob: String,
        sourceRecordCount: Long,
        destinationRecordCount: Long? = null,
        checkpointKey: CheckpointKey? = null,
        totalRecords: Long? = null,
        totalBytes: Long? = null
    ) : this(
        Checkpoint(
            DestinationStream.Descriptor(streamNamespace, streamName),
            state = blob.deserializeToNode(),
        ),
        Stats(sourceRecordCount),
        destinationRecordCount?.let { Stats(it) },
        emptyMap(),
        serializedSizeBytes = 0L,
        checkpointKey = checkpointKey,
        totalRecords = totalRecords,
        totalBytes = totalBytes
    )

    override fun withDestinationStats(stats: Stats) = copy(destinationStats = stats)
    override fun withTotalRecords(totalRecords: Long) = copy(totalRecords = totalRecords)
    override fun withTotalBytes(totalBytes: Long) = copy(totalBytes = totalBytes)

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
    override val serializedSizeBytes: Long,
    override val checkpointKey: CheckpointKey? = null,
    override val totalRecords: Long? = null,
    override val totalBytes: Long? = null,
) : CheckpointMessage {
    /** Convenience constructor, primarily intended for use in tests. */
    constructor(
        blob: String,
        sourceRecordCount: Long,
    ) : this(
        state = blob.deserializeToNode(),
        Stats(sourceRecordCount),
        additionalProperties = emptyMap(),
        serializedSizeBytes = 0L,
    )
    override fun withDestinationStats(stats: Stats) = copy(destinationStats = stats)
    override fun withTotalRecords(totalRecords: Long): CheckpointMessage =
        copy(totalRecords = totalRecords)

    override fun withTotalBytes(totalBytes: Long): CheckpointMessage = copy(totalBytes = totalBytes)

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

/** Catchall for anything unimplemented. */
data object Undefined : DestinationMessage {
    override fun asProtocolMessage(): AirbyteMessage {
        // Arguably we could accept the raw message in the constructor?
        // But that seems weird - when would we ever want to reemit that message?
        throw NotImplementedError(
            "Unrecognized messages cannot be safely converted back to a protocol object.",
        )
    }
}

/**
 * For messages we recognize but do not want to process. Different from [Undefined] mainly in that
 * we don't log a warning.
 */
data object Ignored : DestinationMessage {
    override fun asProtocolMessage(): AirbyteMessage {
        throw NotImplementedError(
            "Ignored messages cannot be safely converted back to a protocol object.",
        )
    }
}
