/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigquery

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * The `spec` output depends on the deployment ([BigQuerySourceSpecificationExtender]):
 * `expected-spec-cloud.json` is the output on Airbyte Cloud (`AIRBYTE_EDITION=CLOUD`) and
 * `expected-spec-oss.json` the output everywhere else, where the Cloud-only settings are shown
 * disabled. `legacy-spec.json` is the `spec` output of the published legacy
 * `airbyte/source-bigquery:0.4.5` image. The spec is laid out like `destination-bigquery`'s
 * (groups, ordering, titles), but every legacy property must survive with the same JSON type and
 * the same `required` list so that saved configurations keep working.
 */
class BigQuerySourceSpecTest {

    /** The two spec variants and the feature flags which select them. */
    enum class Edition(val expectedSpecResource: String, vararg val featureFlags: FeatureFlag) {
        CLOUD("expected-spec-cloud.json", FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
        SELF_MANAGED("expected-spec-oss.json"),
    }

    /** Whole-tree equality with the snapshot, including array order. */
    @Test
    fun testSpecIsIdenticalToSnapshot() {
        for (edition in Edition.entries) {
            val expected: JsonNode =
                Jsons.readTree(ResourceUtils.readResource(edition.expectedSpecResource))
            val actual: JsonNode = Jsons.valueToTree(actualSpec(edition))
            Assertions.assertEquals(
                expected,
                actual,
                "$edition: ${Jsons.writeValueAsString(actual)}"
            )
        }
    }

    /**
     * The Cloud spec is the full one. Elsewhere `max_db_connections` and `use_storage_read_api` are
     * read-only (the Airbyte form shows them disabled), always visible, with the pinned values as
     * defaults and a description saying so; nothing else differs, so a configuration saved on
     * either edition validates on the other.
     */
    @Test
    fun testOnlyTheCloudOnlySettingsDifferBetweenEditions() {
        val cloud: ObjectNode = actualSpec(Edition.CLOUD).connectionSpecification as ObjectNode
        val selfManaged: ObjectNode =
            actualSpec(Edition.SELF_MANAGED).connectionSpecification as ObjectNode
        for ((name, property) in cloud["properties"].properties()) {
            Assertions.assertNull(property["readOnly"], "Cloud disables '$name'")
            Assertions.assertNull(property["airbyte_hidden"], "Cloud hides '$name'")
        }
        for (name in listOf("max_db_connections", "use_storage_read_api")) {
            val property: JsonNode = selfManaged["properties"][name]
            Assertions.assertTrue(property["readOnly"].asBoolean(), property.toString())
            Assertions.assertTrue(property["always_show"].asBoolean(), property.toString())
            Assertions.assertNull(property["airbyte_hidden"], property.toString())
            Assertions.assertTrue(
                property["description"].asText().contains("self-managed Airbyte"),
                property.toString(),
            )
        }
        Assertions.assertEquals(
            1,
            selfManaged["properties"]["max_db_connections"]["default"].asInt()
        )
        Assertions.assertFalse(
            selfManaged["properties"]["use_storage_read_api"]["default"].asBoolean()
        )
        for (spec in listOf(cloud, selfManaged)) {
            (spec["properties"] as ObjectNode).remove(
                listOf("max_db_connections", "use_storage_read_api")
            )
        }
        Assertions.assertEquals(cloud, selfManaged)
    }

    /** A configuration saved for the legacy connector must still validate against either spec. */
    @Test
    fun testLegacyConfigurationsStillValidate() {
        val legacy: JsonNode =
            Jsons.readTree(ResourceUtils.readResource(LEGACY_SPEC_RESOURCE))[
                    "connectionSpecification"]
        for (edition in Edition.entries) {
            val actual: JsonNode = actualSpec(edition).connectionSpecification
            for ((name, legacyProperty) in legacy["properties"].properties()) {
                val property: JsonNode? = actual["properties"][name]
                Assertions.assertNotNull(property, "$edition: legacy property '$name' is gone")
                Assertions.assertEquals(
                    legacyProperty["type"],
                    property!!["type"],
                    "$edition $name"
                )
                Assertions.assertEquals(
                    legacyProperty["airbyte_secret"],
                    property["airbyte_secret"],
                    "$edition $name",
                )
            }
            Assertions.assertEquals(legacy["required"], actual["required"], "$edition")
            Assertions.assertEquals(legacy["title"], actual["title"], "$edition")
            Assertions.assertEquals(legacy["\$schema"], actual["\$schema"], "$edition")
        }
    }

    /** The layout borrowed from `destination-bigquery`: every property is grouped and ordered. */
    @Test
    fun testEveryPropertyIsGroupedAndOrdered() {
        for (edition in Edition.entries) {
            val actual: JsonNode = actualSpec(edition).connectionSpecification
            val groupIds: Set<String> = actual["groups"].map { it["id"].asText() }.toSet()
            Assertions.assertEquals(setOf("connection", "advanced"), groupIds, "$edition")
            val orders = mutableSetOf<Int>()
            for ((name, property) in actual["properties"].properties()) {
                Assertions.assertTrue(
                    property["group"]?.asText() in groupIds,
                    "$edition: group of '$name'"
                )
                Assertions.assertTrue(orders.add(property["order"].asInt()), "order of '$name'")
            }
            // The new optional properties are advanced ones, so that the connection form stays
            // short.
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
    }

    /** The `spec` carries the URL of this connector's own docs page (from `metadata.yaml`). */
    @Test
    fun testDocumentationUrlPointsAtTheConnectorDocsPage() {
        for (edition in Edition.entries) {
            Assertions.assertEquals(
                "https://docs.airbyte.com/integrations/sources/bigquery",
                actualSpec(edition).documentationUrl.toString(),
                "$edition",
            )
        }
    }

    private fun actualSpec(edition: Edition): ConnectorSpecification =
        CliRunner.source("spec", null, null, null, *edition.featureFlags).run().specs().last()

    companion object {
        const val LEGACY_SPEC_RESOURCE = "legacy-spec.json"
    }
}
