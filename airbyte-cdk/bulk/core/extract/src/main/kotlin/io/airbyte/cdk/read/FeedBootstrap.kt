/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.flatbuffers.FlatBufferBuilder
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.MetaFieldDecorator
import io.airbyte.cdk.output.FlatBufferResult
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.output.UnixDomainSocketOutputConsumer
import io.airbyte.cdk.output.UnixDomainSocketOutputConsumerProvider
import io.airbyte.protocol.AirbyteRecord
import io.airbyte.protocol.AirbyteRecord.AirbyteRecordMessage.Builder
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange

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
    //    /** The [OutputConsumer] instance to which [StreamRecordConsumer] will delegate to. */
    val outputConsumer: OutputConsumer,
    /**
     * The [MetaFieldDecorator] instance which [StreamRecordConsumer] will use to decorate records.
     */
    val metaFieldDecorator: MetaFieldDecorator,
    /** [StateManager] singleton which is encapsulated by this [FeedBootstrap]. */
    private val stateManager: StateManager,
    /** [Feed] to emit records for. */
    val feed: T,
    /** [UnixDomainSocketOutputConsumerProvider] to provide socket consumers. */
    private val socketProvider: UnixDomainSocketOutputConsumerProvider,
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

    /**
     * Efficient implementation of [StreamRecordConsumer].
     *
     * It's efficient because it re-uses the same Airbyte protocol message instance from one record
     * to the next. Not doing this generates a lot of garbage and the increased GC activity has a
     * measurable impact on performance.
     */
    private inner class EfficientStreamRecordConsumer(override val stream: Stream) :
        StreamRecordConsumer {
        lateinit var socketOutputConsumer: UnixDomainSocketOutputConsumer
        override suspend fun acceptAsync(
            recordData: ObjectNode,
            changes: Map<Field, FieldValueChange>?,
            recordBuilder: Builder,
            fbResult: FlatBufferResult,
            totalNum: Int?,
            num: Long?
        ) {
            if (::socketOutputConsumer.isInitialized.not()) {
                socketOutputConsumer = socketProvider.getNextFreeSocketConsumer(num!!.toInt())
            }
            socketOutputConsumer.acceptAsyncMaybe(recordData, recordBuilder, fbResult, stream.namespace ?: "", stream.name)
        }

        override fun accept(
            recordData: ObjectNode,
            changes: Map<Field, FieldValueChange>?,
            totalNum: Int?,
            num: Long?
        ) {
            throw NotImplementedError("This method is not implemented. Use acceptAsync instead.")
        }

        override fun close() {
            if (::socketOutputConsumer.isInitialized) {
                socketOutputConsumer.busy = false
            }
        }
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
            outputConsumer: OutputConsumer,
            metaFieldDecorator: MetaFieldDecorator,
            stateManager: StateManager,
            feed: Feed,
            socketProvider: UnixDomainSocketOutputConsumerProvider,
        ): FeedBootstrap<*> =
            when (feed) {
                is Global ->
                    GlobalFeedBootstrap(
                        outputConsumer,
                        metaFieldDecorator,
                        stateManager,
                        feed,
                        socketProvider
                    )
                is Stream ->
                    StreamFeedBootstrap(
                        outputConsumer,
                        metaFieldDecorator,
                        stateManager,
                        feed,
                        socketProvider
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
interface StreamRecordConsumer : AutoCloseable {

    val stream: Stream

    fun accept(
        recordData: ObjectNode,
        changes: Map<Field, FieldValueChange>?,
        totalNum: Int? = null,
        num: Long? = null
    )

    suspend fun acceptAsync(
        recordData: ObjectNode,
        changes: Map<Field, FieldValueChange>?,
        recordBuilder: AirbyteRecord.AirbyteRecordMessage.Builder,
        fbResult: FlatBufferResult,
        totalNum: Int? = null,
        num: Long? = null
    ) {
        accept(recordData, changes, totalNum, num)
    }

    override fun close() {
        /* no-op */
    }
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
    outputConsumer: OutputConsumer,
    metaFieldDecorator: MetaFieldDecorator,
    stateManager: StateManager,
    global: Global,
    socketProvider: UnixDomainSocketOutputConsumerProvider,
) : FeedBootstrap<Global>(outputConsumer, metaFieldDecorator, stateManager, global, socketProvider)

/** [FeedBootstrap] implementation for [Stream] feeds. */
class StreamFeedBootstrap(
    outputConsumer: OutputConsumer,
    metaFieldDecorator: MetaFieldDecorator,
    stateManager: StateManager,
    stream: Stream,
    socketProvider: UnixDomainSocketOutputConsumerProvider,
) :
    FeedBootstrap<Stream>(
        outputConsumer,
        metaFieldDecorator,
        stateManager,
        stream,
        socketProvider
    ) {

    /** A [StreamRecordConsumer] instance for this [Stream]. */
    fun streamRecordConsumer(): StreamRecordConsumer = streamRecordConsumers()[feed.id]!!
}
