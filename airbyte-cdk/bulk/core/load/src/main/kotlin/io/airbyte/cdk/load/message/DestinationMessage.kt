/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.Meta.Companion.CHECKPOINT_ID_NAME
import io.airbyte.cdk.load.message.Meta.Companion.getEmittedAtMs
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.AirbyteTraceMessage
import io.airbyte.protocol.models.v0.StreamDescriptor
import java.util.*
import kotlin.collections.LinkedHashMap

/**
 * Internal representation of destination messages. These are intended to be specialized for
 * usability. Data should be unmarshalled to these from front-line deserialized objects.
 */
sealed interface DestinationMessage {
    fun asProtocolMessage(): AirbyteMessage
}

data class DestinationRecord(
    val stream: DestinationStream,
    val message: DestinationRecordSource,
    val serializedSizeBytes: Long,
    val checkpointId: CheckpointId? = null,
    val airbyteRawId: UUID,
) : DestinationMessage {
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
    val stream: DestinationStream,
    val emittedAtMs: Long,
) : DestinationMessage {
    override fun asProtocolMessage(): AirbyteMessage =
        statusToProtocolMessage(stream, emittedAtMs, AirbyteStreamStatus.COMPLETE)
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
 * For messages, we recognize but do not want to process. Different from [Undefined] mainly in that
 * we don't log a warning.
 */
data object Ignored : DestinationMessage {
    override fun asProtocolMessage(): AirbyteMessage {
        throw NotImplementedError(
            "Ignored messages cannot be safely converted back to a protocol object.",
        )
    }
}

// Moved from DestinationMessageFactory
data object ProbeMessage : DestinationMessage {
    override fun asProtocolMessage(): AirbyteMessage {
        throw UnsupportedOperationException(
            "ProbeMessage cannot be converted to AirbyteMessage. " +
                "It is only used by the source to verify that the data channel is open."
        )
    }
}
