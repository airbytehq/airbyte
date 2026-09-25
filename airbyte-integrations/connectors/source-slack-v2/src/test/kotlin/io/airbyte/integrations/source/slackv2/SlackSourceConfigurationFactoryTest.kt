/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class SlackSourceConfigurationFactoryTest {

    private val factory = SlackSourceConfigurationFactory()

    private fun spec(json: String): SlackSourceConfigurationSpecification =
        Jsons.readValue(json, SlackSourceConfigurationSpecification::class.java)

    private fun assertConfigError(json: String, expectedMessageFragment: String) {
        val e: ConfigErrorException =
            Assertions.assertThrows(ConfigErrorException::class.java) { factory.make(spec(json)) }
        Assertions.assertTrue(
            e.message!!.contains(expectedMessageFragment),
            "expected '$expectedMessageFragment' in '${e.message}'"
        )
    }

    private val valid =
        """"start_date":"2024-01-01T00:00:00Z","lookback_window":0,"join_channels":true,"credentials":{"option_title":"API Token Credentials","api_token":"xoxb-1"}"""

    @Test
    fun testDefaults() {
        val config: SlackSourceConfiguration = factory.make(spec("{$valid}"))
        Assertions.assertEquals(java.time.Instant.parse("2024-01-01T00:00:00Z"), config.startDate)
        Assertions.assertEquals(java.time.Duration.ZERO, config.lookbackWindow)
        Assertions.assertTrue(config.joinChannels)
        Assertions.assertFalse(config.includePrivateChannels)
        Assertions.assertFalse(config.includeArchivedChannels)
        Assertions.assertTrue(config.channelFilter.isEmpty())
        Assertions.assertFalse(config.threadsIgnoreNoReplies)
        Assertions.assertEquals(java.time.Duration.ofDays(100), config.channelMessagesWindow)
        Assertions.assertEquals(2, config.maxConcurrency)
        Assertions.assertEquals(java.time.Duration.ofSeconds(300), config.checkpointTargetInterval)
        Assertions.assertEquals("https://slack.com/api/", config.apiBaseUrl.toString())
        Assertions.assertEquals("slack.com", config.realHost)
        Assertions.assertEquals(443, config.realPort)
        Assertions.assertFalse(
            config.toString().contains("xoxb-1"),
            "token must not leak into toString"
        )
    }

    @Test
    fun testMissingCredentials() =
        assertConfigError(
            """{"start_date":"2024-01-01T00:00:00Z","lookback_window":0,"join_channels":true}""",
            "Missing required 'credentials'"
        )

    @Test
    fun testUnknownOptionTitle() =
        assertConfigError(
            """{"start_date":"2024-01-01T00:00:00Z","lookback_window":0,"join_channels":true,"credentials":{"option_title":"Nope","api_token":"x"}}""",
            "Unsupported 'credentials.option_title'"
        )

    @Test
    fun testBlankToken() =
        assertConfigError(
            """{"start_date":"2024-01-01T00:00:00Z","lookback_window":0,"join_channels":true,"credentials":{"option_title":"API Token Credentials","api_token":"  "}}""",
            "'credentials.api_token' property must not be blank"
        )

    @Test
    fun testBlankOAuthToken() =
        assertConfigError(
            """{"start_date":"2024-01-01T00:00:00Z","lookback_window":0,"join_channels":true,"credentials":{"option_title":"Default OAuth2.0 authorization","client_id":"c","client_secret":"s","access_token":""}}""",
            "'credentials.access_token' property must not be blank"
        )

    @Test
    fun testMissingStartDate() =
        assertConfigError(
            """{"lookback_window":0,"join_channels":true,"credentials":{"option_title":"API Token Credentials","api_token":"x"}}""",
            "'start_date' property is required"
        )

    @Test
    fun testInvalidStartDate() =
        assertConfigError(
            """{"start_date":"2024-01-01","lookback_window":0,"join_channels":true,"credentials":{"option_title":"API Token Credentials","api_token":"x"}}""",
            "Invalid 'start_date'"
        )

    @Test
    fun testLookbackWindowRange() =
        assertConfigError(
            """{"start_date":"2024-01-01T00:00:00Z","lookback_window":400,"join_channels":true,"credentials":{"option_title":"API Token Credentials","api_token":"x"}}""",
            "'lookback_window' must be between 0 and 365"
        )

    @Test
    fun testWindowSizeRange() =
        assertConfigError(
            "{$valid,\"channel_messages_window_size\":0}",
            "'channel_messages_window_size' must be between 1 and 100"
        )

    @Test
    fun testConcurrencyRange() =
        assertConfigError("{$valid,\"concurrency\":11}", "'concurrency' must be between 1 and 10")

    @Test
    fun testCheckpointIntervalRange() =
        assertConfigError(
            "{$valid,\"checkpoint_target_interval_seconds\":0}",
            "'checkpoint_target_interval_seconds' must be at least 1"
        )

    @Test
    fun testConcurrencyPrecedence() {
        Assertions.assertEquals(2, factory.make(spec("{$valid}")).maxConcurrency)
        Assertions.assertEquals(5, factory.make(spec("{$valid,\"num_workers\":5}")).maxConcurrency)
        Assertions.assertEquals(
            3,
            factory.make(spec("{$valid,\"num_workers\":5,\"concurrency\":3}")).maxConcurrency
        )
        Assertions.assertEquals(1, factory.make(spec("{$valid,\"concurrency\":1}")).maxConcurrency)
    }

    @Test
    fun testChannelFilterNormalization() {
        val config =
            factory.make(spec("{$valid,\"channel_filter\":[\"#general\",\" random \",\"\"]}"))
        Assertions.assertEquals(setOf("general", "random"), config.channelFilter)
    }

    @Test
    fun testApiBaseUrlOverride() {
        val config =
            SlackSourceConfigurationFactory(apiBaseUrl = "http://localhost:1234/api")
                .make(spec("{$valid}"))
        Assertions.assertEquals("http://localhost:1234/api/", config.apiBaseUrl.toString())
        Assertions.assertEquals("localhost", config.realHost)
        Assertions.assertEquals(1234, config.realPort)
    }
}
