/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.read.UnlimitedTimePartitionReader
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive

private val log = KotlinLogging.logger {}

/**
 * Reads one of the full-refresh-only streams to its end in a single run: `users` (`users.list`),
 * `channels` (the sync's channel list, see [SlackChannelCatalog]) or `channel_members`
 * (`conversations.members` for every listed channel, one `{member_id, channel_id}` record per
 * member, like the legacy connector). None of them is resumable, so no checkpoint is taken before
 * the end; the final state is a completion marker.
 */
class SlackSimpleStreamReader(
    val slackStream: SlackStream,
    val feedBootstrap: StreamFeedBootstrap,
    val sharedState: SlackSharedState,
) : UnlimitedTimePartitionReader {

    val stream: Stream = feedBootstrap.feed
    private val emitter = SlackRecordEmitter(feedBootstrap.outputConsumer, stream)
    private val acquiredResources = AtomicReference<Map<ResourceType, Resource.Acquired>?>()

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val resources: Map<ResourceType, Resource.Acquired> =
            sharedState.tryAcquireReaderResources(listOf(ResourceType.RESOURCE_DB_CONNECTION))
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        acquiredResources.set(resources)
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run() {
        val client: SlackApiClient = sharedState.client
        when (slackStream) {
            SlackStream.USERS -> {
                client.pages("users.list", mapOf("limit" to PAGE_LIMIT.toString())) { page, _, _ ->
                    currentCoroutineContext().ensureActive()
                    page.get("members")?.forEach { if (it is ObjectNode) emitter.emit(it) }
                    true
                }
            }
            SlackStream.CHANNELS -> {
                for (channel: SlackChannel in sharedState.channels().channels) {
                    emitter.emit(channel.raw)
                }
            }
            SlackStream.CHANNEL_MEMBERS -> {
                for (channel: SlackChannel in sharedState.channels().channels) {
                    currentCoroutineContext().ensureActive()
                    try {
                        client.pages(
                            "conversations.members",
                            mapOf("channel" to channel.id, "limit" to PAGE_LIMIT.toString()),
                        ) { page, _, _ ->
                            page.get("members")?.forEach { member ->
                                emitter.emit(
                                    Jsons.objectNode()
                                        .put("member_id", member.asText())
                                        .put(SlackStream.CHANNEL_ID, channel.id),
                                )
                            }
                            true
                        }
                    } catch (e: SlackSkipException) {
                        log.warn {
                            "Skipping the members of channel ${channel.name} (${channel.id}): ${e.error}"
                        }
                    }
                }
            }
            else -> throw IllegalStateException("$slackStream is not a simple stream")
        }
        log.info { "Read stream ${stream.id} to the end: ${emitter.count.get()} record(s)." }
        sharedState.markComplete(stream.id)
    }

    override fun checkpoint(): PartitionReadCheckpoint =
        PartitionReadCheckpoint(SlackFullRefreshState.COMPLETE_STATE, emitter.count.get())

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.values?.forEach { it.close() }
    }

    companion object {
        /** Slack documents "under 1000" for `users.list` and `conversations.members`. */
        const val PAGE_LIMIT = 999
    }
}
