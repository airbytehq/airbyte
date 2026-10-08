/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3.config

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * `expected-spec.json` is a snapshot of this connector's generated `spec`. It carries the legacy
 * `source-mongodb-v2` property names, titles, descriptions, defaults and `database_config` oneOf
 * (so saved v2 configurations keep loading), minus the two Debezium-only properties v3 drops
 * (`initial_waiting_seconds`, `queue_size`; see the `3.0.0` breaking change in `metadata.yaml`).
 * Rendering follows the Bulk CDK schema generator like every other Bulk CDK source (`"type":
 * "object"` on oneOf variants, discriminators as a single-value `enum` + `default`, no
 * `changelogUrl`) rather than v2's hand-written `spec.json`.
 */
class MongoDbSourceSpecTest {

    @Test
    fun testSpecMatchesExpected() {
        SyncsTestFixture.testSpec(EXPECTED_SPEC_RESOURCE)
    }

    /** Stricter than [SyncsTestFixture.testSpec]: whole-tree equality, including array order. */
    @Test
    fun testSpecIsIdenticalToExpected() {
        val expected: JsonNode = Jsons.readTree(ResourceUtils.readResource(EXPECTED_SPEC_RESOURCE))
        val actualSpec: ConnectorSpecification = CliRunner.source("spec").run().specs().last()
        val actual: JsonNode = Jsons.valueToTree(actualSpec)
        Assertions.assertEquals(expected, actual, Jsons.writeValueAsString(actual))
    }

    companion object {
        const val EXPECTED_SPEC_RESOURCE = "expected-spec.json"
    }
}
