/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import com.fasterxml.jackson.databind.JsonNode
import com.google.protobuf.ByteString
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.AirbyteValueToProtobuf
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.data.json.JsonToAirbyteValue
import io.airbyte.cdk.load.data.json.toJson
import io.airbyte.cdk.load.message.CheckpointMessage.Checkpoint
import io.airbyte.cdk.load.message.CheckpointMessage.Stats
import io.airbyte.cdk.load.message.Meta.Companion.CHECKPOINT_ID_NAME
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointKey
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageFileReference
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessageMetaOuterClass
import java.io.OutputStream

sealed interface InputMessage {
    fun asProtocolMessage(): AirbyteMessage
    fun asProtobuf(): AirbyteMessageProtobuf =
        AirbyteMessageProtobuf.newBuilder()
            .setAirbyteProtocolMessage(asProtocolMessage().serializeToString())
            .build()

    fun writeProtocolMessage(
        dataChannelFormat: DataChannelFormat = DataChannelFormat.JSONL,
        outputStream: OutputStream
    ) {
        when (dataChannelFormat) {
            DataChannelFormat.JSONL ->
                asProtocolMessage().serializeToJsonBytes().also {
                    outputStream.write(it)
                    outputStream.write('\n'.code)
                }
            DataChannelFormat.PROTOBUF -> asProtobuf().writeDelimitedTo(outputStream)
            else ->
                throw IllegalArgumentException(
                    "Unsupported data channel format: $dataChannelFormat"
                )
        }
        outputStream.flush()
    }
}

data class InputRecord(
    val stream: DestinationStream,
    val data: AirbyteValue,
    val emittedAtMs: Long,
    val meta: Meta?,
    val serialized: String,
    val fileReference: AirbyteRecordMessageFileReference? = null,
    val checkpointId: CheckpointId? = null,
    val unknownFieldNames: Set<String> = emptySet(),
) : InputMessage {
    /** Convenience constructor, primarily intended for use in tests. */
    constructor(
        stream: DestinationStream,
        data: String,
        emittedAtMs: Long,
        changes: MutableList<Meta.Change> = mutableListOf(),
        fileReference: AirbyteRecordMessageFileReference? = null,
        checkpointId: CheckpointId? = null,
        unknownFieldNames: Set<String> = emptySet(),
    ) : this(
        stream = stream,
        data = JsonToAirbyteValue().convert(data.deserializeToNode()),
        emittedAtMs = emittedAtMs,
        meta = Meta(changes),
        serialized = data,
        fileReference,
        checkpointId,
        unknownFieldNames
    )

    override fun asProtobuf(): AirbyteMessageProtobuf {
        val recordBuilder =
            AirbyteRecordMessageProtobuf.newBuilder()
                .setStreamName(stream.unmappedName)
                .setEmittedAtMs(emittedAtMs)
        checkpointId?.let { recordBuilder.setPartitionId(it.value) }
        stream.unmappedNamespace?.let { recordBuilder.setStreamNamespace(it) }
        meta?.let { meta ->
            recordBuilder.setMeta(
                AirbyteRecordMessageMetaOuterClass.AirbyteRecordMessageMeta.newBuilder()
                    .addAllChanges(
                        meta.changes.map {
                            AirbyteRecordMessageMetaOuterClass.AirbyteRecordMessageMetaChange
                                .newBuilder()
                                .setField(it.field)
                                .setChange(
                                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType
                                        .valueOf(it.change.name)
                                )
                                .setReason(
                                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                                        .valueOf(it.reason.name)
                                )
                                .build()
                        }
                    )
            )
        }
        val orderedSchema = stream.airbyteValueProxyFieldAccessors
        data as ObjectValue
        orderedSchema.forEach { field ->
            val protoField =
                if (field.type is UnknownType || field.type is UnionType) {
                    data.values[field.name]?.let {
                        AirbyteValueProtobuf.newBuilder()
                            .setJson(ByteString.copyFrom(it.toJson().serializeToJsonBytes()))
                            .build()
                    }
                        ?: toProtobuf(NullValue, field.type)
                } else {
                    toProtobuf(data.values[field.name] ?: NullValue, field.type)
                }
            recordBuilder.addData(protoField)
        }

        return AirbyteMessageProtobuf.newBuilder().setRecord(recordBuilder).build()
    }

    private fun toProtobuf(value: AirbyteValue, type: AirbyteType): AirbyteValueProtobuf =
        AirbyteValueToProtobuf().toProtobuf(value, type)

    override fun asProtocolMessage(): AirbyteMessage =
        AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(
                AirbyteRecordMessage()
                    .withStream(stream.unmappedName)
                    .withNamespace(stream.unmappedNamespace)
                    .withEmittedAt(emittedAtMs)
                    .withData(data.toJson())
                    .also {
                        if (meta != null) {
                            it.withMeta(meta.asProtocolObject())
                        }
                        if (fileReference != null) {
                            it.withFileReference(fileReference)
                        }
                        if (checkpointId != null) {
                            it.additionalProperties[CHECKPOINT_ID_NAME] = checkpointId.value
                        }
                    }
            )
}

data class InputFile(
    val file: DestinationFile,
) : InputMessage {
    constructor(
        stream: DestinationStream,
        emittedAtMs: Long,
        fileMessage: DestinationFile.AirbyteRecordMessageFile,
    ) : this(
        DestinationFile(
            stream,
            emittedAtMs,
            fileMessage,
        )
    )
    override fun asProtocolMessage(): AirbyteMessage = file.asProtocolMessage()
}

sealed interface InputCheckpoint : InputMessage

data class InputStreamCheckpoint(val checkpoint: StreamCheckpoint) : InputCheckpoint {
    constructor(
        streamNamespace: String?,
        streamName: String,
        blob: String,
        sourceRecordCount: Long,
        destinationRecordCount: Long? = null,
        checkpointKey: CheckpointKey? = null,
    ) : this(
        StreamCheckpoint(
            Checkpoint(
                stream = DestinationStream.Descriptor(streamNamespace, streamName),
                state = blob.deserializeToNode()
            ),
            Stats(sourceRecordCount),
            destinationRecordCount?.let { Stats(it) },
            emptyMap(),
            0L,
            checkpointKey,
        )
    )
    override fun asProtocolMessage(): AirbyteMessage = checkpoint.asProtocolMessage()
}

data class InputGlobalCheckpoint(
    val sharedState: JsonNode?,
    val checkpointKey: CheckpointKey? = null,
    val streamStates: List<Checkpoint> = emptyList(),
) : InputCheckpoint {
    override fun asProtocolMessage(): AirbyteMessage =
        AirbyteMessage()
            .withType(AirbyteMessage.Type.STATE)
            .withState(
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                    .withGlobal(
                        AirbyteGlobalState()
                            .withSharedState(sharedState)
                            .withStreamStates(streamStates.map { it.asProtocolObject() })
                    )
                    .also {
                        if (checkpointKey != null) {
                            it.additionalProperties["partition_id"] =
                                checkpointKey.checkpointId.value
                            it.additionalProperties["id"] = checkpointKey.checkpointIndex.value
                        }
                    }
            )
}

data class InputStreamComplete(val streamComplete: DestinationRecordStreamComplete) : InputMessage {
    override fun asProtocolMessage(): AirbyteMessage = streamComplete.asProtocolMessage()
}

data class InputMessageOther(val airbyteMessage: AirbyteMessage) : InputMessage {
    override fun asProtocolMessage(): AirbyteMessage = airbyteMessage
}
