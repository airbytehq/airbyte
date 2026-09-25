/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.node.ObjectNode
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.annotation.PreDestroy
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.time.Clock
import java.time.Instant
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

private val log = KotlinLogging.logger {}

/**
 * State shared by all partitions of a READ: the configuration, the one [SlackApiClient] (whose
 * per-method rate limiters must be shared by every reader), the instant the sync started (the upper
 * bound of every message window), the channel list (fetched and, if configured, joined once per
 * sync), the read progress of each stream, and a cache of `conversations.history` pages so that the
 * channel_messages and threads streams, which scan the same history, fetch each page once.
 */
@Singleton
class SlackSharedState
@Inject
constructor(
    val configuration: SlackSourceConfiguration,
    val concurrencyResource: ConcurrencyResource,
    val resourceAcquirer: ResourceAcquirer,
    /** Empty for every operation but READ. */
    configuredCatalog: ConfiguredAirbyteCatalog = ConfiguredAirbyteCatalog(),
    @Value("\${$RATE_LIMIT_SCALE_PROPERTY:1.0}") val rateLimitScale: Double = 1.0,
    /** `limit` of `conversations.history` and `conversations.replies` requests. */
    @Value("\${$HISTORY_PAGE_LIMIT_PROPERTY:$DEFAULT_HISTORY_PAGE_LIMIT}")
    val historyPageLimit: Int = DEFAULT_HISTORY_PAGE_LIMIT,
    @Value("\${$HISTORY_CACHE_BYTES_PROPERTY:$DEFAULT_HISTORY_CACHE_BYTES}")
    val historyCacheBytes: Long = DEFAULT_HISTORY_CACHE_BYTES,
) {
    private val clientDelegate: Lazy<SlackApiClient> = lazy {
        SlackApiClient(configuration, rateLimitScale)
    }

    val client: SlackApiClient by clientDelegate

    /**
     * Upper bound (`latest`) of every message window of this sync, frozen when the READ starts so
     * that the channel_messages and threads streams read the same windows and the saved cursors are
     * consistent. Messages posted after it are read by the next sync. Deliberately the system
     * clock, not the CDK's injectable `Clock` bean (a fixed instant in tests).
     */
    val syncStart: Instant = Clock.systemUTC().instant()

    private val completedStreams: MutableSet<StreamIdentifier> = ConcurrentHashMap.newKeySet()

    private val progress: MutableMap<StreamIdentifier, Any> = ConcurrentHashMap()

    /** The `conversations.history` consumers of this sync: channel_messages and/or threads. */
    val historyConsumers: Int =
        configuredCatalog.streams.count {
            it.stream.name == SlackStream.CHANNEL_MESSAGES.streamName ||
                it.stream.name == SlackStream.THREADS.streamName
        }

    val historyCache: HistoryPageCache = HistoryPageCache(historyConsumers, historyCacheBytes)

    private val channelsMutex = Mutex()
    private var channelCatalog: SlackChannelCatalog? = null

    /** The channel list of this sync, fetched (and joined) once; safe to call concurrently. */
    suspend fun channels(): SlackChannelCatalog =
        channelsMutex.withLock {
            channelCatalog
                ?: SlackChannelCatalog.fetch(configuration, client).also { channelCatalog = it }
        }

    fun markComplete(streamID: StreamIdentifier) {
        completedStreams.add(streamID)
    }

    fun isComplete(streamID: StreamIdentifier): Boolean = streamID in completedStreams

    /** The in-memory progress object of a stream, created on its first round of this READ. */
    @Suppress("UNCHECKED_CAST")
    fun <T : Any> progress(streamID: StreamIdentifier, create: () -> T): T =
        progress.computeIfAbsent(streamID) { create() } as T

    fun tryAcquireReaderResources(
        resourceTypes: List<ResourceType>,
    ): Map<ResourceType, Resource.Acquired>? = resourceAcquirer.tryAcquire(resourceTypes)

    @PreDestroy
    fun close() {
        if (clientDelegate.isInitialized()) {
            client.close()
        }
    }

    companion object {
        const val RATE_LIMIT_SCALE_PROPERTY = "airbyte.connector.extract.slack.rate-limit-scale"
        const val HISTORY_PAGE_LIMIT_PROPERTY = "airbyte.connector.extract.slack.history-page-limit"
        const val HISTORY_CACHE_BYTES_PROPERTY =
            "airbyte.connector.extract.slack.history-cache-bytes"

        /** `conversations.history` documents a maximum of 999 (the legacy connector sent 1000). */
        const val DEFAULT_HISTORY_PAGE_LIMIT = 999
        const val DEFAULT_HISTORY_CACHE_BYTES: Long = 128L * 1024 * 1024
    }
}

/** A channel as listed by `conversations.list`, with the raw object for the channels stream. */
data class SlackChannel(val raw: ObjectNode) {
    val id: String = raw.get("id")?.asText() ?: ""
    val name: String = raw.get("name")?.asText() ?: ""
    val isMember: Boolean = raw.get("is_member")?.asBoolean() ?: false
    val isArchived: Boolean = raw.get("is_archived")?.asBoolean() ?: false
}

/**
 * The channels of the workspace that pass the configured filters, listed once per sync with
 * `conversations.list` (`types` from `include_private_channels`, `exclude_archived` from
 * `include_archived_channels`, 999 per page) and filtered by `channel_filter` on the channel name,
 * like the legacy connector. When `join_channels` is set, the bot joins every listed channel it is
 * not a member of (archived channels excepted) with `conversations.join`; the records keep the
 * `is_member` value Slack listed, as they did in the legacy connector.
 */
@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "Kotlin coroutines")
class SlackChannelCatalog(val channels: List<SlackChannel>) {

    /** The channels whose messages and threads are read: members, or every channel when joining. */
    fun messageChannels(configuration: SlackSourceConfiguration): List<SlackChannel> =
        channels.filter { it.isMember || configuration.joinChannels }

    @SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "Kotlin coroutines")
    companion object {
        const val PAGE_LIMIT = 999

        suspend fun fetch(
            configuration: SlackSourceConfiguration,
            client: SlackApiClient,
        ): SlackChannelCatalog {
            val params: Map<String, String> =
                mapOf(
                    "types" to
                        if (configuration.includePrivateChannels) "public_channel,private_channel"
                        else "public_channel",
                    "exclude_archived" to (!configuration.includeArchivedChannels).toString(),
                    "limit" to PAGE_LIMIT.toString(),
                )
            val listed = ArrayList<SlackChannel>()
            client.pages("conversations.list", params) { page, _, _ ->
                page.get("channels")?.forEach { channel ->
                    if (channel is ObjectNode) listed.add(SlackChannel(channel))
                }
                true
            }
            val filter: Set<String> = configuration.channelFilter
            val selected: List<SlackChannel> =
                if (filter.isEmpty()) listed else listed.filter { it.name in filter }
            log.info {
                "Listed ${listed.size} channel(s), ${selected.size} selected" +
                    (if (filter.isEmpty()) "" else " by channel_filter $filter")
            }
            if (configuration.joinChannels) {
                join(selected, client)
            }
            return SlackChannelCatalog(selected)
        }

        private suspend fun join(channels: List<SlackChannel>, client: SlackApiClient) {
            val toJoin: List<SlackChannel> = channels.filter { !it.isMember && !it.isArchived }
            if (toJoin.isEmpty()) {
                return
            }
            log.info { "Joining ${toJoin.size} channel(s) the bot is not a member of" }
            for (channel in toJoin) {
                try {
                    client.post("conversations.join", mapOf("channel" to channel.id))
                    log.info { "Successfully joined channel: ${channel.name}" }
                } catch (e: SlackSkipException) {
                    log.warn { "Unable to join channel: ${channel.name}. Reason: ${e.error}" }
                } catch (e: SlackApiException) {
                    log.warn { "Unable to join channel: ${channel.name}. Reason: ${e.error}" }
                }
            }
        }
    }
}

/**
 * Pages of `conversations.history`, keyed by their exact request, kept until every consumer stream
 * of this sync has read them (channel_messages and threads scan the same windows on a first sync)
 * and bounded by [maxBytes] (oldest first out). Concurrent misses on the same page (the two streams
 * usually start on the same channel at the same moment) share one fetch. A miss is just a fetch;
 * the cache never changes what a stream reads, only how often Slack is asked.
 */
@SuppressFBWarnings(value = ["NP_NONNULL_PARAM_VIOLATION"], justification = "Kotlin coroutines")
class HistoryPageCache(private val consumers: Int, private val maxBytes: Long) {
    private class Entry(val page: ObjectNode, val bytes: Int, var remainingReads: Int)

    private val lock = Any()
    private val entries = LinkedHashMap<String, Entry>()
    private val inFlight = HashMap<String, CompletableDeferred<ObjectNode>>()
    private var totalBytes: Long = 0
    var hits: Long = 0
        private set
    var misses: Long = 0
        private set

    val enabled: Boolean
        get() = consumers > 1 && maxBytes > 0

    /** Fetches the page through [fetch] unless another stream already did. */
    suspend fun page(key: String, fetch: suspend () -> ObjectNode): ObjectNode {
        if (!enabled) {
            return fetch()
        }
        val deferred: CompletableDeferred<ObjectNode>
        val owner: Boolean
        synchronized(lock) {
            consume(key)?.let {
                hits++
                return it
            }
            val existing: CompletableDeferred<ObjectNode>? = inFlight[key]
            if (existing != null) {
                hits++
                deferred = existing
                owner = false
            } else {
                misses++
                deferred = CompletableDeferred()
                inFlight[key] = deferred
                owner = true
            }
        }
        if (!owner) {
            val page: ObjectNode = deferred.await()
            synchronized(lock) { consume(key) }
            return page
        }
        val page: ObjectNode =
            try {
                fetch()
            } catch (e: Throwable) {
                synchronized(lock) { inFlight.remove(key) }
                deferred.completeExceptionally(e)
                throw e
            }
        val bytes: Int = Jsons.writeValueAsBytes(page).size
        synchronized(lock) {
            inFlight.remove(key)
            if (bytes <= maxBytes && !entries.containsKey(key)) {
                entries[key] = Entry(page, bytes, consumers - 1)
                totalBytes += bytes
                val iterator = entries.entries.iterator()
                while (totalBytes > maxBytes && iterator.hasNext()) {
                    val oldest = iterator.next()
                    iterator.remove()
                    totalBytes -= oldest.value.bytes
                }
            }
        }
        deferred.complete(page)
        return page
    }

    /** Takes one read of the cached page, removing it after its last consumer; null when absent. */
    private fun consume(key: String): ObjectNode? {
        val entry: Entry = entries[key] ?: return null
        entry.remainingReads--
        if (entry.remainingReads <= 0) {
            entries.remove(key)
            totalBytes -= entry.bytes
        }
        return entry.page
    }

    fun size(): Int = synchronized(lock) { entries.size }
}
