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
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.output.SimpleOutputConsumer
import io.airbyte.cdk.output.sockets.SocketJsonOutputConsumer
import io.airbyte.cdk.output.sockets.BoostedOutputConsumerFactory
import io.airbyte.cdk.output.sockets.InternalRow
import io.airbyte.cdk.output.sockets.NullProtoEncoder
import io.airbyte.cdk.output.sockets.SocketProtobufOutputConsumer
import io.airbyte.cdk.output.sockets.toJson
import io.airbyte.cdk.output.sockets.toProto
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.*
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
    val outputConsumer: SimpleOutputConsumer,
    /**
     * The [MetaFieldDecorator] instance which [StreamRecordConsumer] will use to decorate records.
     */
    val metaFieldDecorator: MetaFieldDecorator,
    /** [StateManager] singleton which is encapsulated by this [FeedBootstrap]. */
    private val stateManager: StateManager,
    /** [Feed] to emit records for. */
    val feed: T,
    val boostedOutputConsumerFactory: BoostedOutputConsumerFactory?,
    val outputFormat: String,
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
    fun streamRecordConsumers(socketJsonOutputConsumer: SocketJsonOutputConsumer? = null): Map<StreamIdentifier, StreamRecordConsumer> =
        feed.streams.associate { stream: Stream ->
            stream.id to EfficientStreamRecordConsumer(stream, socketJsonOutputConsumer)
        }

    /**
     * Efficient implementation of [StreamRecordConsumer].
     *
     * It's efficient because it re-uses the same Airbyte protocol message instance from one record
     * to the next. Not doing this generates a lot of garbage and the increased GC activity has a
     * measurable impact on performance.
     */
    inner class EfficientStreamRecordConsumer(override val stream: Stream, socketJsonOutputConsumer: SocketJsonOutputConsumer?) :
        StreamRecordConsumer {
        val outputer: OutputConsumer = socketJsonOutputConsumer ?: outputConsumer

        override fun close() {
            outputer.close()
        }

        override fun accept(recordData: InternalRow, changes: Map<Field, FieldValueChange>?) {
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
                outputer.accept(reusedMessageWithoutChanges)
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
                outputer.accept(reusedMessageWithChanges)
            }
        }

        private val precedingGlobalFeed: Global? =
            stateManager.feeds
                .filterIsInstance<Global>()
                .filter { it.streams.contains(stream) }
                .firstOrNull()

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
                        timestamp = outputer.recordEmittedAt.atOffset(ZoneOffset.UTC),
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
                        .withEmittedAt(outputer.recordEmittedAt.toEpochMilli())
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
                        .withEmittedAt(outputer.recordEmittedAt.toEpochMilli())
                        .withData(reusedRecordData)
                        .withMeta(reusedRecordMeta)
                )
    }

    inner class ProtoEfficientStreamRecordConsumer(override val stream: Stream, boostedOutputConsumer: SocketProtobufOutputConsumer, val partitionId: String?) :
        StreamRecordConsumer {
        val outputer: SocketProtobufOutputConsumer = boostedOutputConsumer
        override fun close() {
            outputer.close()
        }

        val valueVBuilder = AirbyteValueProtobuf.newBuilder()!!
        override fun accept(recordData: InternalRow, changes: Map<Field, FieldValueChange>?) {
            if (changes.isNullOrEmpty()) {
                /*var b = AirbyteRecordMessageProtobuf.newBuilder()
                    .setStreamName(stream.name)
                    .setStreamNamespace(stream.namespace)
                    .setEmittedAtMs(outputer.recordEmittedAt.toEpochMilli())*/
                //                partitionId?.let { b.setPartitionId(it) }

                var b = defaultRecordData
                val p = recordData.toProto(b, valueVBuilder)

                acceptWithoutChanges(/*recordData.toProto(reusedRecordMessageWithoutChanges)*//*firstData*/p)
            } /*else {
                val protocolChanges: List<AirbyteRecordMessageMetaChange> =
                    changes.map { (field: Field, fieldValueChange: FieldValueChange) ->
                        AirbyteRecordMessageMetaChange()
                            .withField(field.id)
                            .withChange(fieldValueChange.protocolChange())
                            .withReason(fieldValueChange.protocolReason())
                    }
//                acceptWithChanges(recordData.toJson(), protocolChanges) // TEMP
            }*/
        }

        private fun acceptWithoutChanges(recordData: AirbyteRecordMessageProtobuf.Builder,) {
            synchronized(this) {
/*
                for ((fieldName, defaultValue) in defaultRecordData.fields()) {
                    reusedRecordData.set<JsonNode>(fieldName, recordData[fieldName] ?: defaultValue)
                }
*/
                outputer.accept(
                    reusedMessageWithoutChanges
                        .setRecord(recordData)
                        .build() /*firstMessage*/)
            }
        }

/*
        private fun acceptWithChanges(
            recordData: AirbyteRecordMessageProtobuf.Builder,
            changes: List<AirbyteRecordMessageMetaChange>
        ) {
            synchronized(this) {
                for ((fieldName, defaultValue) in defaultRecordData.fields()) {
                    reusedRecordData.set<JsonNode>(fieldName, recordData[fieldName] ?: defaultValue)
                }
                reusedRecordMeta.changes = changes
                outputer.accept(reusedMessageWithChanges)
            }
        }
*/

        private val precedingGlobalFeed: Global? =
            stateManager.feeds
                .filterIsInstance<Global>()
                .filter { it.streams.contains(stream) }
                .firstOrNull()

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
                .setEmittedAtMs(outputer.recordEmittedAt.toEpochMilli())
                .also { builder -> partitionId?.let { builder.setPartitionId(it) } }
                .also { builder ->
                    stream.schema.sortedBy { it.id }.forEach {
                        builder.addData(
                            NullProtoEncoder.encode(valueVBuilder, true)
                        )
                    }
                }
/*        private val defaultRecordData: ObjectNode =
            Jsons.objectNode().also { recordData: ObjectNode ->
                stream.schema.forEach { recordData.putNull(it.id) }
                if (feed is Stream && precedingGlobalFeed != null || isTriggerBasedCdc) {
                    metaFieldDecorator.decorateRecordData(
                        timestamp = outputer.recordEmittedAt.atOffset(ZoneOffset.UTC),
                        globalStateValue =
                            if (precedingGlobalFeed != null)
                                stateManager.scoped(precedingGlobalFeed).current()
                            else null,
                        stream,
                        recordData,
                    )
                }
            }*/

//        private val reusedRecordData: ObjectNode = defaultRecordData.deepCopy()

        private val reusedRecordMessageWithoutChanges: AirbyteRecordMessageProtobuf.Builder =
            AirbyteRecordMessageProtobuf.newBuilder()
                .setStreamName(stream.name)
                .setStreamNamespace(stream.namespace)
                .setEmittedAtMs(outputer.recordEmittedAt.toEpochMilli())
//                .setData()
//                .setMeta()

            /*AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(stream.name)
                        .withNamespace(stream.namespace)
                        .withEmittedAt(outputer.recordEmittedAt.toEpochMilli())
                        .withData(reusedRecordData)
                )*/

        private val reusedRecordMeta = AirbyteRecordMessageMeta()

        val reusedMessageWithoutChanges: AirbyteMessageProtobuf.Builder =
            AirbyteMessageProtobuf.newBuilder()


        private val reusedRecordMessageWithChanges: AirbyteRecordMessageProtobuf.Builder =
            AirbyteRecordMessageProtobuf.newBuilder()
                .setStreamName(stream.name)
                .setStreamNamespace(stream.namespace)
                .setEmittedAtMs(outputer.recordEmittedAt.toEpochMilli())
//                .setData()
//                .setMeta()

/*
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(stream.name)
                        .withNamespace(stream.namespace)
                        .withEmittedAt(outputer.recordEmittedAt.toEpochMilli())
                        .withData(reusedRecordData)
                        .withMeta(reusedRecordMeta)
                )
*/
    }

    companion object {

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
            outputConsumer: SimpleOutputConsumer,
            metaFieldDecorator: MetaFieldDecorator,
            stateManager: StateManager,
            feed: Feed,
            boostedOutputConsumerFactory: BoostedOutputConsumerFactory?,
            outputFormat: String
        ): FeedBootstrap<*> =
            when (feed) {
                is Global ->
                    GlobalFeedBootstrap(outputConsumer, metaFieldDecorator, stateManager, feed, boostedOutputConsumerFactory, outputFormat)
                is Stream ->
                    StreamFeedBootstrap(outputConsumer, metaFieldDecorator, stateManager, feed, boostedOutputConsumerFactory, outputFormat)
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

    fun accept(recordData: InternalRow, changes: Map<Field, FieldValueChange>?)
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
    outputConsumer: SimpleOutputConsumer,
    metaFieldDecorator: MetaFieldDecorator,
    stateManager: StateManager,
    global: Global,
    boostedOutputConsumerFactory: BoostedOutputConsumerFactory?,
    outputFormat: String
) : FeedBootstrap<Global>(outputConsumer, metaFieldDecorator, stateManager, global, boostedOutputConsumerFactory, outputFormat)

/** [FeedBootstrap] implementation for [Stream] feeds. */
class StreamFeedBootstrap(
    outputConsumer: SimpleOutputConsumer,
    metaFieldDecorator: MetaFieldDecorator,
    stateManager: StateManager,
    stream: Stream,
    boostedOutputConsumerFactory: BoostedOutputConsumerFactory?,
    outputFormat: String
) : FeedBootstrap<Stream>(outputConsumer, metaFieldDecorator, stateManager, stream, boostedOutputConsumerFactory, outputFormat) {

    /** A [StreamRecordConsumer] instance for this [Stream]. */
    fun streamRecordConsumer(socketJsonOutputConsumer: SocketJsonOutputConsumer?): StreamRecordConsumer = EfficientStreamRecordConsumer(
        feed.streams.filter { feed.id == it.id }.first(),
        socketJsonOutputConsumer)
    fun protoStreamRecordConsumer(protoOutputConsumer: SocketProtobufOutputConsumer, partitionId: String?): ProtoEfficientStreamRecordConsumer = ProtoEfficientStreamRecordConsumer(
        feed.streams.filter { feed.id == it.id }.first(),
        protoOutputConsumer, partitionId)
}
