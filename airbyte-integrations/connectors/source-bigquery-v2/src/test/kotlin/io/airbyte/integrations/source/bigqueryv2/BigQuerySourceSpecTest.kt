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
 * output of the published legacy `airbyte/source-bigquery:0.4.5` image. The spec is laid out like
 * `destination-bigquery`'s (groups, ordering, titles), but every legacy property must survive with
 * the same JSON type and the same `required` list so that saved configurations keep working.
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

    /** A configuration saved for the legacy connector must still validate against this spec. */
    @Test
    fun testLegacyConfigurationsStillValidate() {
        val legacy: JsonNode =
            Jsons.readTree(ResourceUtils.readResource(LEGACY_SPEC_RESOURCE))[
                    "connectionSpecification"]
        val actual: JsonNode = actualSpec().connectionSpecification
        for ((name, legacyProperty) in legacy["properties"].properties()) {
            val property: JsonNode? = actual["properties"][name]
            Assertions.assertNotNull(property, "legacy property '$name' is gone")
            Assertions.assertEquals(legacyProperty["type"], property!!["type"], name)
            Assertions.assertEquals(
                legacyProperty["airbyte_secret"],
                property["airbyte_secret"],
                name
            )
        }
        Assertions.assertEquals(legacy["required"], actual["required"])
        Assertions.assertEquals(legacy["title"], actual["title"])
        Assertions.assertEquals(legacy["\$schema"], actual["\$schema"])
    }

    /** The layout borrowed from `destination-bigquery`: every property is grouped and ordered. */
    @Test
    fun testEveryPropertyIsGroupedAndOrdered() {
        val actual: JsonNode = actualSpec().connectionSpecification
        val groupIds: Set<String> = actual["groups"].map { it["id"].asText() }.toSet()
        Assertions.assertEquals(setOf("connection", "advanced"), groupIds)
        val orders = mutableSetOf<Int>()
        for ((name, property) in actual["properties"].properties()) {
            Assertions.assertTrue(property["group"]?.asText() in groupIds, "group of '$name'")
            Assertions.assertTrue(orders.add(property["order"].asInt()), "order of '$name'")
        }
        // The new optional properties are advanced ones, so that the connection form stays short.
        Assertions.assertEquals(
            "advanced",
            actual["properties"]["job_project_id"]["group"].asText()
        )
        Assertions.assertEquals(
            "advanced",
            actual["properties"]["max_db_connections"]["group"].asText()
        )
        Assertions.assertEquals(
            "integer",
            actual["properties"]["max_db_connections"]["type"].asText()
        )
    }

    /** The `spec` carries the URL of this connector's own docs page (from `metadata.yaml`). */
    @Test
    fun testDocumentationUrlPointsAtTheConnectorDocsPage() {
        Assertions.assertEquals(
            "https://docs.airbyte.com/integrations/sources/bigquery-v2",
            actualSpec().documentationUrl.toString(),
        )
    }

    private fun actualSpec(): ConnectorSpecification = CliRunner.source("spec").run().specs().last()

    companion object {
        const val EXPECTED_SPEC_RESOURCE = "expected-spec.json"
        const val LEGACY_SPEC_RESOURCE = "legacy-spec.json"
    }
}
