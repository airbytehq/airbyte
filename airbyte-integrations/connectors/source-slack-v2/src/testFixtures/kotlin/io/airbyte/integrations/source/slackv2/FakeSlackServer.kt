/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.sun.net.httpserver.HttpExchange
import com.sun.net.httpserver.HttpServer
import io.airbyte.cdk.util.Jsons
import java.io.File
import java.net.InetSocketAddress
import java.net.URLDecoder
import java.nio.charset.StandardCharsets
import java.util.Base64
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.CopyOnWriteArrayList
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong

/**
 * A fake Slack Web API for tests and local development, so that the connector can be exercised
 * without a workspace and without Slack's rate limits: `auth.test`, `users.list`,
 * `conversations.list`, `conversations.members`, `conversations.history`, `conversations.replies`,
 * `conversations.join` and `conversations.info`, with Slack's envelope, cursor pagination
 * (`response_metadata.next_cursor`, opaque base64 like the real ones),
 * `oldest`/`latest`/`inclusive` filtering, threads (`reply_count`, `reply_users`, `latest_reply`
 * derived from the seeded replies), `ok: false` errors (`invalid_auth`, `not_in_channel`,
 * `channel_not_found`, `thread_not_found`, `is_archived`, ...) and, optionally, per-method rate
 * limits answered with HTTP 429 and `Retry-After`, and the non-Marketplace regime (pages capped at
 * 15 messages).
 *
 * Runs in-process on a random port for JUnit ([start]) or standalone for the Docker harness ([main]
 * ).
 */
class FakeSlackServer(
    val workspace: FakeSlackWorkspace,
    private val port: Int = 0,
    /** Requests per minute allowed per method before a 429; unlimited when absent. */
    private val rateLimits: Map<String, Double> = emptyMap(),
    /** Emulates the non-Marketplace regime: history and replies pages hold 15 messages at most. */
    var nonMarketplace: Boolean = false,
    /** `Retry-After` value of a 429 response. */
    var retryAfterSeconds: Int = 1,
) : AutoCloseable {

    private var server: HttpServer? = null
    val requests: MutableList<RecordedRequest> = CopyOnWriteArrayList()
    private val buckets = ConcurrentHashMap<String, Bucket>()
    /** Errors to return once for a method, in order (tests of transient error handling). */
    private val injectedErrors = ConcurrentHashMap<String, ArrayDeque<InjectedError>>()
    val rateLimitedCount = AtomicLong()

    data class RecordedRequest(
        val method: String,
        val params: Map<String, String>,
        val status: Int,
        val error: String?
    )

    data class InjectedError(val httpStatus: Int, val error: String?, val retryAfter: Int? = null)

    val baseUrl: String
        get() = "http://localhost:${server!!.address.port}/api/"

    fun start(): FakeSlackServer {
        val s: HttpServer = HttpServer.create(InetSocketAddress("0.0.0.0", port), 0)
        s.createContext("/api/") { exchange -> handle(exchange) }
        s.executor = Executors.newFixedThreadPool(8)
        s.start()
        server = s
        return this
    }

    fun stop() {
        server?.stop(0)
        server = null
    }

    override fun close() = stop()

    fun injectError(method: String, error: InjectedError) {
        injectedErrors.computeIfAbsent(method) { ArrayDeque() }.addLast(error)
    }

    fun requestCount(method: String): Int = requests.count { it.method == method }

    private fun handle(exchange: HttpExchange) {
        val method: String = exchange.requestURI.path.removePrefix("/api/")
        val params: Map<String, String> = parseParams(exchange)
        var status = 200
        var error: String? = null
        try {
            val token: String? =
                exchange.requestHeaders.getFirst("Authorization")?.removePrefix("Bearer ")?.trim()
                    ?: params["token"]
            val body: ObjectNode =
                when {
                    token.isNullOrBlank() -> err("not_authed")
                    token !in workspace.validTokens -> err("invalid_auth")
                    else -> {
                        val injected: InjectedError? = injectedErrors[method]?.removeFirstOrNull()
                        if (injected != null) {
                            status = injected.httpStatus
                            injected.retryAfter?.let {
                                exchange.responseHeaders.add("Retry-After", it.toString())
                            }
                            if (injected.error != null) err(injected.error)
                            else Jsons.objectNode().put("ok", false)
                        } else if (!acquire(method)) {
                            status = 429
                            rateLimitedCount.incrementAndGet()
                            exchange.responseHeaders.add(
                                "Retry-After",
                                retryAfterSeconds.toString()
                            )
                            err("ratelimited")
                        } else {
                            dispatch(method, params)
                        }
                    }
                }
            error = body.get("error")?.asText()
            val bytes: ByteArray = Jsons.writeValueAsBytes(body)
            exchange.responseHeaders.add("Content-Type", "application/json; charset=utf-8")
            exchange.sendResponseHeaders(status, bytes.size.toLong())
            exchange.responseBody.use { it.write(bytes) }
        } catch (e: Exception) {
            status = 500
            val bytes: ByteArray =
                Jsons.writeValueAsBytes(err("fatal_error").put("detail", e.toString()))
            exchange.sendResponseHeaders(status, bytes.size.toLong())
            exchange.responseBody.use { it.write(bytes) }
        } finally {
            requests.add(RecordedRequest(method, params, status, error))
        }
    }

    private fun dispatch(method: String, params: Map<String, String>): ObjectNode =
        when (method) {
            "auth.test" -> workspace.authTest()
            "users.list" -> workspace.usersList(params)
            "conversations.list" -> workspace.conversationsList(params)
            "conversations.info" -> workspace.conversationsInfo(params)
            "conversations.members" -> workspace.conversationsMembers(params)
            "conversations.history" -> workspace.conversationsHistory(params, nonMarketplace)
            "conversations.replies" -> workspace.conversationsReplies(params, nonMarketplace)
            "conversations.join" -> workspace.conversationsJoin(params)
            else -> err("unknown_method")
        }

    private fun acquire(method: String): Boolean {
        val perMinute: Double = rateLimits[method] ?: return true
        return buckets.computeIfAbsent(method) { Bucket(perMinute) }.tryAcquire()
    }

    /** Token bucket with a burst of one minute's worth of requests, refilled continuously. */
    private class Bucket(private val perMinute: Double) {
        private var tokens: Double = perMinute
        private var last: Long = System.nanoTime()

        @Synchronized
        fun tryAcquire(): Boolean {
            val now: Long = System.nanoTime()
            tokens = minOf(perMinute, tokens + (now - last) * perMinute / 60_000_000_000.0)
            last = now
            if (tokens >= 1.0) {
                tokens -= 1.0
                return true
            }
            return false
        }
    }

    companion object {
        fun err(error: String): ObjectNode = Jsons.objectNode().put("ok", false).put("error", error)

        private fun parseParams(exchange: HttpExchange): Map<String, String> {
            val params = LinkedHashMap<String, String>()
            fun addQuery(query: String?) {
                query?.split("&")?.forEach { pair ->
                    if (pair.isEmpty()) return@forEach
                    val i: Int = pair.indexOf('=')
                    val k: String =
                        URLDecoder.decode(
                            if (i < 0) pair else pair.substring(0, i),
                            StandardCharsets.UTF_8
                        )
                    val v: String =
                        if (i < 0) ""
                        else URLDecoder.decode(pair.substring(i + 1), StandardCharsets.UTF_8)
                    params[k] = v
                }
            }
            addQuery(exchange.requestURI.rawQuery)
            if (exchange.requestMethod == "POST") {
                val body: String = exchange.requestBody.readBytes().toString(StandardCharsets.UTF_8)
                val contentType: String = exchange.requestHeaders.getFirst("Content-Type") ?: ""
                if (contentType.contains("json") && body.isNotBlank()) {
                    Jsons.readTree(body).properties().forEach { (k, v) ->
                        params[k] = if (v.isTextual) v.asText() else v.toString()
                    }
                } else {
                    addQuery(body)
                }
            }
            return params
        }

        /**
         * Standalone entry point for the Docker harness: `FakeSlackServer <port> <workspace.json>`
         * (or `generate:<channels>:<messagesPerChannel>` instead of a file) with optional
         * `--rate-limit method=perMinute` pairs and `--non-marketplace`.
         */
        @JvmStatic
        fun main(args: Array<String>) {
            val port: Int = args.getOrNull(0)?.toIntOrNull() ?: 8080
            val source: String = args.getOrNull(1) ?: "generate:5:200"
            val workspace: FakeSlackWorkspace =
                if (source.startsWith("generate:")) {
                    val parts: List<String> = source.removePrefix("generate:").split(":")
                    FakeSlackData.generate(
                        channels = parts.getOrNull(0)?.toIntOrNull() ?: 5,
                        messagesPerChannel = parts.getOrNull(1)?.toIntOrNull() ?: 200,
                    )
                } else {
                    FakeSlackWorkspace.load(File(source))
                }
            val rateLimits = HashMap<String, Double>()
            var nonMarketplace = false
            var i = 2
            while (i < args.size) {
                when (args[i]) {
                    "--rate-limit" -> {
                        val (m, r) = args[i + 1].split("=")
                        rateLimits[m] = r.toDouble()
                        i++
                    }
                    "--non-marketplace" -> nonMarketplace = true
                }
                i++
            }
            val server = FakeSlackServer(workspace, port, rateLimits, nonMarketplace).start()
            println(
                "Fake Slack API listening on ${server.baseUrl} with ${workspace.channels.size} channel(s), ${workspace.users.size} user(s), ${workspace.messageCount()} message(s); tokens: ${workspace.validTokens}"
            )
            Thread.currentThread().join()
        }
    }
}

/**
 * The data behind [FakeSlackServer]: raw user and channel objects, the bot's memberships, and every
 * message per channel (top-level messages and replies alike, replies carrying a `thread_ts`
 * different from their `ts`). Thread metadata on parents (`reply_count`, `reply_users`,
 * `reply_users_count`, `latest_reply`) is derived from the replies.
 *
 * File format (`load`): `{"team": {...}, "bot_user_id": "U...", "tokens": ["xoxb-..."], "users":
 * [...], "channels": [{..., "members": ["U..."]}], "messages": {"C...": [...]}}`.
 */
class FakeSlackWorkspace(
    val team: ObjectNode,
    val botUserId: String,
    val validTokens: Set<String>,
    val users: List<ObjectNode>,
    val channels: MutableList<ObjectNode>,
    /** Channel id to member user ids. */
    val members: MutableMap<String, MutableList<String>>,
    /** Channel id to messages, any order. */
    messages: Map<String, List<ObjectNode>>,
) {
    /** Channel id to messages sorted by ts ascending, with thread metadata derived. */
    val messages: Map<String, List<ObjectNode>> =
        messages.mapValues { (_, list) -> withThreadMetadata(list) }

    fun messageCount(): Int = messages.values.sumOf { it.size }

    private fun channel(id: String?): ObjectNode? =
        channels.firstOrNull { it.get("id").asText() == id }

    private fun isBotMember(channelId: String): Boolean =
        members[channelId]?.contains(botUserId) == true

    fun authTest(): ObjectNode =
        Jsons.objectNode().apply {
            put("ok", true)
            put("url", "https://${team.get("domain")?.asText() ?: "fake"}.slack.com/")
            put("team", team.get("name")?.asText() ?: "Fake")
            put("user", "airbyte")
            put("team_id", team.get("id")?.asText() ?: "T000")
            put("user_id", botUserId)
            put("bot_id", "B000FAKE")
            put("is_enterprise_install", false)
        }

    fun usersList(params: Map<String, String>): ObjectNode =
        page(users, params, 999, "members").apply { put("cache_ts", 1700000000) }

    fun conversationsList(params: Map<String, String>): ObjectNode {
        val types: Set<String> =
            (params["types"] ?: "public_channel").split(",").map { it.trim() }.toSet()
        val excludeArchived: Boolean = params["exclude_archived"]?.lowercase() in setOf("true", "1")
        val listed: List<ObjectNode> =
            channels
                .filter { c ->
                    val private: Boolean = c.get("is_private")?.asBoolean() ?: false
                    (private && "private_channel" in types) ||
                        (!private && "public_channel" in types)
                }
                .filter { c -> !(excludeArchived && (c.get("is_archived")?.asBoolean() ?: false)) }
                // Private channels are only listed when the bot is a member, as in Slack.
                .filter { c ->
                    !(c.get("is_private")?.asBoolean() ?: false) ||
                        isBotMember(c.get("id").asText())
                }
                .map { c -> channelView(c) }
        return page(listed, params, 999, "channels")
    }

    /** The channel as Slack lists it: `is_member` and `num_members` from the memberships. */
    private fun channelView(c: ObjectNode): ObjectNode {
        val id: String = c.get("id").asText()
        return c.deepCopy().apply {
            remove("members")
            put("is_member", isBotMember(id))
            put("num_members", members[id]?.size ?: 0)
        }
    }

    fun conversationsInfo(params: Map<String, String>): ObjectNode {
        val c: ObjectNode =
            channel(params["channel"]) ?: return FakeSlackServer.err("channel_not_found")
        return Jsons.objectNode().put("ok", true).apply { set<JsonNode>("channel", channelView(c)) }
    }

    fun conversationsMembers(params: Map<String, String>): ObjectNode {
        val id: String = params["channel"] ?: return FakeSlackServer.err("channel_not_found")
        channel(id) ?: return FakeSlackServer.err("channel_not_found")
        val ids: List<JsonNode> = (members[id] ?: emptyList()).map { Jsons.textNode(it) }
        return page(ids, params, 999, "members")
    }

    fun conversationsJoin(params: Map<String, String>): ObjectNode {
        val c: ObjectNode =
            channel(params["channel"]) ?: return FakeSlackServer.err("channel_not_found")
        val id: String = c.get("id").asText()
        if (c.get("is_archived")?.asBoolean() == true) return FakeSlackServer.err("is_archived")
        if (c.get("is_private")?.asBoolean() == true)
            return FakeSlackServer.err("method_not_supported_for_channel_type")
        val list: MutableList<String> = members.computeIfAbsent(id) { ArrayList() }
        val already: Boolean = botUserId in list
        if (!already) list.add(botUserId)
        return Jsons.objectNode().apply {
            put("ok", true)
            set<JsonNode>("channel", channelView(c))
            if (already) {
                put("warning", "already_in_channel")
                set<JsonNode>(
                    "response_metadata",
                    Jsons.objectNode().apply {
                        set<JsonNode>("warnings", Jsons.arrayNode().add("already_in_channel"))
                    }
                )
            }
        }
    }

    fun conversationsHistory(params: Map<String, String>, nonMarketplace: Boolean): ObjectNode {
        val id: String = params["channel"] ?: return FakeSlackServer.err("channel_not_found")
        channel(id) ?: return FakeSlackServer.err("channel_not_found")
        if (!isBotMember(id)) return FakeSlackServer.err("not_in_channel")
        val all: List<ObjectNode> = messages[id] ?: emptyList()
        val topLevel: List<ObjectNode> =
            all.filter { m ->
                val ts: String = m.get("ts").asText()
                val threadTs: String? = m.get("thread_ts")?.asText()
                threadTs == null ||
                    threadTs == ts ||
                    m.get("subtype")?.asText() == "thread_broadcast"
            }
        val oldest: Double? = params["oldest"]?.toDoubleOrNull()
        val latest: Double? = params["latest"]?.toDoubleOrNull()
        val inclusive: Boolean = params["inclusive"]?.lowercase() in setOf("true", "1")
        val inRange: List<ObjectNode> =
            topLevel
                .filter { m ->
                    val ts: Double = m.get("ts").asText().toDouble()
                    (oldest == null || (if (inclusive) ts >= oldest else ts > oldest)) &&
                        (latest == null || (if (inclusive) ts <= latest else ts < latest))
                }
                .sortedByDescending { it.get("ts").asText().toDouble() }
        val maxLimit: Int = if (nonMarketplace) 15 else 999
        return page(
                inRange,
                params,
                maxLimit,
                "messages",
                defaultLimit = if (nonMarketplace) 15 else 100
            )
            .apply {
                put("pin_count", 0)
                put(
                    "has_more",
                    get("response_metadata")?.get("next_cursor")?.asText()?.isNotEmpty() ?: false
                )
            }
    }

    fun conversationsReplies(params: Map<String, String>, nonMarketplace: Boolean): ObjectNode {
        val id: String = params["channel"] ?: return FakeSlackServer.err("channel_not_found")
        channel(id) ?: return FakeSlackServer.err("channel_not_found")
        if (!isBotMember(id)) return FakeSlackServer.err("not_in_channel")
        val ts: String = params["ts"] ?: return FakeSlackServer.err("thread_not_found")
        val all: List<ObjectNode> = messages[id] ?: emptyList()
        val referenced: ObjectNode =
            all.firstOrNull { it.get("ts").asText() == ts }
                ?: return FakeSlackServer.err("thread_not_found")
        // `ts` may be the parent or any message of the thread.
        val parentTs: String = referenced.get("thread_ts")?.asText() ?: ts
        val thread: List<ObjectNode> =
            all.filter { m ->
                    m.get("ts").asText() == parentTs || m.get("thread_ts")?.asText() == parentTs
                }
                .sortedBy { it.get("ts").asText().toDouble() }
        val oldest: Double? = params["oldest"]?.toDoubleOrNull()
        val latest: Double? = params["latest"]?.toDoubleOrNull()
        val inclusive: Boolean = params["inclusive"]?.lowercase() in setOf("true", "1")
        val inRange: List<ObjectNode> =
            thread.filter { m ->
                val t: Double = m.get("ts").asText().toDouble()
                (oldest == null || (if (inclusive) t >= oldest else t > oldest)) &&
                    (latest == null || (if (inclusive) t <= latest else t < latest))
            }
        val maxLimit: Int = if (nonMarketplace) 15 else 1000
        return page(
                inRange,
                params,
                maxLimit,
                "messages",
                defaultLimit = if (nonMarketplace) 15 else 1000
            )
            .apply {
                put(
                    "has_more",
                    get("response_metadata")?.get("next_cursor")?.asText()?.isNotEmpty() ?: false
                )
            }
    }

    /** One page of [items] under [key], honouring `limit` and an opaque offset `cursor`. */
    private fun <T : JsonNode> page(
        items: List<T>,
        params: Map<String, String>,
        maxLimit: Int,
        key: String,
        defaultLimit: Int = 100,
    ): ObjectNode {
        val limit: Int = (params["limit"]?.toIntOrNull() ?: defaultLimit).coerceIn(1, maxLimit)
        val offset: Int = params["cursor"]?.let { decodeCursor(it) } ?: 0
        if (offset < 0 || offset > items.size) return FakeSlackServer.err("invalid_cursor")
        val end: Int = minOf(items.size, offset + limit)
        val array: ArrayNode = Jsons.arrayNode()
        items.subList(offset, end).forEach { array.add(it) }
        val next: String = if (end < items.size) encodeCursor(end) else ""
        return Jsons.objectNode().apply {
            put("ok", true)
            set<JsonNode>(key, array)
            set<JsonNode>("response_metadata", Jsons.objectNode().put("next_cursor", next))
        }
    }

    companion object {
        private fun encodeCursor(offset: Int): String =
            Base64.getEncoder().encodeToString("offset:$offset".toByteArray(StandardCharsets.UTF_8))

        private fun decodeCursor(cursor: String): Int? =
            try {
                String(Base64.getDecoder().decode(cursor), StandardCharsets.UTF_8)
                    .removePrefix("offset:")
                    .toInt()
            } catch (_: Exception) {
                -1
            }

        /** Sorts by ts and derives the parents' thread metadata from the replies. */
        fun withThreadMetadata(list: List<ObjectNode>): List<ObjectNode> {
            val sorted: List<ObjectNode> =
                list.map { it.deepCopy() }.sortedBy { it.get("ts").asText().toDouble() }
            val byTs: Map<String, ObjectNode> = sorted.associateBy { it.get("ts").asText() }
            val replies: Map<String, List<ObjectNode>> =
                sorted
                    .filter { m ->
                        m.get("thread_ts")?.asText()?.let { it != m.get("ts").asText() } == true
                    }
                    .groupBy { it.get("thread_ts").asText() }
            for ((parentTs: String, replyList: List<ObjectNode>) in replies) {
                val parent: ObjectNode = byTs[parentTs] ?: continue
                val users: List<String> =
                    replyList.mapNotNull { it.get("user")?.asText() }.distinct()
                parent.put("thread_ts", parentTs)
                parent.put("reply_count", replyList.size)
                parent.put("reply_users_count", users.size)
                parent.put("latest_reply", replyList.last().get("ts").asText())
                parent.set<JsonNode>(
                    "reply_users",
                    Jsons.arrayNode().apply { users.take(5).forEach { add(it) } }
                )
                parent.put("subscribed", false)
                for (reply in replyList) {
                    reply.put("parent_user_id", parent.get("user")?.asText() ?: "")
                }
            }
            return sorted
        }

        fun load(file: File): FakeSlackWorkspace = fromJson(Jsons.readTree(file) as ObjectNode)

        fun fromJson(root: ObjectNode): FakeSlackWorkspace {
            val channels: MutableList<ObjectNode> =
                root.get("channels").map { it as ObjectNode }.toMutableList()
            val members: MutableMap<String, MutableList<String>> =
                channels
                    .associate { c ->
                        c.get("id").asText() to
                            (c.get("members")?.map { it.asText() }?.toMutableList() ?: ArrayList())
                    }
                    .toMutableMap()
            return FakeSlackWorkspace(
                team = root.get("team") as? ObjectNode
                        ?: Jsons.objectNode()
                            .put("id", "T0FAKE")
                            .put("name", "Fake")
                            .put("domain", "fake"),
                botUserId = root.get("bot_user_id")?.asText() ?: "UBOT",
                validTokens = root.get("tokens")?.map { it.asText() }?.toSet()
                        ?: setOf("xoxb-fake"),
                users = root.get("users").map { it as ObjectNode },
                channels = channels,
                members = members,
                messages =
                    root.get("messages")?.properties()?.associate { (k, v) ->
                        k to v.map { it as ObjectNode }
                    }
                        ?: emptyMap(),
            )
        }
    }

    fun toJson(): ObjectNode =
        Jsons.objectNode().apply {
            set<JsonNode>("team", team)
            put("bot_user_id", botUserId)
            set<JsonNode>("tokens", Jsons.arrayNode().apply { validTokens.forEach { add(it) } })
            set<JsonNode>("users", Jsons.arrayNode().apply { users.forEach { add(it) } })
            set<JsonNode>(
                "channels",
                Jsons.arrayNode().apply {
                    channels.forEach { c ->
                        add(
                            c.deepCopy().apply {
                                set<JsonNode>(
                                    "members",
                                    Jsons.arrayNode().apply {
                                        members[c.get("id").asText()]?.forEach { add(it) }
                                    }
                                )
                            }
                        )
                    }
                },
            )
            set<JsonNode>(
                "messages",
                Jsons.objectNode().apply {
                    messages.forEach { (id, list) ->
                        set<JsonNode>(id, Jsons.arrayNode().apply { list.forEach { add(it) } })
                    }
                },
            )
        }
}
