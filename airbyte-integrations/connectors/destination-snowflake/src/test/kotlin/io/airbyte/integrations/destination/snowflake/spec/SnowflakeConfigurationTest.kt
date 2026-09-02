/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.spec

import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

internal class SnowflakeConfigurationTest {

    @Test
    fun testOAuthSpecificationMapsToConfiguration() {
        val specification =
            Jsons.readValue(
                """
                {
                  "credentials": {
                    "auth_type": "OAuth2.0",
                    "client_id": "test-client-id",
                    "client_secret": "test-client-secret",
                    "refresh_token": "test-refresh-token"
                  }
                }
                """.trimIndent(),
                SnowflakeSpecification::class.java,
            )

        val configuration =
            SnowflakeConfigurationFactory().makeWithoutExceptionHandling(specification)

        assertEquals(
            OAuthAuthConfiguration(
                clientId = "test-client-id",
                clientSecret = "test-client-secret",
                refreshToken = "test-refresh-token",
                accessToken = null,
            ),
            configuration.authType,
        )
    }

    @Test
    fun testOAuthSpecificationDeserializesFromJson() {
        val specification =
            Jsons.readValue(
                """
                {
                  "credentials": {
                    "auth_type": "OAuth2.0",
                    "client_id": "test-client-id",
                    "client_secret": "test-client-secret",
                    "refresh_token": "test-refresh-token"
                  }
                }
                """.trimIndent(),
                SnowflakeSpecification::class.java,
            )

        assertEquals(OAuthSpecification::class.java, specification.credentials?.javaClass)
        val credentials = specification.credentials as OAuthSpecification
        assertEquals("test-client-id", credentials.clientId)
        assertEquals("test-client-secret", credentials.clientSecret)
        assertEquals("test-refresh-token", credentials.refreshToken)
        assertEquals(null, credentials.accessToken)
    }
}
