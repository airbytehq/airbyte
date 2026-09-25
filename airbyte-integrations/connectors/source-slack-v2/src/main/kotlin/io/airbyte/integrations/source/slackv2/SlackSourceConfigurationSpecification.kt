/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonPropertyOrder
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.command.ConfigurationSpecification
import jakarta.inject.Singleton

/**
 * The object which is mapped to the Slack source configuration JSON.
 *
 * Every property of the legacy `source-slack` (3.2.x) spec is kept with its name, type, default and
 * wording, so that a saved legacy configuration loads unchanged: `start_date`, `lookback_window`,
 * `join_channels`, `include_private_channels`, `include_archived_channels`, `channel_filter`,
 * `threads_ignore_no_replies`, `credentials` (OAuth or bot token, discriminated by `option_title`),
 * `num_workers` and `channel_messages_window_size`. The two standard Bulk CDK tuning properties
 * (`concurrency`, `checkpoint_target_interval_seconds`) are new. Use [SlackSourceConfiguration]
 * instead wherever possible.
 */
@JsonSchemaTitle("Slack Spec")
@JsonPropertyOrder(
    value =
        [
            "start_date",
            "lookback_window",
            "join_channels",
            "include_private_channels",
            "include_archived_channels",
            "channel_filter",
            "threads_ignore_no_replies",
            "credentials",
            "num_workers",
            "channel_messages_window_size",
            "concurrency",
            "checkpoint_target_interval_seconds",
        ],
)
@Singleton
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class SlackSourceConfigurationSpecification : ConfigurationSpecification() {

    @JsonProperty("start_date")
    @JsonSchemaTitle("Start Date")
    @JsonSchemaDescription(
        "UTC date and time in the format 2017-01-25T00:00:00Z. Any data before this date will not be replicated.",
    )
    @JsonSchemaInject(
        json =
            """{"pattern":"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$","examples":["2017-01-25T00:00:00Z"],"format":"date-time"}""",
    )
    lateinit var startDate: String

    /** Null when the (required) `start_date` property is absent from the config JSON. */
    fun startDateOrNull(): String? = if (this::startDate.isInitialized) startDate else null

    @JsonProperty("lookback_window")
    @JsonSchemaTitle("Threads Lookback window (Days)")
    @JsonSchemaDescription(
        "How far into the past to look for messages in threads, default is 0 days"
    )
    @JsonSchemaInject(json = """{"examples":[7,14],"minimum":0,"default":0,"maximum":365}""")
    var lookbackWindow: Int = DEFAULT_LOOKBACK_WINDOW_DAYS

    @JsonProperty("join_channels")
    @JsonSchemaTitle("Join all channels")
    @JsonSchemaDescription(
        "Whether to join all channels or to sync data only from channels the bot is already in.  If false, you''ll need to manually add the bot to all the channels from which you''d like to sync messages.",
    )
    @JsonSchemaInject(json = """{"default":true}""")
    var joinChannels: Boolean = true

    @JsonProperty("include_private_channels")
    @JsonSchemaTitle("Include private channels")
    @JsonSchemaDescription(
        "Whether to read information from private channels that the bot is already in.  If false, only public channels will be read.  If true, the bot must be manually added to private channels.",
    )
    @JsonSchemaInject(json = """{"default":false}""")
    var includePrivateChannels: Boolean? = null

    @JsonProperty("include_archived_channels")
    @JsonSchemaTitle("Include archived channels")
    @JsonSchemaDescription(
        "Whether to include archived channels in the sync. When disabled (default), archived channels are excluded from the Slack API response, reducing the number of API calls for downstream streams such as channel_messages, threads, and channel_members. Enable this option if you need to sync data from archived channels.",
    )
    @JsonSchemaInject(json = """{"default":false}""")
    var includeArchivedChannels: Boolean? = null

    @JsonProperty("channel_filter")
    @JsonSchemaTitle("Channel name filter")
    @JsonSchemaDescription(
        "A channel name list (without leading '#' char) which limit the channels from which you'd like to sync. Empty list means no filter.",
    )
    @JsonSchemaInject(
        json =
            """{"default":[],"items":{"type":"string","minLength":0},"examples":["channel_one","channel_two"]}""",
    )
    var channelFilter: List<String>? = null

    @JsonProperty("threads_ignore_no_replies")
    @JsonSchemaTitle("Ignore messages with no replies in threads stream")
    @JsonSchemaDescription(
        "When enabled, the threads stream will skip messages that have no replies (reply_count is 0, null, or absent), reducing the number of API calls. Disabled by default to make Threads stream contain unthreaded messages in its records.",
    )
    @JsonSchemaInject(json = """{"default":false}""")
    var threadsIgnoreNoReplies: Boolean? = null

    @JsonProperty("credentials")
    @JsonSchemaTitle("Authentication mechanism")
    @JsonSchemaDescription("Choose how to authenticate into Slack")
    var credentials: CredentialsSpecification? = null

    @JsonProperty("num_workers")
    @JsonSchemaTitle("Number of concurrent threads")
    @JsonSchemaDescription("The number of worker threads to use for the sync.")
    @JsonSchemaInject(
        json = """{"minimum":2,"maximum":10,"default":2,"examples":[2,3],"order":7}""",
    )
    var numWorkers: Int? = null

    @JsonProperty("channel_messages_window_size")
    @JsonSchemaTitle("Channel messages date window size (in days)")
    @JsonSchemaDescription(
        "The size (in days) of the date window that will be used while syncing data from the channel messages stream. A smaller window will allow for greater parallelization when syncing records, but can lead to rate limiting errors.",
    )
    @JsonSchemaInject(
        json = """{"order":8,"default":100,"minimum":1,"maximum":100,"examples":[30,10,5]}""",
    )
    var channelMessagesWindowSize: Int? = null

    @JsonProperty("concurrency")
    @JsonSchemaTitle("Concurrency")
    @JsonPropertyDescription(
        "Maximum number of streams read at the same time. Slack rate limits each API method separately, so reading the streams concurrently (users, channels, channel members, channel messages and threads each use their own method) shortens a sync without hitting the limits sooner. Defaults to the legacy 'num_workers' value, or 2.",
    )
    @JsonSchemaInject(json = """{"order":9,"minimum":1,"maximum":10,"examples":[2,5]}""")
    var concurrency: Int? = null

    @JsonProperty("checkpoint_target_interval_seconds")
    @JsonSchemaTitle("Checkpoint Target Time Interval (Advanced)")
    @JsonSchemaDescription(
        "How often (in seconds) a stream should checkpoint its progress, when possible. Long streams (channel messages, threads) save their state at about this interval, so that an interrupted sync resumes where it stopped. Defaults to 300.",
    )
    @JsonSchemaInject(json = """{"order":10,"default":300,"minimum":1,"examples":[300,900]}""")
    var checkpointTargetIntervalSeconds: Int? = null

    companion object {
        const val DEFAULT_LOOKBACK_WINDOW_DAYS = 0
        const val MAX_LOOKBACK_WINDOW_DAYS = 365
        const val DEFAULT_CHANNEL_MESSAGES_WINDOW_SIZE_DAYS = 100
        const val MAX_CHANNEL_MESSAGES_WINDOW_SIZE_DAYS = 100
        const val DEFAULT_NUM_WORKERS = 2
        const val MAX_CONCURRENCY = 10

        /** Same default as the Bulk CDK JDBC sources. */
        const val DEFAULT_CHECKPOINT_TARGET_INTERVAL_SECONDS = 300
    }
}

/**
 * The `credentials` oneOf, discriminated by `option_title` exactly like the legacy spec: "Default
 * OAuth2.0 authorization" (Airbyte's OAuth flow, or a user's own Slack app) and "API Token
 * Credentials" (a bot token pasted by the user).
 */
@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    property = CredentialsSpecification.OPTION_TITLE,
    // Any other `option_title` deserializes to this marker so that the configuration factory can
    // reject it with a clear message. Not part of the generated spec.
    defaultImpl = UnsupportedCredentialsSpecification::class,
)
@JsonSubTypes(
    JsonSubTypes.Type(
        value = OAuthCredentialsSpecification::class,
        name = CredentialsSpecification.OAUTH
    ),
    JsonSubTypes.Type(
        value = ApiTokenCredentialsSpecification::class,
        name = CredentialsSpecification.API_TOKEN
    ),
)
sealed interface CredentialsSpecification {
    /** The bearer token used for every Slack Web API call. Not a spec property. */
    @get:JsonIgnore val token: String?

    companion object {
        const val OPTION_TITLE = "option_title"
        const val OAUTH = "Default OAuth2.0 authorization"
        const val API_TOKEN = "API Token Credentials"
    }
}

/** Token obtained through Slack's OAuth 2.0 flow (Airbyte Cloud's Marketplace app, or your own). */
@JsonSchemaTitle("Sign in via Slack (OAuth)")
@JsonSchemaInject(json = """{"order":0}""")
@JsonPropertyOrder(value = ["client_id", "client_secret", "access_token"])
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class OAuthCredentialsSpecification : CredentialsSpecification {
    @JsonProperty("client_id")
    @JsonSchemaTitle("Client ID")
    @JsonSchemaDescription(
        """Slack client_id. See our <a href="https://docs.airbyte.com/integrations/sources/slack">docs</a> if you need help finding this id.""",
    )
    lateinit var clientId: String

    @JsonProperty("client_secret")
    @JsonSchemaTitle("Client Secret")
    @JsonSchemaDescription(
        """Slack client_secret. See our <a href="https://docs.airbyte.com/integrations/sources/slack">docs</a> if you need help finding this secret.""",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true}""")
    lateinit var clientSecret: String

    @JsonProperty("access_token")
    @JsonSchemaTitle("Access token")
    @JsonSchemaDescription(
        """Slack access_token. See our <a href="https://docs.airbyte.com/integrations/sources/slack">docs</a> if you need help generating the token.""",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true}""")
    lateinit var accessToken: String

    @get:JsonIgnore
    override val token: String?
        get() = if (this::accessToken.isInitialized) accessToken else null
}

/** A bot token (`xoxb-...`) of a Slack app installed in the workspace. */
@JsonSchemaTitle("Bot Token")
@JsonSchemaInject(json = """{"order":1}""")
@JsonPropertyOrder(value = ["api_token"])
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class ApiTokenCredentialsSpecification : CredentialsSpecification {
    @JsonProperty("api_token")
    @JsonSchemaTitle("Bot Token")
    @JsonSchemaDescription(
        """A Slack bot token (xoxb-). See the <a href="https://docs.airbyte.com/integrations/sources/slack">docs</a> for instructions on how to generate it.""",
    )
    @JsonSchemaInject(json = """{"airbyte_secret":true}""")
    lateinit var apiToken: String

    @get:JsonIgnore
    override val token: String?
        get() = if (this::apiToken.isInitialized) apiToken else null
}

/**
 * Marker for an `option_title` this connector does not know. Rejected by the configuration factory.
 */
class UnsupportedCredentialsSpecification : CredentialsSpecification {
    @get:JsonIgnore
    override val token: String?
        get() = null
}
