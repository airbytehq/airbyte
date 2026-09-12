/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * `expected-spec.json` is the `spec` output of this connector; `legacy-spec.json` is the `spec`
 * output of the published legacy `airbyte/source-bigquery:0.4.5` image. The connection
 * specification properties (names, titles, descriptions, secrets, required list) must stay
 * identical to the legacy ones so that saved configurations keep working.
 */
class BigQuerySourceSpecTest {

    @Test
    fun testSpecMatchesSnapshot() {
        SyncsTestFixture.testSpec(EXPECTED_SPEC_RESOURCE)
    }

    /** Stricter than [SyncsTestFixture.testSpec]: whole-tree equality, including array order. */
    @Test
    fun testSpecIsIdenticalToSnapshot() {
        val expected: JsonNode = Jsons.readTree(ResourceUtils.readResource(EXPECTED_SPEC_RESOURCE))
        val actual: JsonNode = Jsons.valueToTree(actualSpec())
        Assertions.assertEquals(expected, actual, Jsons.writeValueAsString(actual))
    }

    @Test
    fun testConnectionSpecificationPropertiesMatchLegacyConnector() {
        val legacy: JsonNode =
            Jsons.readTree(ResourceUtils.readResource(LEGACY_SPEC_RESOURCE))[
                    "connectionSpecification"]
        val actual: JsonNode = actualSpec().connectionSpecification
        Assertions.assertEquals(legacy["properties"], actual["properties"])
        Assertions.assertEquals(legacy["required"], actual["required"])
        Assertions.assertEquals(legacy["title"], actual["title"])
        Assertions.assertEquals(legacy["\$schema"], actual["\$schema"])
    }

    @Test
    fun testDocumentationUrlMatchesLegacyConnector() {
        val legacy: JsonNode = Jsons.readTree(ResourceUtils.readResource(LEGACY_SPEC_RESOURCE))
        Assertions.assertEquals(
            legacy["documentationUrl"].asText(),
            actualSpec().documentationUrl.toString(),
        )
    }

    private fun actualSpec(): ConnectorSpecification = CliRunner.source("spec").run().specs().last()

    companion object {
        const val EXPECTED_SPEC_RESOURCE = "expected-spec.json"
        const val LEGACY_SPEC_RESOURCE = "legacy-spec.json"
    }
}
