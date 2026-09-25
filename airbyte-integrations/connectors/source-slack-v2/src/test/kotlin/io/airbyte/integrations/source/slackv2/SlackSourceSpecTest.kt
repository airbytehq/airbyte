/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.slackv2

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.ConnectorSpecification
import java.io.File
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Isolated

/**
 * `expected-spec.json` is the snapshot of this connector's own `spec`; `legacy-spec.json` is the
 * `spec` output of `airbyte/source-slack:3.2.24`. Every legacy property, the `required` list, the
 * `credentials` oneOf and `advanced_auth` must be identical, so that saved configurations and the
 * OAuth flow keep working; only the two standard Bulk CDK properties are added.
 */
/** Runs alone: the fake server, its request log and the system properties are shared state. */
@Isolated
class SlackSourceSpecTest {

    @Test
    fun testSpecMatchesSnapshot() {
        SyncsTestFixture.testSpec(EXPECTED_SPEC_RESOURCE)
    }

    @Test
    fun testSpecIsIdenticalToSnapshot() {
        val actual: JsonNode = actualSpec()
        val expected: JsonNode = Jsons.readTree(ResourceUtils.readResource(EXPECTED_SPEC_RESOURCE))
        Assertions.assertEquals(
            expected,
            actual,
            Jsons.writerWithDefaultPrettyPrinter().writeValueAsString(actual)
        )
    }

    @Test
    fun testLegacySpecParity() {
        val actual: JsonNode = actualSpec()
        val legacy: JsonNode = Jsons.readTree(ResourceUtils.readResource(LEGACY_SPEC_RESOURCE))
        val actualProperties: JsonNode = actual["connectionSpecification"]["properties"]
        val legacyProperties: JsonNode = legacy["connectionSpecification"]["properties"]
        for ((name: String, legacySchema: JsonNode) in legacyProperties.properties()) {
            Assertions.assertEquals(legacySchema, actualProperties[name], "property '$name'")
        }
        Assertions.assertEquals(
            setOf("concurrency", "checkpoint_target_interval_seconds"),
            actualProperties.fieldNames().asSequence().toSet() -
                legacyProperties.fieldNames().asSequence().toSet(),
        )
        Assertions.assertEquals(
            legacy["connectionSpecification"]["required"],
            actual["connectionSpecification"]["required"]
        )
        Assertions.assertEquals(
            legacy["connectionSpecification"]["title"],
            actual["connectionSpecification"]["title"]
        )
        Assertions.assertEquals(legacy["advanced_auth"], actual["advanced_auth"])
        Assertions.assertEquals(legacy["supportsNormalization"], actual["supportsNormalization"])
        Assertions.assertEquals(legacy["supportsDBT"], actual["supportsDBT"])
    }

    @Test
    fun testLegacyConfigurationsStillLoad() {
        val factory = SlackSourceConfigurationFactory()
        val token: SlackSourceConfiguration =
            factory.make(
                Jsons.readValue(
                    """{"start_date":"2017-01-25T00:00:00Z","lookback_window":7,"join_channels":false,
                        "channel_filter":["general","random"],"credentials":{"option_title":"API Token Credentials","api_token":"xoxb-1"},
                        "num_workers":4,"channel_messages_window_size":30}""",
                    SlackSourceConfigurationSpecification::class.java,
                ),
            )
        Assertions.assertEquals("xoxb-1", token.token)
        Assertions.assertFalse(token.oauth)
        Assertions.assertEquals(java.time.Duration.ofDays(7), token.lookbackWindow)
        Assertions.assertEquals(setOf("general", "random"), token.channelFilter)
        Assertions.assertEquals(4, token.maxConcurrency)
        Assertions.assertEquals(java.time.Duration.ofDays(30), token.channelMessagesWindow)

        val oauth: SlackSourceConfiguration =
            factory.make(
                Jsons.readValue(
                    """{"start_date":"2024-01-01T00:00:00Z","lookback_window":0,"join_channels":true,
                        "credentials":{"option_title":"Default OAuth2.0 authorization","client_id":"c","client_secret":"s","access_token":"xoxe-1"}}""",
                    SlackSourceConfigurationSpecification::class.java,
                ),
            )
        Assertions.assertEquals("xoxe-1", oauth.token)
        Assertions.assertTrue(oauth.oauth)
        Assertions.assertEquals(2, oauth.maxConcurrency)
    }

    private fun actualSpec(): JsonNode {
        val actualSpec: ConnectorSpecification = CliRunner.source("spec").run().specs().last()
        val actual: JsonNode = Jsons.valueToTree(actualSpec)
        File("build").mkdirs()
        File("build/actual-spec.json")
            .writeText(Jsons.writerWithDefaultPrettyPrinter().writeValueAsString(actual) + "\n")
        return actual
    }

    companion object {
        const val EXPECTED_SPEC_RESOURCE = "expected-spec.json"
        const val LEGACY_SPEC_RESOURCE = "legacy-spec.json"
    }
}
