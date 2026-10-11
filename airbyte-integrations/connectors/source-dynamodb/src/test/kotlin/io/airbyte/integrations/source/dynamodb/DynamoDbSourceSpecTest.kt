/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.ConnectorSpecification
import java.io.File
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import software.amazon.awssdk.regions.Region

/**
 * The `spec` output depends on the deployment ([DynamoDbSourceSpecificationExtender]):
 * `expected-spec-cloud.json` is the output on Airbyte Cloud (`AIRBYTE_EDITION=CLOUD`) and
 * `expected-spec-oss.json` the output everywhere else, where `max_db_connections` is shown
 * disabled. `legacy-spec.json` is the `spec` output of the published legacy
 * `airbyte/source-dynamodb` image, kept because legacy access-key configurations must still load
 * (see [testLegacyAccessKeyConfigurationStillLoads]).
 */
class DynamoDbSourceSpecTest {

    /** The two spec variants and the feature flags which select them. */
    enum class Edition(val expectedSpecResource: String, vararg val featureFlags: FeatureFlag) {
        CLOUD("expected-spec-cloud.json", FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
        SELF_MANAGED("expected-spec-oss.json"),
    }

    /** The CDK's own spec check, which runs without feature flags, i.e. self-managed. */
    @Test
    fun testSpecMatchesSnapshot() {
        SyncsTestFixture.testSpec(Edition.SELF_MANAGED.expectedSpecResource)
    }

    /**
     * Stricter than [SyncsTestFixture.testSpec]: whole-tree equality, including array order, for
     * both editions. The actual specs are also written to `build/actual-spec-<edition>.json` to
     * make refreshing the snapshots easy.
     */
    @Test
    fun testSpecIsIdenticalToSnapshot() {
        val actuals: Map<Edition, JsonNode> =
            Edition.entries.associateWith { Jsons.valueToTree(actualSpec(it)) }
        File("build").mkdirs()
        for ((edition, actual) in actuals) {
            File("build/actual-spec-${edition.name.lowercase()}.json")
                .writeText(Jsons.writerWithDefaultPrettyPrinter().writeValueAsString(actual) + "\n")
        }
        for ((edition, actual) in actuals) {
            val expected: JsonNode =
                Jsons.readTree(ResourceUtils.readResource(edition.expectedSpecResource))
            Assertions.assertEquals(
                expected,
                actual,
                "$edition: ${Jsons.writerWithDefaultPrettyPrinter().writeValueAsString(actual)}",
            )
        }
    }

    /**
     * The Cloud spec is the full one. Elsewhere `max_db_connections` is read-only (the Airbyte form
     * shows it disabled), always visible, with the pinned value as default and a description saying
     * so; nothing else differs, so a configuration saved on either edition validates on the other.
     */
    @Test
    fun testOnlyTheCloudOnlySettingDiffersBetweenEditions() {
        val cloud: ObjectNode = actualSpec(Edition.CLOUD).connectionSpecification as ObjectNode
        val selfManaged: ObjectNode =
            actualSpec(Edition.SELF_MANAGED).connectionSpecification as ObjectNode
        for ((name, property) in cloud["properties"].properties()) {
            Assertions.assertNull(property["readOnly"], "Cloud disables '$name'")
            Assertions.assertNull(property["airbyte_hidden"], "Cloud hides '$name'")
        }
        val property: JsonNode = selfManaged["properties"]["max_db_connections"]
        Assertions.assertTrue(property["readOnly"].asBoolean(), property.toString())
        Assertions.assertTrue(property["always_show"].asBoolean(), property.toString())
        Assertions.assertNull(property["airbyte_hidden"], property.toString())
        Assertions.assertEquals(1, property["default"].asInt(), property.toString())
        Assertions.assertTrue(
            property["description"].asText().contains("self-managed Airbyte"),
            property.toString(),
        )
        for (spec in listOf(cloud, selfManaged)) {
            (spec["properties"] as ObjectNode).remove("max_db_connections")
        }
        Assertions.assertEquals(cloud, selfManaged)
    }

    /** The `region` dropdown lists every reachable region known to the pinned AWS SDK. */
    @Test
    fun testRegionEnumMatchesAwsSdk() {
        val spec: JsonNode =
            Jsons.readTree(ResourceUtils.readResource(Edition.CLOUD.expectedSpecResource))
        val actual: List<String> =
            spec["connectionSpecification"]["properties"]["region"]["enum"].map { it.asText() }
        val expected: List<String> =
            Region.regions()
                .filter { !it.isGlobalRegion }
                .map { it.id() }
                // Isolated (air-gapped) partitions are not reachable from Airbyte.
                .filter { !it.contains("-iso") }
                .sorted()
        Assertions.assertEquals(expected, actual)
    }

    /**
     * Property names and the `auth_type: "User"` discriminator are inherited from the legacy spec,
     * so a configuration saved for `source-dynamodb` (access keys) loads unchanged, on either
     * edition.
     */
    @Test
    fun testLegacyAccessKeyConfigurationStillLoads() {
        val legacy: JsonNode = Jsons.readTree(ResourceUtils.readResource(LEGACY_SPEC_RESOURCE))
        val legacyProperties: Set<String> =
            legacy["connectionSpecification"]["properties"].fieldNames().asSequence().toSet()
        for (edition in Edition.entries) {
            val actual: JsonNode =
                Jsons.readTree(ResourceUtils.readResource(edition.expectedSpecResource))
            val actualProperties: Set<String> =
                actual["connectionSpecification"]["properties"].fieldNames().asSequence().toSet()
            // Every legacy property still exists (new optional ones may be added).
            Assertions.assertTrue(
                actualProperties.containsAll(legacyProperties),
                "$edition: missing legacy properties: ${legacyProperties - actualProperties}",
            )
        }

        val config: DynamoDbSourceConfiguration =
            DynamoDbSourceConfigurationFactory()
                .make(
                    Jsons.readValue(
                        """
{
  "credentials": {"auth_type": "User", "access_key_id": "AKIA123", "secret_access_key": "s3cr3t"},
  "endpoint": "",
  "region": "eu-west-1",
  "reserved_attribute_names": "name, field-name",
  "ignore_missing_read_permissions_tables": true
}
""",
                        DynamoDbSourceConfigurationSpecification::class.java,
                    ),
                )
        Assertions.assertEquals("AKIA123", config.accessKeyId)
        Assertions.assertEquals(Region.EU_WEST_1, config.region)
        Assertions.assertNull(config.endpoint)
        Assertions.assertFalse(config.assumesRole)
    }

    private fun actualSpec(edition: Edition): ConnectorSpecification =
        CliRunner.source("spec", null, null, null, *edition.featureFlags).run().specs().last()

    companion object {
        const val LEGACY_SPEC_RESOURCE = "legacy-spec.json"
    }
}
