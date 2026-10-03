/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.ConnectorSpecification
import java.io.File
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import software.amazon.awssdk.regions.Region

/**
 * `expected-spec.json` is the snapshot of this connector's own `spec`; `legacy-spec.json` is the
 * `spec` output of the published legacy `airbyte/source-dynamodb` image, kept because legacy
 * access-key configurations must still load (see [testLegacyAccessKeyConfigurationStillLoads]).
 */
class DynamoDbSourceSpecTest {

    @Test
    fun testSpecMatchesSnapshot() {
        SyncsTestFixture.testSpec(EXPECTED_SPEC_RESOURCE)
    }

    /**
     * Stricter than [SyncsTestFixture.testSpec]: whole-tree equality, including array order. The
     * actual spec is also written to `build/actual-spec.json` to make refreshing the snapshot easy.
     */
    @Test
    fun testSpecIsIdenticalToSnapshot() {
        val actualSpec: ConnectorSpecification = CliRunner.source("spec").run().specs().last()
        val actual: JsonNode = Jsons.valueToTree(actualSpec)
        File("build").mkdirs()
        File("build/actual-spec.json")
            .writeText(Jsons.writerWithDefaultPrettyPrinter().writeValueAsString(actual) + "\n")
        val expected: JsonNode = Jsons.readTree(ResourceUtils.readResource(EXPECTED_SPEC_RESOURCE))
        Assertions.assertEquals(
            expected,
            actual,
            Jsons.writerWithDefaultPrettyPrinter().writeValueAsString(actual),
        )
    }

    /** The `region` dropdown lists every reachable region known to the pinned AWS SDK. */
    @Test
    fun testRegionEnumMatchesAwsSdk() {
        val spec: JsonNode = Jsons.readTree(ResourceUtils.readResource(EXPECTED_SPEC_RESOURCE))
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
     * so a configuration saved for `source-dynamodb` (access keys) loads unchanged.
     */
    @Test
    fun testLegacyAccessKeyConfigurationStillLoads() {
        val legacy: JsonNode = Jsons.readTree(ResourceUtils.readResource(LEGACY_SPEC_RESOURCE))
        val legacyProperties: Set<String> =
            legacy["connectionSpecification"]["properties"].fieldNames().asSequence().toSet()
        val actual: JsonNode = Jsons.readTree(ResourceUtils.readResource(EXPECTED_SPEC_RESOURCE))
        val actualProperties: Set<String> =
            actual["connectionSpecification"]["properties"].fieldNames().asSequence().toSet()
        // Every legacy property still exists (new optional ones may be added).
        Assertions.assertTrue(
            actualProperties.containsAll(legacyProperties),
            "missing legacy properties: ${legacyProperties - actualProperties}",
        )

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

    companion object {
        const val EXPECTED_SPEC_RESOURCE = "expected-spec.json"
        const val LEGACY_SPEC_RESOURCE = "legacy-spec.json"
    }
}
