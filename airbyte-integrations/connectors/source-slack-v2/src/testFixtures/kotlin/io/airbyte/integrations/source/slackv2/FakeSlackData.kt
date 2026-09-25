/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.util.Jsons
import kotlin.random.Random

/**
 * Deterministic synthetic Slack workspaces for the fake server: realistic user, channel and message
 * shapes (profiles, topic/purpose, `blocks`, `attachments`, `reactions`, `files`, `edited`,
 * `bot_message` / `channel_join` / `thread_broadcast` subtypes, threads with replies), sized by
 * parameters so that the same generator serves unit tests and scale runs.
 */
object FakeSlackData {
    const val TEAM_ID = "T0FAKE0001"
    const val BOT_USER_ID = "U0FAKEBOT"
    const val TOKEN = "xoxb-fake-token"
    const val OAUTH_TOKEN = "xoxe-fake-oauth-token"

    /**
     * Midnight UTC 40 days ago: the first message of every generated workspace. Relative to the
     * clock so that lookback windows (at most 365 days) can always reach the messages; the tests
     * compute their expectations from the workspace, never from fixed timestamps.
     */
    val EPOCH_START: Long = (java.time.Instant.now().epochSecond / 86400 - 40) * 86400
    /** Messages span 30 days. */
    const val SPAN_SECONDS: Long = 30L * 24 * 3600

    val GENERAL_ID = "C0FAKEGENERAL"
    val RANDOM_ID = "C0FAKERANDOM"
    /** Public, bot is not a member: joined when `join_channels` is set, skipped otherwise. */
    val UNJOINED_ID = "C0FAKEUNJOINED"
    /** Private, bot is a member: listed only with `include_private_channels`. */
    val PRIVATE_ID = "G0FAKEPRIVATE"
    /** Archived, bot is a member: listed only with `include_archived_channels`. */
    val ARCHIVED_ID = "C0FAKEARCHIVED"
    /** Bot is a member, no messages. */
    val EMPTY_ID = "C0FAKEEMPTY"

    /**
     * The standard workspace of the tests: six fixed channels ([GENERAL_ID] with
     * [messagesPerChannel] messages, [RANDOM_ID], [UNJOINED_ID], [PRIVATE_ID], [ARCHIVED_ID] with
     * fewer, [EMPTY_ID] with none) plus `channels - 6` generated public channels the bot is in.
     */
    fun generate(
        channels: Int = 6,
        messagesPerChannel: Int = 200,
        users: Int = 25,
        threadRatio: Double = 0.3,
        maxReplies: Int = 5,
        seed: Long = 42L,
    ): FakeSlackWorkspace {
        val random = Random(seed)
        // `+ botUser()` would pick `plus(Iterable)`: an ObjectNode is an Iterable<JsonNode>.
        val userList: List<ObjectNode> = (1..users).map { user(it, random) } + listOf(botUser())
        val userIds: List<String> =
            userList.map { it.get("id").asText() }.filter { it != BOT_USER_ID }
        val channelList = ArrayList<ObjectNode>()
        val members = HashMap<String, MutableList<String>>()
        val messages = HashMap<String, List<ObjectNode>>()

        fun add(channel: ObjectNode, memberIds: List<String>, count: Int) {
            val id: String = channel.get("id").asText()
            channelList.add(channel)
            members[id] = memberIds.toMutableList()
            messages[id] =
                if (count == 0) emptyList()
                else
                    messages(
                        count,
                        memberIds.filter { it != BOT_USER_ID },
                        threadRatio,
                        maxReplies,
                        random
                    )
        }
        add(
            channel(GENERAL_ID, "general", isGeneral = true, created = EPOCH_START - 86400 * 400),
            userIds + BOT_USER_ID,
            messagesPerChannel
        )
        add(
            channel(RANDOM_ID, "random", created = EPOCH_START - 86400 * 399),
            userIds.take(10) + BOT_USER_ID,
            maxOf(1, messagesPerChannel / 4)
        )
        add(
            channel(UNJOINED_ID, "unjoined", created = EPOCH_START - 86400 * 30),
            userIds.take(5),
            maxOf(1, messagesPerChannel / 10)
        )
        add(
            channel(
                PRIVATE_ID,
                "secret-plans",
                isPrivate = true,
                created = EPOCH_START - 86400 * 20
            ),
            userIds.take(3) + BOT_USER_ID,
            maxOf(1, messagesPerChannel / 10)
        )
        add(
            channel(
                ARCHIVED_ID,
                "old-project",
                isArchived = true,
                created = EPOCH_START - 86400 * 500
            ),
            userIds.take(4) + BOT_USER_ID,
            maxOf(1, messagesPerChannel / 20)
        )
        add(
            channel(EMPTY_ID, "empty", created = EPOCH_START - 86400 * 2),
            userIds.take(2) + BOT_USER_ID,
            0
        )
        for (i in 7..channels) {
            val id = "C0FAKE%06d".format(i)
            add(
                channel(id, "team-%03d".format(i), created = EPOCH_START - 86400L * i),
                userIds.shuffled(random).take(1 + random.nextInt(userIds.size)) + BOT_USER_ID,
                messagesPerChannel
            )
        }
        return FakeSlackWorkspace(
            team =
                Jsons.objectNode()
                    .put("id", TEAM_ID)
                    .put("name", "Fake Workspace")
                    .put("domain", "fake-workspace"),
            botUserId = BOT_USER_ID,
            validTokens = setOf(TOKEN, OAUTH_TOKEN),
            users = userList,
            channels = channelList,
            members = members,
            messages = messages,
        )
    }

    fun user(i: Int, random: Random): ObjectNode {
        val id = "U0FAKE%06d".format(i)
        val first: String = FIRST_NAMES[random.nextInt(FIRST_NAMES.size)]
        val last: String = LAST_NAMES[random.nextInt(LAST_NAMES.size)]
        val name: String = "${first.lowercase()}.${last.lowercase()}$i"
        return Jsons.objectNode().apply {
            put("id", id)
            put("team_id", TEAM_ID)
            put("name", name)
            put("deleted", i % 17 == 0)
            put("color", "%06x".format(random.nextInt(0xFFFFFF)))
            put("real_name", "$first $last")
            put("tz", TIMEZONES[random.nextInt(TIMEZONES.size)].first)
            put("tz_label", TIMEZONES[random.nextInt(TIMEZONES.size)].second)
            put("tz_offset", TIMEZONES[random.nextInt(TIMEZONES.size)].third)
            set<JsonNode>(
                "profile",
                Jsons.objectNode().apply {
                    put("title", if (i % 3 == 0) "Engineer" else "")
                    put("phone", "")
                    put("skype", "")
                    put("real_name", "$first $last")
                    put("real_name_normalized", "$first $last")
                    put("display_name", name)
                    put("display_name_normalized", name)
                    set<JsonNode>(
                        "fields",
                        if (i % 5 == 0)
                            Jsons.objectNode().apply {
                                set<JsonNode>(
                                    "Xf01",
                                    Jsons.objectNode().put("value", "42").put("alt", "")
                                )
                            }
                        else Jsons.nullNode()
                    )
                    put("status_text", if (i % 4 == 0) "Out of office" else "")
                    put("status_emoji", if (i % 4 == 0) ":palm_tree:" else "")
                    set<JsonNode>("status_emoji_display_info", Jsons.arrayNode())
                    put("status_expiration", 0)
                    put("avatar_hash", "g%015x".format(random.nextLong(0, Long.MAX_VALUE)))
                    put("email", "$name@example.com")
                    put("first_name", first)
                    put("last_name", last)
                    for (size in listOf(24, 32, 48, 72, 192, 512)) put(
                        "image_$size",
                        "https://secure.gravatar.com/avatar/$id.jpg?s=$size"
                    )
                    put("status_text_canonical", "")
                    put("team", TEAM_ID)
                },
            )
            put("is_admin", i == 1)
            put("is_owner", i == 1)
            put("is_primary_owner", i == 1)
            put("is_restricted", i % 11 == 0)
            put("is_ultra_restricted", false)
            put("is_bot", false)
            put("is_app_user", false)
            put("updated", EPOCH_START - random.nextLong(0, 86400L * 365))
            put("is_email_confirmed", true)
            put("who_can_share_contact_card", "EVERYONE")
            put("has_2fa", i % 2 == 0)
        }
    }

    private fun botUser(): ObjectNode =
        Jsons.objectNode().apply {
            put("id", BOT_USER_ID)
            put("team_id", TEAM_ID)
            put("name", "airbyte")
            put("deleted", false)
            put("color", "4bbe2e")
            put("real_name", "Airbyte")
            put("tz", "America/Los_Angeles")
            put("tz_label", "Pacific Daylight Time")
            put("tz_offset", -25200)
            set<JsonNode>(
                "profile",
                Jsons.objectNode().apply {
                    put("real_name", "Airbyte")
                    put("display_name", "")
                    put("bot_id", "B000FAKE")
                    put("api_app_id", "A000FAKE")
                    put("team", TEAM_ID)
                }
            )
            put("is_admin", false)
            put("is_owner", false)
            put("is_primary_owner", false)
            put("is_restricted", false)
            put("is_ultra_restricted", false)
            put("is_bot", true)
            put("is_app_user", false)
            put("updated", EPOCH_START)
            put("is_email_confirmed", false)
            put("who_can_share_contact_card", "EVERYONE")
        }

    fun channel(
        id: String,
        name: String,
        isPrivate: Boolean = false,
        isArchived: Boolean = false,
        isGeneral: Boolean = false,
        created: Long,
    ): ObjectNode =
        Jsons.objectNode().apply {
            put("id", id)
            put("name", name)
            put("is_channel", !isPrivate)
            put("is_group", isPrivate)
            put("is_im", false)
            put("is_mpim", false)
            put("is_private", isPrivate)
            put("created", created)
            put("is_archived", isArchived)
            put("is_general", isGeneral)
            put("unlinked", 0)
            put("name_normalized", name)
            put("is_shared", false)
            put("is_org_shared", false)
            put("is_pending_ext_shared", false)
            set<JsonNode>("pending_shared", Jsons.arrayNode())
            put("context_team_id", TEAM_ID)
            put("updated", created * 1000 + 123)
            set<JsonNode>("parent_conversation", Jsons.nullNode())
            put("creator", "U0FAKE000001")
            put("is_ext_shared", false)
            set<JsonNode>("shared_team_ids", Jsons.arrayNode().add(TEAM_ID))
            set<JsonNode>("pending_connected_team_ids", Jsons.arrayNode())
            set<JsonNode>(
                "topic",
                Jsons.objectNode()
                    .put("value", if (isGeneral) "Company-wide announcements" else "")
                    .put("creator", if (isGeneral) "U0FAKE000001" else "")
                    .put("last_set", if (isGeneral) created + 60 else 0)
            )
            set<JsonNode>(
                "purpose",
                Jsons.objectNode()
                    .put("value", "Talk about $name")
                    .put("creator", "U0FAKE000001")
                    .put("last_set", created + 30)
            )
            set<JsonNode>("previous_names", Jsons.arrayNode())
        }

    /** [count] top-level messages spread over the span, a share of them threads with replies. */
    fun messages(
        count: Int,
        userIds: List<String>,
        threadRatio: Double,
        maxReplies: Int,
        random: Random,
    ): List<ObjectNode> {
        val result = ArrayList<ObjectNode>()
        var seconds: Double = EPOCH_START.toDouble()
        val step: Double = SPAN_SECONDS.toDouble() / (count + 1)
        var micro = 0
        for (i in 0 until count) {
            seconds += step * (0.5 + random.nextDouble())
            micro = (micro + 1 + random.nextInt(1000)) % 1_000_000
            val ts: String = ts(seconds, micro)
            val user: String = userIds[random.nextInt(userIds.size)]
            val message: ObjectNode =
                when {
                    i == 0 -> channelJoin(ts, user)
                    i % 23 == 0 -> botMessage(ts, i)
                    else -> textMessage(ts, user, i, random)
                }
            result.add(message)
            if (message.get("subtype") == null && random.nextDouble() < threadRatio) {
                val replies: Int = 1 + random.nextInt(maxReplies)
                var replySeconds: Double = seconds
                for (r in 1..replies) {
                    replySeconds += 1 + random.nextInt(3 * 24 * 3600)
                    micro = (micro + 7) % 1_000_000
                    val replyUser: String = userIds[random.nextInt(userIds.size)]
                    val reply: ObjectNode =
                        textMessage(ts(replySeconds, micro), replyUser, i * 100 + r, random)
                    reply.put("thread_ts", ts)
                    if (r == replies && random.nextDouble() < 0.2) {
                        reply.put("subtype", "thread_broadcast")
                        reply.set<JsonNode>("root", message.deepCopy())
                    }
                    result.add(reply)
                }
            }
        }
        return result
    }

    private fun ts(seconds: Double, micro: Int): String = "%d.%06d".format(seconds.toLong(), micro)

    private fun textMessage(ts: String, user: String, i: Int, random: Random): ObjectNode {
        val text: String = TEXTS[random.nextInt(TEXTS.size)].replace("{i}", i.toString())
        return Jsons.objectNode().apply {
            put("user", user)
            put("type", "message")
            put("ts", ts)
            put(
                "client_msg_id",
                "%08x-%04x-%04x-%04x-%012x".format(
                    random.nextInt(),
                    random.nextInt(0xFFFF),
                    random.nextInt(0xFFFF),
                    random.nextInt(0xFFFF),
                    random.nextLong(0, 1L shl 48)
                )
            )
            put("text", text)
            put("team", TEAM_ID)
            set<JsonNode>(
                "blocks",
                Jsons.arrayNode()
                    .add(
                        Jsons.objectNode().apply {
                            put("type", "rich_text")
                            put("block_id", "b%03d".format(random.nextInt(1000)))
                            set<JsonNode>(
                                "elements",
                                Jsons.arrayNode()
                                    .add(
                                        Jsons.objectNode().apply {
                                            put("type", "rich_text_section")
                                            set<JsonNode>(
                                                "elements",
                                                Jsons.arrayNode()
                                                    .add(
                                                        Jsons.objectNode()
                                                            .put("type", "text")
                                                            .put("text", text)
                                                    )
                                            )
                                        },
                                    ),
                            )
                        },
                    ),
            )
            if (i % 7 == 0) {
                set<JsonNode>(
                    "reactions",
                    Jsons.arrayNode()
                        .add(
                            Jsons.objectNode().put("name", "thumbsup").put("count", 2).apply {
                                set<JsonNode>(
                                    "users",
                                    Jsons.arrayNode().add("U0FAKE000001").add("U0FAKE000002")
                                )
                            }
                        ),
                )
            }
            if (i % 13 == 0) {
                set<JsonNode>(
                    "edited",
                    Jsons.objectNode()
                        .put("user", user)
                        .put("ts", ts.substringBefore('.') + ".000000")
                )
            }
            if (i % 19 == 0) {
                set<JsonNode>(
                    "attachments",
                    Jsons.arrayNode()
                        .add(
                            Jsons.objectNode()
                                .put("id", 1)
                                .put("color", "36a64f")
                                .put("fallback", "Build #$i passed")
                                .put("title", "Build #$i")
                                .put("title_link", "https://ci.example.com/builds/$i")
                        ),
                )
            }
            if (i % 29 == 0) {
                put("upload", false)
                set<JsonNode>(
                    "files",
                    Jsons.arrayNode()
                        .add(
                            Jsons.objectNode()
                                .put("id", "F0FAKE%06d".format(i))
                                .put("name", "report-$i.pdf")
                                .put("title", "Report $i")
                                .put("mimetype", "application/pdf")
                                .put("filetype", "pdf")
                                .put("size", 1024 * i)
                                .put(
                                    "url_private",
                                    "https://files.slack.com/files-pri/$TEAM_ID-F0FAKE%06d/report-$i.pdf".format(
                                        i
                                    )
                                )
                        ),
                )
            }
        }
    }

    private fun botMessage(ts: String, i: Int): ObjectNode =
        Jsons.objectNode().apply {
            put("type", "message")
            put("subtype", "bot_message")
            put("ts", ts)
            put("bot_id", "B0FAKECI")
            put("username", "ci-bot")
            put("text", "Deployment $i finished")
            set<JsonNode>("icons", Jsons.objectNode().put("emoji", ":rocket:"))
            set<JsonNode>(
                "bot_profile",
                Jsons.objectNode()
                    .put("id", "B0FAKECI")
                    .put("deleted", false)
                    .put("name", "CI")
                    .put("updated", EPOCH_START)
                    .put("app_id", "A0FAKECI")
                    .put("team_id", TEAM_ID)
            )
        }

    private fun channelJoin(ts: String, user: String): ObjectNode =
        Jsons.objectNode().apply {
            put("type", "message")
            put("subtype", "channel_join")
            put("ts", ts)
            put("user", user)
            put("text", "<@$user> has joined the channel")
        }

    private val FIRST_NAMES =
        listOf(
            "Ada",
            "Grace",
            "Linus",
            "Margaret",
            "Dennis",
            "Barbara",
            "Ken",
            "Radia",
            "Guido",
            "Anders",
            "Yukihiro",
            "Bjarne"
        )
    private val LAST_NAMES =
        listOf(
            "Lovelace",
            "Hopper",
            "Torvalds",
            "Hamilton",
            "Ritchie",
            "Liskov",
            "Thompson",
            "Perlman",
            "Rossum",
            "Hejlsberg",
            "Matsumoto",
            "Stroustrup"
        )
    private val TIMEZONES =
        listOf(
            Triple("America/Los_Angeles", "Pacific Daylight Time", -25200),
            Triple("Europe/Berlin", "Central European Summer Time", 7200),
            Triple("Asia/Tokyo", "Japan Standard Time", 32400),
            Triple("America/New_York", "Eastern Daylight Time", -14400)
        )
    private val TEXTS =
        listOf(
            "Good morning team, standup in 5 minutes",
            "Deployed build {i} to staging :rocket:",
            "Can someone review PR #{i}? It touches the sync scheduler",
            "Reminder: the retro is moved to Thursday",
            "I'm seeing timeouts on the warehouse loader, anyone else?",
            "Lunch? :pizza:",
            "Merged {i}, thanks for the reviews everyone",
            "The dashboard numbers look off since yesterday's release",
            "FYI the API rate limit doc changed again: https://docs.slack.dev/apis/web-api/rate-limits/",
            "Posting the notes from today's design review in the thread",
            "Unicode check: naïve café 日本語 🚀 \"quotes\" <tags> & ampersands",
        )
}
