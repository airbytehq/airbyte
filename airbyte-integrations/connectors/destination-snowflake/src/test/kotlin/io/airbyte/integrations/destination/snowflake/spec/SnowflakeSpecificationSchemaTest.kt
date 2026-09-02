/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.spec

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ValidatedJsonUtils
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

internal class SnowflakeSpecificationSchemaTest {

    @Test
    fun testKeyPairConfigurationIsValid() {
        assertDoesNotThrow {
            ValidatedJsonUtils.parseOne(SnowflakeSpecification::class.java, keyPairConfiguration())
        }
    }

    @Test
    fun testRootLevelPasswordIsInvalid() {
        assertThrows<ConfigErrorException> {
            ValidatedJsonUtils.parseOne(
                SnowflakeSpecification::class.java,
                baseConfiguration("\"password\": \"test-password\""),
            )
        }
    }

    @Test
    fun testUsernamePasswordCredentialsAreInvalid() {
        assertThrows<ConfigErrorException> {
            ValidatedJsonUtils.parseOne(
                SnowflakeSpecification::class.java,
                baseConfiguration(
                    """
                    "credentials": {
                      "auth_type": "Username and Password",
                      "password": "test-password"
                    }
                    """.trimIndent()
                ),
            )
        }
    }

    private fun keyPairConfiguration(): String =
        baseConfiguration(
            """
            "credentials": {
              "auth_type": "Key Pair Authentication",
              "private_key": "test-private-key"
            }
            """.trimIndent()
        )

    private fun baseConfiguration(authentication: String): String =
        """
        {
          "host": "testhost.snowflakecomputing.com",
          "role": "AIRBYTE_ROLE",
          "warehouse": "AIRBYTE_WAREHOUSE",
          "database": "AIRBYTE_DATABASE",
          "schema": "RESTRICTED_SCHEMA",
          "username": "AIRBYTE_USER",
          $authentication
        }
        """.trimIndent()
}
