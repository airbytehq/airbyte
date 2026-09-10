/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * `expected-spec.json` is the `spec` output of the published legacy `airbyte/source-mongodb-v2`
 * image. The two connectors must keep advertising the same spec.
 */
class MongoDbSourceSpecTest {

    @Test
    fun testSpecMatchesLegacyConnector() {
        SyncsTestFixture.testSpec(EXPECTED_SPEC_RESOURCE)
    }

    /** Stricter than [SyncsTestFixture.testSpec]: whole-tree equality, including array order. */
    @Test
    fun testSpecIsIdenticalToLegacyConnector() {
        val expected: JsonNode = Jsons.readTree(ResourceUtils.readResource(EXPECTED_SPEC_RESOURCE))
        val actualSpec: ConnectorSpecification = CliRunner.source("spec").run().specs().last()
        val actual: JsonNode = Jsons.valueToTree(actualSpec)
        Assertions.assertEquals(expected, actual, Jsons.writeValueAsString(actual))
    }

    companion object {
        const val EXPECTED_SPEC_RESOURCE = "expected-spec.json"
    }
}
