/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.SourceConfiguration
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.output.DataChannelMedium
import io.airbyte.cdk.output.DataChannelMedium.SOCKET
import io.airbyte.cdk.output.DataChannelMedium.STDIO
import io.airbyte.cdk.output.sockets.DATA_CHANNEL_PROPERTY_PREFIX
import io.airbyte.cdk.ssh.SshConnectionOptions
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.net.URI
import java.time.Duration
import java.time.Instant
import java.time.format.DateTimeParseException

/** Slack-specific implementation of [SourceConfiguration]. */
data class SlackSourceConfiguration(
    /** Bearer token of every Slack Web API call (`xoxb-`/`xoxp-`/`xoxe-`). */
    val token: String,
    /** Whether the token came from the OAuth flow (Airbyte's Marketplace app) or was pasted. */
    val oauth: Boolean,
    /** Base URL of the Slack Web API, `https://slack.com/api/` outside tests. */
    val apiBaseUrl: URI,
    /** Messages before this instant are not replicated. */
    val startDate: Instant,
    /** How far before the saved cursor the message and thread streams look again. */
    val lookbackWindow: Duration,
    val joinChannels: Boolean,
    val includePrivateChannels: Boolean,
    val includeArchivedChannels: Boolean,
    /** Channel names to replicate; empty for every channel. */
    val channelFilter: Set<String>,
    val threadsIgnoreNoReplies: Boolean,
    /** Size of the date windows a channel's history is read in. */
    val channelMessagesWindow: Duration,
    override val maxConcurrency: Int,
    override val realHost: String,
    override val realPort: Int,
    /** Slack syncs use per-stream state (no CDC / Global feed). */
    override val global: Boolean = false,
    override val maxSnapshotReadDuration: Duration? = null,
    /** How long a partition reader runs before the CDK asks it for a checkpoint. */
    override val checkpointTargetInterval: Duration,
    override val resourceAcquisitionHeartbeat: Duration = Duration.ofMillis(100L),
    /** SSH tunnels are not part of the Slack spec. */
    override val sshTunnel: SshTunnelMethodConfiguration? = null,
    override val sshConnectionOptions: SshConnectionOptions =
        SshConnectionOptions.fromAdditionalProperties(emptyMap()),
) : SourceConfiguration {

    /** Keeps the token out of logs. */
    override fun toString(): String =
        "SlackSourceConfiguration(token=*****, oauth=$oauth, apiBaseUrl=$apiBaseUrl, " +
            "startDate=$startDate, lookbackWindow=$lookbackWindow, joinChannels=$joinChannels, " +
            "includePrivateChannels=$includePrivateChannels, " +
            "includeArchivedChannels=$includeArchivedChannels, channelFilter=$channelFilter, " +
            "threadsIgnoreNoReplies=$threadsIgnoreNoReplies, " +
            "channelMessagesWindow=$channelMessagesWindow, maxConcurrency=$maxConcurrency, " +
            "checkpointTargetInterval=$checkpointTargetInterval)"

    /** Required to inject [SlackSourceConfiguration] directly. */
    @Factory
    private class MicronautFactory {
        @Singleton
        fun slackSourceConfig(
            factory:
                SourceConfigurationFactory<
                    SlackSourceConfigurationSpecification, SlackSourceConfiguration>,
            supplier: ConfigurationSpecificationSupplier<SlackSourceConfigurationSpecification>,
        ): SlackSourceConfiguration = factory.make(supplier.get())
    }

    companion object {
        const val HTTPS_PORT = 443
        const val HTTP_PORT = 80
        const val DEFAULT_API_BASE_URL = "https://slack.com/api/"
    }
}

@Singleton
class SlackSourceConfigurationFactory
@Inject
constructor(
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.medium}") val dataChannelMedium: String = STDIO.name,
    @Value("\${${DATA_CHANNEL_PROPERTY_PREFIX}.socket-paths}")
    val socketPaths: List<String> = emptyList(),
    /** Tests and the local harness point the connector at a fake Slack server. */
    @Value("\${$API_BASE_URL_PROPERTY:${SlackSourceConfiguration.DEFAULT_API_BASE_URL}}")
    val apiBaseUrl: String = SlackSourceConfiguration.DEFAULT_API_BASE_URL,
) : SourceConfigurationFactory<SlackSourceConfigurationSpecification, SlackSourceConfiguration> {

    private val log = KotlinLogging.logger {}

    /**
     * The default implementation wraps every exception, including [ConfigErrorException], in a
     * generic "Failed to build ConnectorConfiguration." error, which hides the user-facing messages
     * thrown below. Let those through unchanged.
     */
    override fun make(spec: SlackSourceConfigurationSpecification): SlackSourceConfiguration =
        try {
            makeWithoutExceptionHandling(spec)
        } catch (e: ConfigErrorException) {
            throw e
        } catch (e: Exception) {
            throw ConfigErrorException("Failed to build ConnectorConfiguration.", e)
        }

    override fun makeWithoutExceptionHandling(
        pojo: SlackSourceConfigurationSpecification,
    ): SlackSourceConfiguration {
        val credentials: CredentialsSpecification =
            pojo.credentials
                ?: throw ConfigErrorException(
                    "Missing required 'credentials' property: choose 'Sign in via Slack (OAuth)' " +
                        "or 'Bot Token'.",
                )
        if (credentials is UnsupportedCredentialsSpecification) {
            throw ConfigErrorException(
                "Unsupported 'credentials.option_title'; expected " +
                    "'${CredentialsSpecification.OAUTH}' or '${CredentialsSpecification.API_TOKEN}'.",
            )
        }
        val token: String =
            credentials.token?.trim()?.ifBlank { null }
                ?: throw ConfigErrorException(
                    when (credentials) {
                        is OAuthCredentialsSpecification ->
                            "The 'credentials.access_token' property must not be blank."
                        else -> "The 'credentials.api_token' property must not be blank."
                    },
                )

        val startDateText: String =
            pojo.startDateOrNull()?.trim()?.ifBlank { null }
                ?: throw ConfigErrorException("The 'start_date' property is required.")
        val startDate: Instant =
            try {
                Instant.parse(startDateText)
            } catch (e: DateTimeParseException) {
                throw ConfigErrorException(
                    "Invalid 'start_date' '$startDateText': expected a UTC date and time such as " +
                        "2017-01-25T00:00:00Z.",
                    e,
                )
            }

        val lookbackWindowDays: Int = pojo.lookbackWindow
        if (
            lookbackWindowDays !in 0..SlackSourceConfigurationSpecification.MAX_LOOKBACK_WINDOW_DAYS
        ) {
            throw ConfigErrorException(
                "'lookback_window' must be between 0 and " +
                    "${SlackSourceConfigurationSpecification.MAX_LOOKBACK_WINDOW_DAYS} days, " +
                    "got $lookbackWindowDays.",
            )
        }

        val windowDays: Int =
            pojo.channelMessagesWindowSize
                ?: SlackSourceConfigurationSpecification.DEFAULT_CHANNEL_MESSAGES_WINDOW_SIZE_DAYS
        if (
            windowDays !in
                1..SlackSourceConfigurationSpecification.MAX_CHANNEL_MESSAGES_WINDOW_SIZE_DAYS
        ) {
            throw ConfigErrorException(
                "'channel_messages_window_size' must be between 1 and " +
                    "${SlackSourceConfigurationSpecification.MAX_CHANNEL_MESSAGES_WINDOW_SIZE_DAYS} " +
                    "days, got $windowDays.",
            )
        }

        val channelFilter: Set<String> =
            pojo.channelFilter
                ?.map { it.trim().removePrefix("#") }
                ?.filter(String::isNotEmpty)
                ?.toSet()
                ?: emptySet()

        val checkpointTargetIntervalSeconds: Int =
            pojo.checkpointTargetIntervalSeconds
                ?: SlackSourceConfigurationSpecification.DEFAULT_CHECKPOINT_TARGET_INTERVAL_SECONDS
        if (checkpointTargetIntervalSeconds < 1) {
            throw ConfigErrorException(
                "'checkpoint_target_interval_seconds' must be at least 1, got $checkpointTargetIntervalSeconds.",
            )
        }

        // Slack rate limits each Web API method separately, so streams (each on its own method)
        // are read concurrently: the standard `concurrency` wins, then the legacy `num_workers`,
        // then the legacy default of 2; in speed mode, one stream per socket.
        val requestedConcurrency: Int? = pojo.concurrency ?: pojo.numWorkers
        val maxConcurrency: Int =
            when (DataChannelMedium.valueOf(dataChannelMedium)) {
                STDIO -> requestedConcurrency
                        ?: SlackSourceConfigurationSpecification.DEFAULT_NUM_WORKERS
                SOCKET -> requestedConcurrency ?: socketPaths.size.coerceAtLeast(1)
            }
        if (maxConcurrency !in 1..SlackSourceConfigurationSpecification.MAX_CONCURRENCY) {
            throw ConfigErrorException(
                "'concurrency' must be between 1 and " +
                    "${SlackSourceConfigurationSpecification.MAX_CONCURRENCY}, got $maxConcurrency.",
            )
        }
        log.info { "Effective concurrency: $maxConcurrency" }

        val baseUrl: URI = parseApiBaseUrl(apiBaseUrl)
        val (realHost: String, realPort: Int) = hostAndPort(baseUrl)

        return SlackSourceConfiguration(
            token = token,
            oauth = credentials is OAuthCredentialsSpecification,
            apiBaseUrl = baseUrl,
            startDate = startDate,
            lookbackWindow = Duration.ofDays(lookbackWindowDays.toLong()),
            joinChannels = pojo.joinChannels,
            includePrivateChannels = pojo.includePrivateChannels ?: false,
            includeArchivedChannels = pojo.includeArchivedChannels ?: false,
            channelFilter = channelFilter,
            threadsIgnoreNoReplies = pojo.threadsIgnoreNoReplies ?: false,
            channelMessagesWindow = Duration.ofDays(windowDays.toLong()),
            checkpointTargetInterval = Duration.ofSeconds(checkpointTargetIntervalSeconds.toLong()),
            maxConcurrency = maxConcurrency,
            realHost = realHost,
            realPort = realPort,
        )
    }

    companion object {
        const val API_BASE_URL_PROPERTY = "airbyte.connector.extract.slack.api-base-url"

        /**
         * An absolute http(s) URL ending in a slash, so that method names can be resolved on it.
         */
        fun parseApiBaseUrl(raw: String): URI {
            val text: String = raw.trim().let { if (it.endsWith("/")) it else "$it/" }
            val uri: URI =
                try {
                    URI(text)
                } catch (e: java.net.URISyntaxException) {
                    throw ConfigErrorException("Invalid Slack API base URL '$raw': ${e.reason}", e)
                }
            val scheme: String? = uri.scheme?.lowercase()
            if ((scheme != "http" && scheme != "https") || uri.host == null) {
                throw ConfigErrorException(
                    "Invalid Slack API base URL '$raw': expected a URL such as https://slack.com/api/.",
                )
            }
            return uri
        }

        /** Informational only (the CDK uses them for SSH tunnels, which the Slack spec lacks). */
        fun hostAndPort(baseUrl: URI): Pair<String, Int> {
            val port: Int =
                when {
                    baseUrl.port > 0 -> baseUrl.port
                    baseUrl.scheme.equals("http", ignoreCase = true) ->
                        SlackSourceConfiguration.HTTP_PORT
                    else -> SlackSourceConfiguration.HTTPS_PORT
                }
            return baseUrl.host to port
        }
    }
}
