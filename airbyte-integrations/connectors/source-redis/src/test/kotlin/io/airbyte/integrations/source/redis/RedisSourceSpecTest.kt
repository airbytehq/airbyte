/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.redis

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class RedisSourceSpecTest {
    @Test
    fun testSpecMatchesSnapshot() {
        SyncsTestFixture.testSpec(EXPECTED_SPEC)
    }

    @Test
    fun testSpecIsIdenticalToSnapshotAndIncludesRedisConfigurationDecisions() {
        val actual: JsonNode =
            Jsons.valueToTree(CliRunner.source("spec", null).run().specs().last())
        val expected: JsonNode = Jsons.readTree(ResourceUtils.readResource(EXPECTED_SPEC))
        Assertions.assertEquals(
            expected,
            actual,
            Jsons.writerWithDefaultPrettyPrinter().writeValueAsString(actual),
        )

        val schema = actual["connectionSpecification"]
        Assertions.assertEquals(
            listOf("host", "port"),
            schema["required"].map(JsonNode::asText),
        )
        val properties = schema["properties"]
        Assertions.assertTrue(properties["password"]["airbyte_secret"].asBoolean())
        val sslMode = properties["ssl_mode"]
        val sslOptions = sslMode["oneOf"]
        Assertions.assertEquals(
            listOf("Disable", "Require", "Verify CA", "Verify Full"),
            sslOptions.map { it["title"].asText() },
        )
        Assertions.assertEquals(
            listOf("disable", "require", "verify-ca", "verify-full"),
            sslOptions.map { it["properties"]["mode"]["enum"][0].asText() },
        )
        for (option in sslOptions.drop(2)) {
            val sslProperties = option["properties"]
            for (notSecret in listOf("ca_certificate", "client_certificate")) {
                Assertions.assertFalse(sslProperties[notSecret].has("airbyte_secret"))
            }
            for (secret in listOf("client_key", "client_key_password")) {
                Assertions.assertTrue(sslProperties[secret]["airbyte_secret"].asBoolean())
            }
        }
        Assertions.assertEquals(6379, properties["port"]["default"].asInt())
        Assertions.assertEquals(0, properties["database"]["default"].asInt())
        Assertions.assertEquals("*", properties["key_pattern"]["default"].asText())
        Assertions.assertEquals(1000, properties["scan_batch_size"]["default"].asInt())
        Assertions.assertEquals(
            300,
            properties["checkpoint_target_interval_seconds"]["default"].asInt(),
        )
    }

    companion object {
        private const val EXPECTED_SPEC = "expected-spec.json"
    }
}
