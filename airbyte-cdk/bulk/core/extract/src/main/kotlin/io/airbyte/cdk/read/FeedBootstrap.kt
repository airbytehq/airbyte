/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.MetaFieldDecorator
import io.airbyte.cdk.output.DataChannelFormat
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.output.StandardOutputConsumer
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.output.sockets.ProtoEncoder
import io.airbyte.cdk.output.sockets.SocketJsonOutputConsumer
import io.airbyte.cdk.output.sockets.SocketProtobufOutputConsumer
import io.airbyte.cdk.output.sockets.nullProtoEncoder
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.output.sockets.toProtobuf
import io.airbyte.cdk.output.sockets.toProtobufEncoder
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessageMetaOuterClass
import java.time.Clock
import java.time.ZoneOffset

/**
 * [FeedBootstrap] is the input to a [PartitionsCreatorFactory].
 *
 * This object conveniently packages the [StateManager] singleton with the [feed] for which the
 * [PartitionsCreatorFactory] is to operate on, eventually causing the emission of Airbyte RECORD
 * messages for the [Stream]s in the [feed]. For this purpose, [FeedBootstrap] provides
 * [StreamRecordConsumer] instances which essentially provide a layer of caching over
 * [OutputConsumer], leveraging the fact that all records for a given stream share the same schema.
 */
sealed class FeedBootstrap<T : Feed>(
    /** The [OutputConsumer] instance to which [StreamRecordConsumer] will delegate to. */
    val outputConsumer: StandardOutputConsumer,
    /**
     * The [MetaFieldDecorator] instance which [StreamRecordConsumer] will use to decorate records.
     */
    val metaFieldDecorator: MetaFieldDecorator,
    /** [StateManager] singleton which is encapsulated by this [FeedBootstrap]. */
    private val stateManager: StateManager,
    /** [Feed] to emit records for. */
    val feed: T,
    val dataChannelFormat: DataChannelFormat,
    val dataChannelMedium: DataChannelMedium,
    val bufferByteSizeThresholdForFlush: Int,
    val clock: Clock,
) {

    /** Delegates to [StateManager.feeds]. */
    val feeds: List<Feed>
        get() = stateManager.feeds

    /** Deletages to [StateManager] to return the current state value for any [Feed]. */
    fun currentState(feed: Feed): OpaqueStateValue? = stateManager.scoped(feed).current()

    /** Convenience getter for the current state value for this [feed]. */
    val currentState: OpaqueStateValue?
        get() = currentState(feed)

    /** Resets the state value of this feed and the streams in it to zero. */
    fun resetAll() {
        stateManager.scoped(feed).reset()
        for (stream in feed.streams) {
            stateManager.scoped(stream).reset()
        }
    }

    /** A map of all [StreamRecordConsumer] for this [feed]. */
    fun streamRecordConsumers(): Map<StreamIdentifier, StreamRecordConsumer> =
        feed.streams.associate { stream: Stream ->
            stream.id to EfficientStreamRecordConsumer(stream)
        }

    fun streamJsonSocketRecordConsumers(
        socketJsonOutputConsumer: SocketJsonOutputConsumer
    ): Map<StreamIdentifier, JsonSocketEfficientStreamRecordConsumer> =
        feed.streams.associate { stream: Stream ->
            stream.id to JsonSocketEfficientStreamRecordConsumer(stream, socketJsonOutputConsumer)
        }

    fun streamProtoRecordConsumers(
        socketProtoOutputConsumer: SocketProtobufOutputConsumer,
    ): Map<StreamIdentifier, ProtoEfficientStreamRecordConsumer> =
        feed.streams.associate { stream: Stream ->
            stream.id to ProtoEfficientStreamRecordConsumer(stream, socketProtoOutputConsumer)
        }

    /**
     * Efficient implementation of [StreamRecordConsumer].
     *
     * It's efficient because it re-uses the same Airbyte protocol message instance from one record
     * to the next. Not doing this generates a lot of garbage and the increased GC activity has a
     * measurable impact on performance.
     */
    open inner class EfficientStreamRecordConsumer(
        override val stream: Stream,
        val outputDataChannel: OutputConsumer = outputConsumer
    ) : StreamRecordConsumer {

        override fun close() {
            outputDataChannel.close()
        }

        override fun accept(
            recordData: NativeRecordPayload,
            changes: Map<Field, FieldValueChange>?
        ) {
            if (changes.isNullOrEmpty()) {
                acceptWithoutChanges(recordData.toJson())
            } else {
                val protocolChanges: List<AirbyteRecordMessageMetaChange> =
                    changes.map { (field: Field, fieldValueChange: FieldValueChange) ->
                        AirbyteRecordMessageMetaChange()
                            .withField(field.id)
                            .withChange(fieldValueChange.protocolChange())
                            .withReason(fieldValueChange.protocolReason())
                    }
                acceptWithChanges(recordData.toJson(), protocolChanges)
            }
        }

        private fun acceptWithoutChanges(recordData: ObjectNode) {
            synchronized(this) {
                for ((fieldName, defaultValue) in defaultRecordData.fields()) {
                    reusedRecordData.set<JsonNode>(fieldName, recordData[fieldName] ?: defaultValue)
                }
                outputDataChannel.accept(reusedMessageWithoutChanges)
            }
        }

        private fun acceptWithChanges(
            recordData: ObjectNode,
            changes: List<AirbyteRecordMessageMetaChange>
        ) {
            synchronized(this) {
                for ((fieldName, defaultValue) in defaultRecordData.fields()) {
                    reusedRecordData.set<JsonNode>(fieldName, recordData[fieldName] ?: defaultValue)
                }
                reusedRecordMeta.changes = changes
                outputDataChannel.accept(reusedMessageWithChanges)
            }
        }

        private val precedingGlobalFeed: Global? =
            stateManager.feeds.filterIsInstance<Global>().firstOrNull {
                it.streams.contains(stream)
            }

        // Ideally we should check if sync is trigger-based CDC by checking source connector
        // configuration. But we don't have that information here. So this is just a hacky solution
        private val isTriggerBasedCdc: Boolean =
            precedingGlobalFeed == null &&
                metaFieldDecorator.globalCursor != null &&
                stream.schema.none { it.id == metaFieldDecorator.globalCursor?.id } &&
                stream.configuredCursor?.id == metaFieldDecorator.globalCursor?.id &&
                stream.configuredSyncMode == ConfiguredSyncMode.INCREMENTAL

        private val defaultRecordData: ObjectNode =
            Jsons.objectNode().also { recordData: ObjectNode ->
                stream.schema.forEach { recordData.putNull(it.id) }
                if (feed is Stream && precedingGlobalFeed != null || isTriggerBasedCdc) {
                    metaFieldDecorator.decorateRecordData(
                        timestamp = outputDataChannel.recordEmittedAt.atOffset(ZoneOffset.UTC),
                        globalStateValue =
                            if (precedingGlobalFeed != null)
                                stateManager.scoped(precedingGlobalFeed).current()
                            else null,
                        stream,
                        recordData,
                    )
                }
            }

        private val reusedRecordData: ObjectNode = defaultRecordData.deepCopy()

        private val reusedMessageWithoutChanges: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(stream.name)
                        .withNamespace(stream.namespace)
                        .withEmittedAt(outputDataChannel.recordEmittedAt.toEpochMilli())
                        .withData(reusedRecordData)
                )

        private val reusedRecordMeta = AirbyteRecordMessageMeta()

        private val reusedMessageWithChanges: AirbyteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(stream.name)
                        .withNamespace(stream.namespace)
                        .withEmittedAt(outputDataChannel.recordEmittedAt.toEpochMilli())
                        .withData(reusedRecordData)
                        .withMeta(reusedRecordMeta)
                )
    }

    // JsonSocketEfficientStreamRecordConsumer is an EfficientStreamRecordConsumer created with a
    // socket data channel resource
    inner class JsonSocketEfficientStreamRecordConsumer(stream: Stream, outputer: OutputConsumer) :
        EfficientStreamRecordConsumer(stream, outputer)

    // ProtoEfficientStreamRecordConsumer is an optimizing record consumer emitting protobuf
    // messages to the underlying output consumer
    inner class ProtoEfficientStreamRecordConsumer(
        override val stream: Stream,
        private val socketProtobufOutputConsumer: SocketProtobufOutputConsumer,
    ) : StreamRecordConsumer {
        override fun close() {
            socketProtobufOutputConsumer.close()
        }

        val valueVBuilder = AirbyteValueProtobuf.newBuilder()!!
        override fun accept(
            recordData: NativeRecordPayload,
            changes: Map<Field, FieldValueChange>?
        ) {
            if (changes.isNullOrEmpty()) {
                acceptWithoutChanges(
                    recordData.toProtobuf(stream.schema, defaultRecordData, valueVBuilder)
                )
            } else {
                val rm = AirbyteRecordMessageMetaOuterClass.AirbyteRecordMessageMeta.newBuilder()
                val c =
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordMessageMetaChange.newBuilder()
                changes.forEach { (field: Field, fieldValueChange: FieldValueChange) ->
                    c.clear()
                        .setField(field.id)
                        .setChange(fieldValueChange.protobufChange())
                        .setReason(fieldValueChange.protobufReason())
                    rm.addChanges(c)
                }
                acceptWithChanges(
                    recordData.toProtobuf(stream.schema, defaultRecordData, valueVBuilder),
                    rm
                )
            }
        }

        private fun acceptWithoutChanges(
            recordData: AirbyteRecordMessageProtobuf.Builder,
        ) {
            synchronized(this) {
                socketProtobufOutputConsumer.accept(
                    reusedMessageWithoutChanges.setRecord(recordData).build()
                )
            }
        }

        private fun acceptWithChanges(
            recordData: AirbyteRecordMessageProtobuf.Builder,
            changes: AirbyteRecordMessageMetaOuterClass.AirbyteRecordMessageMeta.Builder
        ) {
            synchronized(this) {
                recordData.setMeta(changes)
                socketProtobufOutputConsumer.accept(
                    reusedMessageWithoutChanges.setRecord(recordData).build()
                )
            }
        }

        private val precedingGlobalFeed: Global? =
            stateManager.feeds.filterIsInstance<Global>().firstOrNull {
                it.streams.contains(stream)
            }

        // Ideally we should check if sync is trigger-based CDC by checking source connector
        // configuration. But we don't have that information here. So this is just a hacky solution
        private val isTriggerBasedCdc: Boolean =
            precedingGlobalFeed == null &&
                metaFieldDecorator.globalCursor != null &&
                stream.schema.none { it.id == metaFieldDecorator.globalCursor?.id } &&
                stream.configuredCursor?.id == metaFieldDecorator.globalCursor?.id &&
                stream.configuredSyncMode == ConfiguredSyncMode.INCREMENTAL

        private val defaultRecordData: AirbyteRecordMessageProtobuf.Builder =
            AirbyteRecordMessageProtobuf.newBuilder()
                .setStreamName(stream.name)
                .setStreamNamespace(stream.namespace)
                .setEmittedAtMs(socketProtobufOutputConsumer.recordEmittedAt.toEpochMilli())
                .also { builder ->
                    socketProtobufOutputConsumer.additionalProperties["partition_id"]?.let {
                        builder.setPartitionId(it)
                    }
                }
                .also { builder ->
                    val decoratingFields: NativeRecordPayload = mutableMapOf()
                    if (feed is Stream && precedingGlobalFeed != null || isTriggerBasedCdc) {
                        metaFieldDecorator.decorateRecordData(
                            timestamp =
                                socketProtobufOutputConsumer.recordEmittedAt.atOffset(
                                    ZoneOffset.UTC
                                ),
                            globalStateValue =
                                if (precedingGlobalFeed != null)
                                    stateManager.scoped(precedingGlobalFeed).current()
                                else null,
                            stream,
                            decoratingFields
                        )
                    }

                    // Unlike STDIO mode, in socket mode we always include all scehma fields
                    // Including decorating field even when it has NULL value.
                    // This is necessary beacuse in PROTOBUF mode we don't have field names so
                    // the sorted order of fields is used to determine the field position on the
                    // other side.
                    stream.schema
                        .sortedBy { it.id }
                        .forEach { field ->
                            builder.addData(
                                when {
                                    decoratingFields.keys.contains(field.id) -> {
                                        @Suppress("UNCHECKED_CAST")
                                        (decoratingFields[field.id]!!
                                                .jsonEncoder
                                                .toProtobufEncoder() as ProtoEncoder<Any>)
                                            .encode(
                                                valueVBuilder.clear(),
                                                decoratingFields[field.id]!!.fieldValue!!
                                            )
                                    }
                                    else -> nullProtoEncoder.encode(valueVBuilder.clear(), true)
                                }
                            )
                        }
                }

        val reusedMessageWithoutChanges: AirbyteMessageProtobuf.Builder =
            AirbyteMessageProtobuf.newBuilder()
    }

    companion object {

        @JvmStatic
        private fun FieldValueChange.protobufChange():
            AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType =
            when (this) {
                FieldValueChange.RECORD_SIZE_LIMITATION_ERASURE ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType.NULLED
                FieldValueChange.RECORD_SIZE_LIMITATION_TRUNCATION ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType.TRUNCATED
                FieldValueChange.FIELD_SIZE_LIMITATION_ERASURE ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType.NULLED
                FieldValueChange.FIELD_SIZE_LIMITATION_TRUNCATION ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType.TRUNCATED
                FieldValueChange.DESERIALIZATION_FAILURE_TOTAL ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType.NULLED
                FieldValueChange.DESERIALIZATION_FAILURE_PARTIAL ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType.TRUNCATED
                FieldValueChange.RETRIEVAL_FAILURE_TOTAL ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType.NULLED
                FieldValueChange.RETRIEVAL_FAILURE_PARTIAL ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeType.TRUNCATED
            }

        @JvmStatic
        private fun FieldValueChange.protobufReason():
            AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType =
            when (this) {
                FieldValueChange.RECORD_SIZE_LIMITATION_ERASURE ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                        .SOURCE_RECORD_SIZE_LIMITATION
                FieldValueChange.RECORD_SIZE_LIMITATION_TRUNCATION ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                        .SOURCE_RECORD_SIZE_LIMITATION
                FieldValueChange.FIELD_SIZE_LIMITATION_ERASURE ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                        .SOURCE_RECORD_SIZE_LIMITATION
                FieldValueChange.FIELD_SIZE_LIMITATION_TRUNCATION ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                        .SOURCE_RECORD_SIZE_LIMITATION
                FieldValueChange.DESERIALIZATION_FAILURE_TOTAL ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                        .SOURCE_SERIALIZATION_ERROR
                FieldValueChange.DESERIALIZATION_FAILURE_PARTIAL ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                        .SOURCE_SERIALIZATION_ERROR
                FieldValueChange.RETRIEVAL_FAILURE_TOTAL ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                        .SOURCE_RETRIEVAL_ERROR
                FieldValueChange.RETRIEVAL_FAILURE_PARTIAL ->
                    AirbyteRecordMessageMetaOuterClass.AirbyteRecordChangeReasonType
                        .SOURCE_RETRIEVAL_ERROR
            }

        @JvmStatic
        private fun FieldValueChange.protocolChange(): AirbyteRecordMessageMetaChange.Change =
            when (this) {
                FieldValueChange.RECORD_SIZE_LIMITATION_ERASURE ->
                    AirbyteRecordMessageMetaChange.Change.NULLED
                FieldValueChange.RECORD_SIZE_LIMITATION_TRUNCATION ->
                    AirbyteRecordMessageMetaChange.Change.TRUNCATED
                FieldValueChange.FIELD_SIZE_LIMITATION_ERASURE ->
                    AirbyteRecordMessageMetaChange.Change.NULLED
                FieldValueChange.FIELD_SIZE_LIMITATION_TRUNCATION ->
                    AirbyteRecordMessageMetaChange.Change.TRUNCATED
                FieldValueChange.DESERIALIZATION_FAILURE_TOTAL ->
                    AirbyteRecordMessageMetaChange.Change.NULLED
                FieldValueChange.DESERIALIZATION_FAILURE_PARTIAL ->
                    AirbyteRecordMessageMetaChange.Change.TRUNCATED
                FieldValueChange.RETRIEVAL_FAILURE_TOTAL ->
                    AirbyteRecordMessageMetaChange.Change.NULLED
                FieldValueChange.RETRIEVAL_FAILURE_PARTIAL ->
                    AirbyteRecordMessageMetaChange.Change.TRUNCATED
            }

        @JvmStatic
        private fun FieldValueChange.protocolReason(): AirbyteRecordMessageMetaChange.Reason =
            when (this) {
                FieldValueChange.RECORD_SIZE_LIMITATION_ERASURE ->
                    AirbyteRecordMessageMetaChange.Reason.SOURCE_RECORD_SIZE_LIMITATION
                FieldValueChange.RECORD_SIZE_LIMITATION_TRUNCATION ->
                    AirbyteRecordMessageMetaChange.Reason.SOURCE_RECORD_SIZE_LIMITATION
                FieldValueChange.FIELD_SIZE_LIMITATION_ERASURE ->
                    AirbyteRecordMessageMetaChange.Reason.SOURCE_FIELD_SIZE_LIMITATION
                FieldValueChange.FIELD_SIZE_LIMITATION_TRUNCATION ->
                    AirbyteRecordMessageMetaChange.Reason.SOURCE_FIELD_SIZE_LIMITATION
                FieldValueChange.DESERIALIZATION_FAILURE_TOTAL ->
                    AirbyteRecordMessageMetaChange.Reason.SOURCE_SERIALIZATION_ERROR
                FieldValueChange.DESERIALIZATION_FAILURE_PARTIAL ->
                    AirbyteRecordMessageMetaChange.Reason.SOURCE_SERIALIZATION_ERROR
                FieldValueChange.RETRIEVAL_FAILURE_TOTAL ->
                    AirbyteRecordMessageMetaChange.Reason.SOURCE_RETRIEVAL_ERROR
                FieldValueChange.RETRIEVAL_FAILURE_PARTIAL ->
                    AirbyteRecordMessageMetaChange.Reason.SOURCE_RETRIEVAL_ERROR
            }

        /** [FeedBootstrap] factory method. */
        fun create(
            outputConsumer: StandardOutputConsumer,
            metaFieldDecorator: MetaFieldDecorator,
            stateManager: StateManager,
            feed: Feed,
            dataChannelFormat: DataChannelFormat,
            dataChannelMedium: DataChannelMedium,
            bufferByteSizeThresholdForFlush: Int,
            clock: Clock,
        ): FeedBootstrap<*> =
            when (feed) {
                is Global ->
                    GlobalFeedBootstrap(
                        outputConsumer,
                        metaFieldDecorator,
                        stateManager,
                        feed,
                        dataChannelFormat,
                        dataChannelMedium,
                        bufferByteSizeThresholdForFlush,
                        clock
                    )
                is Stream ->
                    StreamFeedBootstrap(
                        outputConsumer,
                        metaFieldDecorator,
                        stateManager,
                        feed,
                        dataChannelFormat,
                        dataChannelMedium,
                        bufferByteSizeThresholdForFlush,
                        clock
                    )
            }
    }
}

/**
 * Emits an Airbyte RECORD message for the [Stream] associated with this instance.
 *
 * The purpose of this interface is twofold:
 * 1. to encapsulate a performance-minded implementation behind a simple abstraction;
 * 2. to decorate the RECORD messages with
 * ```
 *    a) meta-fields in the record data, and
 *    b) field value changes and the motivating reason for these in the record metadata.
 * ```
 */
interface StreamRecordConsumer {

    val stream: Stream

    fun accept(recordData: NativeRecordPayload, changes: Map<Field, FieldValueChange>?)
    fun close()
}

/**
 * This enum maps to [AirbyteRecordMessageMetaChange.Change] and
 * [AirbyteRecordMessageMetaChange.Reason] enum value pairs.
 */
enum class FieldValueChange {
    RECORD_SIZE_LIMITATION_ERASURE,
    RECORD_SIZE_LIMITATION_TRUNCATION,
    FIELD_SIZE_LIMITATION_ERASURE,
    FIELD_SIZE_LIMITATION_TRUNCATION,
    DESERIALIZATION_FAILURE_TOTAL,
    DESERIALIZATION_FAILURE_PARTIAL,
    RETRIEVAL_FAILURE_TOTAL,
    RETRIEVAL_FAILURE_PARTIAL,
}

/** [FeedBootstrap] implementation for [Global] feeds. */
class GlobalFeedBootstrap(
    outputConsumer: StandardOutputConsumer,
    metaFieldDecorator: MetaFieldDecorator,
    stateManager: StateManager,
    global: Global,
    dataChannelFormat: DataChannelFormat,
    dataChannelMedium: DataChannelMedium,
    bufferByteSizeThresholdForFlush: Int,
    clock: Clock,
) :
    FeedBootstrap<Global>(
        outputConsumer,
        metaFieldDecorator,
        stateManager,
        global,
        dataChannelFormat,
        dataChannelMedium,
        bufferByteSizeThresholdForFlush,
        clock
    )

/** [FeedBootstrap] implementation for [Stream] feeds. */
class StreamFeedBootstrap(
    outputConsumer: StandardOutputConsumer,
    metaFieldDecorator: MetaFieldDecorator,
    stateManager: StateManager,
    stream: Stream,
    dataChannelFormat: DataChannelFormat,
    dataChannelMedium: DataChannelMedium,
    bufferByteSizeThresholdForFlush: Int,
    clock: Clock,
) :
    FeedBootstrap<Stream>(
        outputConsumer,
        metaFieldDecorator,
        stateManager,
        stream,
        dataChannelFormat,
        dataChannelMedium,
        bufferByteSizeThresholdForFlush,
        clock
    )
