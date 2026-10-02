/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.spec

import io.airbyte.cdk.command.ValidatedJsonUtils
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

internal class SnowflakeHostSpecificationTest {
    @ParameterizedTest
    @ValueSource(strings = ["com", "cn", "mil"])
    fun generatedHostPatternAcceptsSupportedSnowflakeDomains(domain: String) {
        listOf(
                "account",
                "orgname-account_name",
                "account.cn-northwest-1.aws",
                "orgname-account_name.privatelink",
                "account.cn-northwest-1.aws.privatelink",
            )
            .forEach { account ->
                listOf("", "https://").forEach { prefix ->
                    val host = "$prefix$account.snowflakecomputing.$domain"
                    assertTrue(hostPattern.containsMatchIn(host), "Host schema rejected $host")
                }
            }
    }

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "account.localstack.cloud",
                "http://account.localstack.cloud",
                "http://account.snowflakecomputing.com",
            ]
    )
    fun generatedHostPatternPreservesExistingFormats(host: String) {
        // The shared schema also serves existing authentication methods. WIF independently
        // rejects HTTP and local emulator hosts before acquiring credentials.
        assertTrue(hostPattern.containsMatchIn(host), "Host schema rejected $host")
    }

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "account.snowflakecomputing.cn.attacker.invalid",
                "account.snowflakecomputing.mil.attacker.invalid",
                "notsnowflakecomputing.cn",
                "notsnowflakecomputing.mil",
                "account.snowflakecomputing.invalid",
                "snowflakecomputing.cn",
                "snowflakecomputing.mil",
                "https://account.snowflakecomputing.cn/path",
                "account.snowflakecomputing.cn?ssl=false",
            ]
    )
    fun generatedHostPatternRejectsUnsupportedDomainsAndUrls(host: String) {
        assertFalse(hostPattern.containsMatchIn(host), "Host schema accepted $host")
    }

    companion object {
        private val hostPattern: Regex by lazy {
            val schema =
                ValidatedJsonUtils.generateAirbyteJsonSchema(SnowflakeSpecification::class.java)
            val pattern = schema.path("properties").path("host").path("pattern")
            assertTrue(pattern.isTextual && pattern.asText().isNotBlank())
            Regex(pattern.asText())
        }
    }
}
