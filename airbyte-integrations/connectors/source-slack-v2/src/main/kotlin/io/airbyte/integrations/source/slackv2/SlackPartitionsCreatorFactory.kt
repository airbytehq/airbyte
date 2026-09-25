/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.read.ConfiguredSyncMode
import io.airbyte.cdk.read.CreateNoPartitions
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.PartitionsCreator
import io.airbyte.cdk.read.PartitionsCreatorFactory
import io.airbyte.cdk.read.PartitionsCreatorFactorySupplier
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.util.concurrent.atomic.AtomicLong

private val log = KotlinLogging.logger {}

/**
 * Entry point of the READ operation: one [PartitionReader] per stream feed, reading the stream to
 * its end (users, channels, channel_members) or until the checkpoint interval elapses
 * (channel_messages, threads), and no partition once the stream is complete.
 *
 * A single reader per stream is deliberate: Slack rate limits each Web API method per app and
 * workspace, so several readers of the same stream would share one budget and gain nothing, while
 * different streams (different methods) are already read concurrently by the CDK.
 */
@Singleton
class SlackPartitionsCreatorFactory(
    val sharedState: SlackSharedState,
) : PartitionsCreatorFactory {

    override fun make(feedBootstrap: FeedBootstrap<*>): PartitionsCreator? {
        if (feedBootstrap !is StreamFeedBootstrap) {
            return CreateNoPartitions
        }
        return SlackPartitionsCreator(feedBootstrap, sharedState)
    }
}

/** [io.airbyte.cdk.read.ReadOperation] looks up the suppliers, not the factories. */
@Singleton
class SlackPartitionsCreatorFactorySupplier(
    val factory: SlackPartitionsCreatorFactory,
) : PartitionsCreatorFactorySupplier<SlackPartitionsCreatorFactory> {
    override fun get(): SlackPartitionsCreatorFactory = factory
}

class SlackPartitionsCreator(
    val feedBootstrap: StreamFeedBootstrap,
    val sharedState: SlackSharedState,
) : PartitionsCreator {

    override fun tryAcquireResources(): PartitionsCreator.TryAcquireResourcesStatus =
        PartitionsCreator.TryAcquireResourcesStatus.READY_TO_RUN

    override suspend fun run(): List<PartitionReader> {
        val stream: Stream = feedBootstrap.feed
        if (sharedState.isComplete(stream.id)) {
            return emptyList()
        }
        val slackStream: SlackStream =
            SlackStream.byName(stream.name)
                ?: run {
                    log.warn { "Unknown stream ${stream.id}; nothing to read." }
                    sharedState.markComplete(stream.id)
                    return emptyList()
                }
        return when (slackStream) {
            SlackStream.USERS,
            SlackStream.CHANNELS,
            SlackStream.CHANNEL_MEMBERS -> {
                if (SlackFullRefreshState.isComplete(feedBootstrap.currentState)) {
                    log.info { "Stream ${stream.id} was read to the end already; nothing to do." }
                    sharedState.markComplete(stream.id)
                    emptyList()
                } else {
                    listOf(SlackSimpleStreamReader(slackStream, feedBootstrap, sharedState))
                }
            }
            SlackStream.CHANNEL_MESSAGES,
            SlackStream.THREADS -> {
                val progress: SlackHistoryProgress =
                    sharedState.progress(stream.id) {
                        SlackHistoryProgress.start(
                            slackStream,
                            SlackHistoryStreamState.parse(stream.id, feedBootstrap.currentState),
                            fullRefresh =
                                stream.configuredSyncMode == ConfiguredSyncMode.FULL_REFRESH,
                            sharedState,
                        )
                    }
                if (progress.complete) {
                    sharedState.markComplete(stream.id)
                    emptyList()
                } else {
                    listOf(
                        SlackHistoryStreamReader(slackStream, feedBootstrap, sharedState, progress)
                    )
                }
            }
        }
    }

    override fun releaseResources() {}
}

/**
 * Emits RECORD messages for one stream straight to the output consumer, with the whole Slack object
 * as record data. The CDK's own [io.airbyte.cdk.read.StreamRecordConsumer] only writes the fields
 * of the configured schema, but Slack's schemas are open (`additionalProperties: true`) and the
 * legacy connector emitted every field Slack returned; this keeps that behaviour.
 */
class SlackRecordEmitter(private val outputConsumer: OutputConsumer, val stream: Stream) {
    private val recordMessage: AirbyteRecordMessage =
        AirbyteRecordMessage()
            .withStream(stream.name)
            .withNamespace(stream.namespace)
            .withEmittedAt(outputConsumer.recordEmittedAt.toEpochMilli())
    private val message: AirbyteMessage =
        AirbyteMessage().withType(AirbyteMessage.Type.RECORD).withRecord(recordMessage)
    val count = AtomicLong()

    fun emit(data: ObjectNode) {
        synchronized(this) {
            recordMessage.data = data
            outputConsumer.accept(message)
        }
        count.incrementAndGet()
    }
}
