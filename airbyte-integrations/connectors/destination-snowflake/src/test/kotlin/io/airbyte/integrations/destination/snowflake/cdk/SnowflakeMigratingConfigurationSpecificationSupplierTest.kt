/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.cdk

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.integrations.destination.snowflake.spec.CredentialsSpecification
import io.airbyte.integrations.destination.snowflake.spec.KeyPairAuthSpecification
import io.airbyte.integrations.destination.snowflake.spec.NumberDataType
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfigurationFactory
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import io.airbyte.integrations.destination.snowflake.spec.USERNAME_PASSWORD_AUTH_TYPE
import io.airbyte.integrations.destination.snowflake.spec.USERNAME_PASSWORD_REMOVED_MESSAGE
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

internal class SnowflakeMigratingConfigurationSpecificationSupplierTest {

    @Test
    fun testCredentialsWithMissingAuthType() {
        val json =
            this.javaClass.getResource("/config_without_credentials_auth_type.json")!!.readText()

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        assertAuthenticationRemoved(supplier)
    }

    @Test
    fun testCredentialsWithMissingAuthTypeFlat() {
        val json =
            unprettyPrintJson(
                this.javaClass
                    .getResource("/config_without_credentials_auth_type.json")!!
                    .readText()
            )

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        assertAuthenticationRemoved(supplier)
    }

    @Test
    fun testCredentialsWithMissingAuthTypeKeyPair() {
        val json =
            this.javaClass
                .getResource("/config_without_credentials_auth_type_key_pair.json")!!
                .readText()

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        assertDoesNotThrow {
            val spec = supplier.get()
            assertEquals(CredentialsSpecification.Type.PRIVATE_KEY, spec.credentials?.auth_type)
            assertEquals(
                "test-private-key",
                ((spec.credentials) as KeyPairAuthSpecification).privateKey
            )
        }
    }

    @Test
    fun testCredentialsWithMissingAuthTypeKeyPairFlat() {
        val json =
            unprettyPrintJson(
                this.javaClass
                    .getResource("/config_without_credentials_auth_type_key_pair.json")!!
                    .readText()
            )

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        assertDoesNotThrow {
            val spec = supplier.get()
            assertEquals(CredentialsSpecification.Type.PRIVATE_KEY, spec.credentials?.auth_type)
            assertEquals(
                "test-private-key",
                ((spec.credentials) as KeyPairAuthSpecification).privateKey
            )
        }
    }

    @Test
    fun testCredentialsWithTopLevelPassword() {
        val json = this.javaClass.getResource("/config_with_top_level_password.json")!!.readText()

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        assertAuthenticationRemoved(supplier)
    }

    @Test
    fun testCredentialsWithTopLevelPasswordFlat() {
        val json =
            unprettyPrintJson(
                this.javaClass.getResource("/config_with_top_level_password.json")!!.readText()
            )

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        assertAuthenticationRemoved(supplier)
    }

    @Test
    fun testCredentialsWithAuthType() {
        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(
                jsonPropertyValue = usernamePasswordJson()
            )
        assertAuthenticationRemoved(supplier)
    }

    @Test
    fun testCredentialsWithAuthTypeKeyPair() {
        val json =
            this.javaClass
                .getResource("/config_with_credentials_auth_type_key_pair.json")!!
                .readText()

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        assertDoesNotThrow {
            val spec = supplier.get()
            assertEquals(CredentialsSpecification.Type.PRIVATE_KEY, spec.credentials?.auth_type)
            assertEquals(
                "test-private-key",
                ((spec.credentials) as KeyPairAuthSpecification).privateKey
            )
        }
    }

    @Test
    fun testCredentialsWithAuthTypeFlat() {
        val json = unprettyPrintJson(usernamePasswordJson())

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        assertAuthenticationRemoved(supplier)
    }

    @Test
    fun testNumberDataTypeDefaultsToFloatWhenAbsentFromConfig() {
        // Missing `number_data_type` parses as null and defaults to FLOAT.
        val json =
            unprettyPrintJson(
                this.javaClass
                    .getResource("/config_with_credentials_auth_type_key_pair.json")!!
                    .readText()
            )

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        val spec = supplier.get()
        assertNull(spec.numberDataTypeConversion)

        val config = SnowflakeConfigurationFactory().makeWithoutExceptionHandling(spec)
        assertEquals(NumberDataType.FLOAT, config.numberDataTypeConversion)
    }

    @Test
    fun testNumberDataTypeParsedFromConfig() {
        val json =
            unprettyPrintJson(
                this.javaClass.getResource("/config_with_number_data_type.json")!!.readText()
            )

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        val spec = supplier.get()
        assertEquals(NumberDataType.NUMBER_38_9, spec.numberDataTypeConversion)

        val config = SnowflakeConfigurationFactory().makeWithoutExceptionHandling(spec)
        assertEquals(NumberDataType.NUMBER_38_9, config.numberDataTypeConversion)
    }

    @Test
    fun testInvalidJson() {
        val json = """{ "invalid" : "json""""

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)

        assertThrows<ConfigErrorException> { supplier.get() }
    }

    @Test
    fun testMissingCredentials() {
        val exception =
            assertThrows<ConfigErrorException> {
                SnowflakeConfigurationFactory()
                    .makeWithoutExceptionHandling(SnowflakeSpecification())
            }
        assertEquals(USERNAME_PASSWORD_REMOVED_MESSAGE, exception.message)
    }

    private fun assertAuthenticationRemoved(
        supplier: SnowflakeMigratingConfigurationSpecificationSupplier
    ) {
        val exception = assertThrows<ConfigErrorException> { supplier.get() }
        assertEquals(USERNAME_PASSWORD_REMOVED_MESSAGE, exception.message)
    }

    private fun usernamePasswordJson() =
        """
        {
          "host": "testhost.snowflakecomputing.com",
          "role": "AIRBYTE_ROLE",
          "warehouse": "AIRBYTE_WAREHOUSE",
          "database": "AIRBYTE_DATABASE",
          "schema": "RESTRICTED_SCHEMA",
          "username": "AIRBYTE_USER",
          "credentials": {
            "auth_type": "$USERNAME_PASSWORD_AUTH_TYPE",
            "password": "test-password"
          }
        }
        """.trimIndent()

    private fun unprettyPrintJson(json: String) =
        json
            .replace("\n", "")
            .replace("\\s*:\\s*".toRegex(), ":")
            .replace(",\\s*".toRegex(), ",")
            .replace("\\{\\s*".toRegex(), "{")
            .replace("\\s*}".toRegex(), "}")
}
