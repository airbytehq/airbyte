/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointIndex
import io.airbyte.cdk.load.state.CheckpointKey
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.UUIDGenerator
import io.airbyte.protocol.models.v0.*
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.micronaut.context.annotation.Value
import jakarta.inject.Named
import jakarta.inject.Singleton

@Singleton
class DestinationMessageFactory(
    private val catalog: DestinationCatalog,
    @Value("\${airbyte.destination.core.file-transfer.enabled}")
    private val fileTransferEnabled: Boolean,
    @Named("requireCheckpointIdOnRecordAndKeyOnState")
    private val requireCheckpointIdOnRecordAndKeyOnState: Boolean = false,
    private val namespaceMapper: NamespaceMapper,
    private val uuidGenerator: UUIDGenerator,
) {

    fun fromAirbyteProtocolMessage(
        message: AirbyteMessage,
        serializedSizeBytes: Long
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
                            "Unexpected value for $name: $it (${it::class.qualifiedName})",
                        )
                }
            }
        }

        return when (message.type) {
            AirbyteMessage.Type.RECORD -> {
                val descriptor =
                    namespaceMapper.map(
                        namespace = message.record.namespace,
                        name = message.record.stream
                    )
                val stream = catalog.getStream(descriptor)
                if (fileTransferEnabled) {
                    try {
                        @Suppress("UNCHECKED_CAST")
                        val fileMessage =
                            message.record.additionalProperties["file"] as Map<String, Any>

                        DestinationFile(
                            stream = stream,
                            emittedAtMs = message.record.emittedAt,
                            fileMessage =
                                DestinationFile.AirbyteRecordMessageFile(
                                    fileUrl = fileMessage["file_url"] as String?,
                                    bytes = toLong(fileMessage["bytes"], "message.record.bytes"),
                                    fileRelativePath = fileMessage["file_relative_path"] as String?,
                                    modified =
                                        toLong(fileMessage["modified"], "message.record.modified"),
                                    sourceFileUrl = fileMessage["source_file_url"] as String?,
                                ),
                        )
                    } catch (e: Exception) {
                        throw IllegalArgumentException(
                            "Failed to construct file message: ${e.message}",
                        )
                    }
                } else {
                    // In socket mode, multiple sockets can run in parallel, which means that we
                    // depend on upstream to associate each record with the appropriate state
                    // message for us.
                    val checkpointId =
                        if (requireCheckpointIdOnRecordAndKeyOnState) {
                            val idSource =
                                (message.record.additionalProperties[Meta.CHECKPOINT_ID_NAME]
                                    ?: throw IllegalStateException(
                                        "Expected `partition_id` on record"
                                    ))
                            CheckpointId(idSource as String)
                        } else {
                            null
                        }
                    DestinationRecord(
                        stream = stream,
                        message = DestinationRecordJsonSource(message),
                        serializedSizeBytes = serializedSizeBytes,
                        checkpointId = checkpointId,
                        airbyteRawId = uuidGenerator.v7(),
                    )
                }
            }
            AirbyteMessage.Type.TRACE -> {
                val status = message.trace.streamStatus
                if (
                    message.trace.type == null ||
                        message.trace.type == AirbyteTraceMessage.Type.STREAM_STATUS
                ) {
                    val descriptor =
                        namespaceMapper.map(
                            namespace = status.streamDescriptor.namespace,
                            name = status.streamDescriptor.name,
                        )
                    val stream = catalog.getStream(descriptor)
                    when (status.status) {
                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE ->
                            if (fileTransferEnabled) {
                                DestinationFileStreamComplete(
                                    stream,
                                    message.trace.emittedAt?.toLong() ?: 0L,
                                )
                            } else {
                                DestinationRecordStreamComplete(
                                    stream,
                                    message.trace.emittedAt?.toLong() ?: 0L,
                                )
                            }
                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.INCOMPLETE ->
                            throw ConfigErrorException(
                                "Received stream status INCOMPLETE message. This indicates a bug in the Airbyte platform. Original message: $message"
                            )
                        else -> Undefined
                    }
                } else {
                    // Ignore other TRACE message types
                    Ignored
                }
            }
            AirbyteMessage.Type.STATE -> {
                when (message.state.type) {
                    AirbyteStateMessage.AirbyteStateType.STREAM -> {
                        val additionalProperties = message.state.additionalProperties
                        StreamCheckpoint(
                            checkpoint = fromAirbyteStreamState(message.state.stream),
                            sourceStats =
                                message.state.sourceStats?.recordCount?.let {
                                    CheckpointMessage.Stats(recordCount = it.toLong())
                                },
                            additionalProperties = additionalProperties,
                            serializedSizeBytes = serializedSizeBytes,
                            checkpointKey = keyFromAdditionalPropertiesMaybe(additionalProperties),
                        )
                    }
                    null,
                    AirbyteStateMessage.AirbyteStateType.GLOBAL -> {
                        val additionalProperties = message.state.additionalProperties
                        GlobalCheckpoint(
                            sourceStats =
                                message.state.sourceStats?.recordCount?.let {
                                    CheckpointMessage.Stats(recordCount = it.toLong())
                                },
                            state = message.state.global.sharedState,
                            checkpoints =
                                message.state.global.streamStates.map {
                                    fromAirbyteStreamState(it)
                                },
                            additionalProperties = message.state.additionalProperties,
                            originalTypeField = message.state.type,
                            serializedSizeBytes = serializedSizeBytes,
                            checkpointKey = keyFromAdditionalPropertiesMaybe(additionalProperties)
                        )
                    }
                    else -> // TODO: Do we still need to handle LEGACY?
                    Undefined
                }
            }
            else -> Undefined
        }
    }

    private fun keyFromAdditionalPropertiesMaybe(
        additionalProperties: Map<String, Any>,
    ): CheckpointKey? {
        val id = additionalProperties[Meta.CHECKPOINT_ID_NAME]?.let { CheckpointId(it as String) }
        val index =
            additionalProperties[Meta.CHECKPOINT_INDEX_NAME]?.let {
                CheckpointIndex((it as Int).toInt())
            }
        return if (id != null && index != null) {
            CheckpointKey(index, id)
        } else {
            check(!requireCheckpointIdOnRecordAndKeyOnState) {
                "Expected `${Meta.CHECKPOINT_ID_NAME}` and `${Meta.CHECKPOINT_INDEX_NAME}` in additional properties (got ${additionalProperties.keys})"
            }
            null
        }
    }

    private fun fromAirbyteStreamState(
        streamState: AirbyteStreamState
    ): CheckpointMessage.Checkpoint {
        val descriptor =
            namespaceMapper.map(
                namespace = streamState.streamDescriptor.namespace,
                name = streamState.streamDescriptor.name
            )
        return CheckpointMessage.Checkpoint(
            stream = DestinationStream.Descriptor(descriptor.namespace, descriptor.name),
            state = runCatching { streamState.streamState }.getOrNull(),
        )
    }

    fun fromAirbyteProtobufMessage(
        message: AirbyteMessageProtobuf,
        serializedSizeBytes: Long,
    ): DestinationMessage {
        // Control messages will be sent as serialized json.
        return if (message.hasAirbyteProtocolMessage()) {
            val airbyteMessage =
                Jsons.readValue(message.airbyteProtocolMessage, AirbyteMessage::class.java)
            fromAirbyteProtocolMessage(airbyteMessage, serializedSizeBytes)
        } else if (message.hasRecord()) {
            val descriptor =
                namespaceMapper.map(
                    namespace =
                        if (message.record.hasStreamNamespace()) {
                            message.record.streamNamespace // defaults to "", not null
                        } else {
                            null
                        },
                    name = message.record.streamName
                )
            val stream = catalog.getStream(descriptor)
            DestinationRecord(
                stream = stream,
                message = DestinationRecordProtobufSource(message),
                serializedSizeBytes = serializedSizeBytes,
                checkpointId = CheckpointId(message.record.partitionId),
                airbyteRawId = uuidGenerator.v7(),
            )
        } else if (message.hasProbe()) {
            ProbeMessage
        } else {
            throw IllegalArgumentException("AirbyteMessage must contain a payload.")
        }
    }
}

data object ProbeMessage : DestinationMessage {
    override fun asProtocolMessage(): AirbyteMessage {
        throw UnsupportedOperationException(
            "ProbeMessage cannot be converted to AirbyteMessage. " +
                "It is only used by the source to verify that the data channel is open."
        )
    }
}
