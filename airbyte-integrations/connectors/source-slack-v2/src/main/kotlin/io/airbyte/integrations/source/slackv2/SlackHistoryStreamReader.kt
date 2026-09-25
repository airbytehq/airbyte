/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.ensureActive

private val log = KotlinLogging.logger {}

/**
 * The progress of the channel_messages or threads stream over a whole READ, shared by the
 * successive [SlackHistoryStreamReader]s of the stream (one per checkpoint round). It holds the
 * bounds of the sync, the cursors to emit, the channels done so far and where the current channel
 * stopped, and it renders the [OpaqueStateValue] of every checkpoint.
 *
 * **Bounds.** Every channel is read from its lower bound up to [latestBound]. The lower bound is
 * the saved cursor of the channel minus `lookback_window` (or `start_date` for a channel without
 * one, and for a full refresh); [latestBound] is the instant the sync started. A channel that has
 * been read to the end gets [latestBound] as its cursor. A sync that was interrupted keeps its
 * original bound when it is resumed (its `done` channels are skipped and the current channel
 * continues where it stopped), so that every channel ends the sync at the same cursor.
 *
 * **Threads watermark.** [repliesWatermark] is the bound of the last sync that completed: a thread
 * whose `latest_reply` is older than it got no new reply since that sync, so its
 * `conversations.replies` call is skipped. The lookback window widens the history that is scanned
 * for thread parents, not this test: Slack does not move `latest_reply` on edits or deletions, so
 * re-fetching older threads would find nothing new. The watermark is null for a full refresh and
 * for the first sync after a legacy state, whose cursors are maxima of record timestamps rather
 * than sync bounds.
 */
class SlackHistoryProgress(
    val slackStream: SlackStream,
    val fullRefresh: Boolean,
    val startDate: Double,
    val lookbackSeconds: Long,
    val windowSeconds: Long,
    /** `latest` of every window of this sync. */
    val latestBound: Double,
    val repliesWatermark: Double?,
    initialCursors: Map<String, Double>,
    private val globalCursor: Double?,
    done: Set<String>,
    initialProgress: SlackChannelProgress?,
) {
    private val cursors: MutableMap<String, Double> = ConcurrentHashMap(initialCursors)
    val done: MutableSet<String> = ConcurrentHashMap.newKeySet<String>().apply { addAll(done) }

    @Volatile var current: SlackChannelProgress? = initialProgress
    @Volatile var complete: Boolean = false

    /** Threads fetched in this sync per channel, so that a thread is emitted once. */
    val fetchedThreads: MutableMap<String, MutableSet<String>> = ConcurrentHashMap()
    val nonMarketplaceWarned = AtomicBoolean(false)
    val stats = Stats()

    class Stats {
        val historyPages = AtomicLong()
        val messages = AtomicLong()
        val threadsFetched = AtomicLong()
        val threadsSkippedUnchanged = AtomicLong()
        val threadsWithoutReplies = AtomicLong()
    }

    /** `oldest` of the first window of a channel (a resumed channel continues from [current]). */
    fun lowerBound(channel: String): Double {
        if (fullRefresh) return startDate
        val cursor: Double =
            when (slackStream) {
                SlackStream.THREADS -> globalCursor
                else -> cursors[channel] ?: if (cursors.isEmpty()) globalCursor else null
            }
                ?: return startDate
        return maxOf(startDate, cursor - lookbackSeconds)
    }

    fun channelDone(channel: String) {
        cursors[channel] = latestBound
        done.add(channel)
        current = null
    }

    fun state(): OpaqueStateValue =
        SlackHistoryStreamState.emit(
            channelCursors =
                if (slackStream == SlackStream.THREADS) {
                    // One global cursor: the bound once the sync is complete, else the saved one.
                    mapOf("*" to (if (complete) latestBound else (globalCursor ?: startDate)))
                } else cursors,
            syncStart = latestBound,
            lookbackSeconds = lookbackSeconds,
            threads = slackStream == SlackStream.THREADS,
            done = if (complete) emptySet() else done,
            progress = if (complete) null else current,
            watermark = if (complete) latestBound else repliesWatermark,
        )

    companion object {
        fun start(
            slackStream: SlackStream,
            saved: SlackHistoryStreamState,
            fullRefresh: Boolean,
            sharedState: SlackSharedState,
        ): SlackHistoryProgress {
            val configuration: SlackSourceConfiguration = sharedState.configuration
            val resumed: Boolean = !fullRefresh || saved.interrupted
            val interrupted: Boolean = resumed && saved.interrupted
            val latestBound: Double =
                if (interrupted) saved.syncStart!! else SlackTs.fromInstant(sharedState.syncStart)
            log.info {
                "Stream ${slackStream.streamName}: " +
                    (if (interrupted)
                        "resuming the sync started at ${saved.syncStart} (${saved.done.size} channel(s) done)"
                    else "starting a sync with latest bound $latestBound") +
                    (if (fullRefresh) " (full refresh)" else "")
            }
            return SlackHistoryProgress(
                slackStream = slackStream,
                fullRefresh = fullRefresh,
                startDate = SlackTs.fromInstant(configuration.startDate),
                lookbackSeconds = configuration.lookbackWindow.toSeconds(),
                windowSeconds = configuration.channelMessagesWindow.toSeconds(),
                latestBound = latestBound,
                repliesWatermark = if (fullRefresh) null else saved.watermark,
                initialCursors = if (fullRefresh) emptyMap() else saved.channelCursors,
                globalCursor = if (fullRefresh) null else saved.globalCursor,
                done = if (interrupted) saved.done else emptySet(),
                initialProgress = if (interrupted) saved.progress else null,
            )
        }
    }
}

/**
 * Reads the channel_messages or threads stream, channel after channel, until every selected channel
 * is done or the checkpoint interval has elapsed; the CDK then takes the checkpoint and asks for a
 * new reader, which continues from the shared [SlackHistoryProgress].
 *
 * Each channel's history is read in date windows of `channel_messages_window_size` days with
 * `conversations.history` (`inclusive`, `oldest`, `latest`, cursor pagination, newest first),
 * through the shared page cache so that the two streams fetch each page once.
 * - channel_messages emits every message with `channel_id` and `float_ts` added.
 * - threads emits, for every history message, the messages `conversations.replies` would return: a
 * message without replies is emitted as is, without a call (Slack returns just the message for such
 * a `ts`; the legacy connector made the call anyway, one per channel message); a thread parent is
 * fetched once per sync, and skipped when its `latest_reply` predates the last completed sync.
 */
class SlackHistoryStreamReader(
    val slackStream: SlackStream,
    val feedBootstrap: StreamFeedBootstrap,
    val sharedState: SlackSharedState,
    val progress: SlackHistoryProgress,
) : PartitionReader {

    val stream: Stream = feedBootstrap.feed
    private val configuration: SlackSourceConfiguration = sharedState.configuration
    private val emitter = SlackRecordEmitter(feedBootstrap.outputConsumer, stream)
    private val acquiredResources = AtomicReference<Map<ResourceType, Resource.Acquired>?>()
    private var deadlineNanos: Long = Long.MAX_VALUE

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val resources: Map<ResourceType, Resource.Acquired> =
            sharedState.tryAcquireReaderResources(listOf(ResourceType.RESOURCE_DB_CONNECTION))
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        acquiredResources.set(resources)
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override suspend fun run() {
        deadlineNanos = System.nanoTime() + configuration.checkpointTargetInterval.toNanos()
        val channels: List<SlackChannel> = sharedState.channels().messageChannels(configuration)
        for (channel: SlackChannel in channels) {
            if (channel.id in progress.done) continue
            currentCoroutineContext().ensureActive()
            val finished: Boolean =
                try {
                    readChannel(channel)
                } catch (e: SlackSkipException) {
                    log.warn {
                        "Skipping channel ${channel.name} (${channel.id}) for ${slackStream.streamName}: ${e.error}"
                    }
                    true
                }
            if (!finished) {
                log.info {
                    "Pausing ${slackStream.streamName} for a checkpoint after ${emitter.count.get()} record(s); " +
                        "${progress.done.size}/${channels.size} channel(s) done"
                }
                return
            }
            progress.channelDone(channel.id)
        }
        progress.complete = true
        sharedState.markComplete(stream.id)
        val s = progress.stats
        log.info {
            "Read ${slackStream.streamName} to the end: ${emitter.count.get()} record(s) from " +
                "${channels.size} channel(s), ${s.historyPages.get()} history page(s) " +
                "(cache hits ${sharedState.historyCache.hits}, misses ${sharedState.historyCache.misses})" +
                if (slackStream == SlackStream.THREADS) {
                    ", ${s.threadsFetched.get()} thread(s) fetched, ${s.threadsSkippedUnchanged.get()} " +
                        "skipped as unchanged, ${s.threadsWithoutReplies.get()} message(s) without replies"
                } else ""
        }
    }

    /** True when the channel was read to the end, false when the deadline paused it. */
    private suspend fun readChannel(channel: SlackChannel): Boolean {
        val resume: SlackChannelProgress? = progress.current?.takeIf { it.channel == channel.id }
        var windowOldest: Double = resume?.windowOldest ?: progress.lowerBound(channel.id)
        var pageCursor: String? = resume?.pageCursor
        var resumeTs: Double? = resume?.pageResumeTs
        log.info {
            "Reading ${slackStream.streamName} of channel ${channel.name} (${channel.id}) from " +
                "$windowOldest to ${progress.latestBound}" +
                (resume?.let { ", resumed at $it" } ?: "")
        }
        while (true) {
            val windowLatest: Double =
                minOf(windowOldest + progress.windowSeconds, progress.latestBound)
            while (true) {
                val params: Map<String, String> =
                    mapOf(
                        "channel" to channel.id,
                        "inclusive" to "true",
                        "oldest" to SlackTs.toRequestParam(windowOldest),
                        "latest" to SlackTs.toRequestParam(windowLatest),
                        "limit" to sharedState.historyPageLimit.toString(),
                    ) + (pageCursor?.let { mapOf("cursor" to it) } ?: emptyMap())
                val cacheKey: String = params.toSortedMap().toString()
                val page: ObjectNode =
                    sharedState.historyCache.page(cacheKey) {
                        sharedState.client.get("conversations.history", params)
                    }
                progress.stats.historyPages.incrementAndGet()
                val messages: List<ObjectNode> =
                    page.get("messages")?.filterIsInstance<ObjectNode>() ?: emptyList()
                warnIfNonMarketplace(page, messages.size)
                for (message: ObjectNode in messages) {
                    val ts: Double = SlackTs.toDouble(message.get("ts")) ?: continue
                    if (resumeTs != null && ts >= resumeTs) continue
                    processMessage(channel, message)
                    progress.current =
                        SlackChannelProgress(channel.id, windowOldest, windowLatest, pageCursor, ts)
                    if (System.nanoTime() >= deadlineNanos) {
                        return false
                    }
                }
                resumeTs = null
                val next: String? = SlackApiClient.nextCursor(page)
                if (next == null) break
                pageCursor = next
                progress.current =
                    SlackChannelProgress(channel.id, windowOldest, windowLatest, next, null)
                if (System.nanoTime() >= deadlineNanos) {
                    return false
                }
            }
            if (windowLatest >= progress.latestBound) {
                return true
            }
            // Contiguous windows, one microsecond (the resolution of a Slack ts) apart.
            windowOldest = windowLatest + 0.000001
            pageCursor = null
            progress.current =
                SlackChannelProgress(
                    channel.id,
                    windowOldest,
                    minOf(windowOldest + progress.windowSeconds, progress.latestBound)
                )
        }
    }

    private suspend fun processMessage(channel: SlackChannel, message: ObjectNode) {
        progress.stats.messages.incrementAndGet()
        when (slackStream) {
            SlackStream.CHANNEL_MESSAGES -> emitter.emit(decorate(message, channel.id))
            SlackStream.THREADS -> processThreadCandidate(channel, message)
            else -> throw IllegalStateException("$slackStream is not a history stream")
        }
    }

    /**
     * What the legacy connector's `conversations.replies` call for this message would have
     * returned, with as few calls as possible; see the class comment.
     */
    private suspend fun processThreadCandidate(channel: SlackChannel, message: ObjectNode) {
        val ts: String = message.get("ts")?.asText() ?: return
        val threadTs: String? = message.get("thread_ts")?.asText()?.ifBlank { null }
        val replyCount: Int = message.get("reply_count")?.asInt() ?: 0
        val isParentWithReplies: Boolean = threadTs == ts && replyCount > 0
        val isBroadcastReply: Boolean = threadTs != null && threadTs != ts
        if (!isParentWithReplies && !isBroadcastReply) {
            // No thread: Slack would return just this message.
            progress.stats.threadsWithoutReplies.incrementAndGet()
            if (!configuration.threadsIgnoreNoReplies) {
                emitter.emit(decorate(message, channel.id))
            }
            return
        }
        if (isBroadcastReply && configuration.threadsIgnoreNoReplies) {
            // The legacy filter (`thread_ts` set and `reply_count > 0`) drops broadcast replies.
            return
        }
        val fetched: MutableSet<String> =
            progress.fetchedThreads.computeIfAbsent(channel.id) { ConcurrentHashMap.newKeySet() }
        if (!fetched.add(threadTs!!)) {
            return
        }
        val watermark: Double? = progress.repliesWatermark
        if (watermark != null) {
            // A parent tells when its thread last changed; a broadcast reply is itself a reply,
            // posted at its own ts (newer replies of that thread are found through the parent).
            val lastChange: Double? =
                if (isParentWithReplies) SlackTs.toDouble(message.get("latest_reply"))
                else SlackTs.toDouble(message.get("ts"))
            if (lastChange != null && lastChange < watermark) {
                progress.stats.threadsSkippedUnchanged.incrementAndGet()
                return
            }
        }
        progress.stats.threadsFetched.incrementAndGet()
        try {
            sharedState.client.pages(
                "conversations.replies",
                mapOf(
                    "channel" to channel.id,
                    "ts" to threadTs,
                    "limit" to REPLIES_PAGE_LIMIT.toString()
                ),
            ) { page, _, _ ->
                val replies: List<ObjectNode> =
                    page.get("messages")?.filterIsInstance<ObjectNode>() ?: emptyList()
                warnIfNonMarketplace(page, replies.size)
                replies.forEach { emitter.emit(decorate(it, channel.id)) }
                true
            }
        } catch (e: SlackSkipException) {
            log.warn { "Skipping thread $threadTs of channel ${channel.name}: ${e.error}" }
        }
    }

    /**
     * The record: the raw Slack message plus `float_ts` and `channel_id`, as the legacy connector
     * added them.
     */
    private fun decorate(message: ObjectNode, channelId: String): ObjectNode {
        val record: ObjectNode = message.deepCopy()
        record.set<JsonNode>(
            SlackStream.FLOAT_TS,
            SlackTs.floatTsNode(message.get("ts")?.asText() ?: "")
        )
        record.put(SlackStream.CHANNEL_ID, channelId)
        return record
    }

    private fun warnIfNonMarketplace(page: ObjectNode, pageSize: Int) {
        if (
            pageSize == SlackRateLimits.NON_MARKETPLACE_PAGE_SIZE &&
                page.get("has_more")?.asBoolean() == true &&
                sharedState.historyPageLimit > SlackRateLimits.NON_MARKETPLACE_PAGE_SIZE &&
                progress.nonMarketplaceWarned.compareAndSet(false, true)
        ) {
            log.warn {
                "Slack returned ${SlackRateLimits.NON_MARKETPLACE_PAGE_SIZE} messages per page although " +
                    "${sharedState.historyPageLimit} were requested: this Slack app is subject to the " +
                    "non-Marketplace rate limits (1 request per minute and 15 messages per request for " +
                    "conversations.history and conversations.replies). Syncing message history will be " +
                    "slow; authenticate with Airbyte's Slack Marketplace app (OAuth) or an internal app " +
                    "of your own workspace for the standard limits."
            }
        }
    }

    override fun checkpoint(): PartitionReadCheckpoint =
        PartitionReadCheckpoint(progress.state(), emitter.count.get())

    override fun releaseResources() {
        acquiredResources.getAndSet(null)?.values?.forEach { it.close() }
    }

    companion object {
        /** `conversations.replies` documents a default and maximum of 1000. */
        const val REPLIES_PAGE_LIMIT = 1000
    }
}
