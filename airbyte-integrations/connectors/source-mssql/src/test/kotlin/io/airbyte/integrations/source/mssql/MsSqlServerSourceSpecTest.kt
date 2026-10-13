/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mssql

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.CliRunner
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.protocol.models.v0.ConnectorSpecification
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

/**
 * The `spec` output depends on the deployment ([MsSqlServerSourceSpecificationExtender]): on
 * Airbyte Cloud (`AIRBYTE_EDITION=CLOUD`) the Encryption option defaults to
 * `encrypted_trust_server_certificate` and that option comes first; everywhere else the generated
 * spec is returned as is, with no `default` and `Unencrypted` first.
 */
class MsSqlServerSourceSpecTest {

    @Test
    fun testCloudDefaultsToEncryptedTrustServerCertificate() {
        val sslMode: JsonNode = sslMode(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT)
        Assertions.assertEquals(
            MsSqlServerSourceSpecificationExtender.CLOUD_DEFAULT_SSL_MODE,
            sslMode["default"]?.asText(),
            sslMode.toString(),
        )
        Assertions.assertEquals(
            listOf(
                "encrypted_trust_server_certificate",
                "unencrypted",
                "encrypted_verify_certificate",
            ),
            modes(sslMode),
        )
    }

    @Test
    fun testSelfManagedHasNoDefaultAndKeepsUnencryptedFirst() {
        val sslMode: JsonNode = sslMode()
        Assertions.assertNull(sslMode["default"], sslMode.toString())
        Assertions.assertEquals(
            listOf(
                "unencrypted",
                "encrypted_trust_server_certificate",
                "encrypted_verify_certificate",
            ),
            modes(sslMode),
        )
    }

    /** Nothing but the Encryption default and option order differs between the editions. */
    @Test
    fun testOnlyTheEncryptionDefaultDiffersBetweenEditions() {
        val cloud: ObjectNode =
            spec(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT).connectionSpecification as ObjectNode
        val selfManaged: ObjectNode = spec().connectionSpecification as ObjectNode
        Assertions.assertEquals(
            modes(selfManaged["properties"]["ssl_mode"]).toSet(),
            modes(cloud["properties"]["ssl_mode"]).toSet(),
        )
        for (schema in listOf(cloud, selfManaged)) {
            (schema["properties"] as ObjectNode).remove("ssl_mode")
        }
        Assertions.assertEquals(selfManaged, cloud)
    }

    private fun spec(vararg featureFlags: FeatureFlag): ConnectorSpecification =
        CliRunner.source("spec", null, null, null, *featureFlags).run().specs().last()

    private fun sslMode(vararg featureFlags: FeatureFlag): JsonNode =
        spec(*featureFlags).connectionSpecification["properties"]["ssl_mode"]

    private fun modes(sslMode: JsonNode): List<String?> =
        sslMode["oneOf"].map { MsSqlServerSourceSpecificationExtender.modeOf(it) }
}
