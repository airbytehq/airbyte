/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.cdk

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.integrations.destination.snowflake.spec.CredentialsSpecification
import io.airbyte.integrations.destination.snowflake.spec.KeyPairAuthSpecification
import io.airbyte.integrations.destination.snowflake.spec.UsernamePasswordAuthSpecification
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

internal class SnowflakeMigratingConfigurationSpecificationSupplierTest {

    @Test
    fun testCredentialsWithMissingAuthType() {
        val json =
            this.javaClass.getResource("/config_without_credentials_auth_type.json")!!.readText()

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        assertDoesNotThrow {
            val spec = supplier.get()
            assertEquals(
                CredentialsSpecification.Type.USERNAME_PASSWORD,
                spec.credentials?.auth_type
            )
            assertEquals(
                "test-password",
                ((spec.credentials) as UsernamePasswordAuthSpecification).password
            )
        }
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
        assertDoesNotThrow {
            val spec = supplier.get()
            assertEquals(
                CredentialsSpecification.Type.USERNAME_PASSWORD,
                spec.credentials?.auth_type
            )
            assertEquals(
                "test-password",
                ((spec.credentials) as UsernamePasswordAuthSpecification).password
            )
        }
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
        assertDoesNotThrow {
            val spec = supplier.get()
            assertEquals(
                CredentialsSpecification.Type.USERNAME_PASSWORD,
                spec.credentials?.auth_type
            )
            assertEquals(UsernamePasswordAuthSpecification::class.java, spec.credentials?.javaClass)
            assertEquals(
                "test-password",
                ((spec.credentials) as UsernamePasswordAuthSpecification).password
            )
        }
    }

    @Test
    fun testCredentialsWithTopLevelPasswordFlat() {
        val json =
            unprettyPrintJson(
                this.javaClass.getResource("/config_with_top_level_password.json")!!.readText()
            )

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        assertDoesNotThrow {
            val spec = supplier.get()
            assertEquals(
                CredentialsSpecification.Type.USERNAME_PASSWORD,
                spec.credentials?.auth_type
            )
            assertEquals(UsernamePasswordAuthSpecification::class.java, spec.credentials?.javaClass)
            assertEquals(
                "test-password",
                ((spec.credentials) as UsernamePasswordAuthSpecification).password
            )
        }
    }

    @Test
    fun testCredentialsWithAuthType() {
        val json =
            this.javaClass.getResource("/config_with_credentials_auth_type.json")!!.readText()

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        assertDoesNotThrow {
            val spec = supplier.get()
            assertEquals(
                CredentialsSpecification.Type.USERNAME_PASSWORD,
                spec.credentials?.auth_type
            )
            assertEquals(
                "test-password",
                ((spec.credentials) as UsernamePasswordAuthSpecification).password
            )
        }
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
        val json =
            unprettyPrintJson(
                this.javaClass.getResource("/config_with_credentials_auth_type.json")!!.readText()
            )

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        assertDoesNotThrow {
            val spec = supplier.get()
            assertEquals(
                CredentialsSpecification.Type.USERNAME_PASSWORD,
                spec.credentials?.auth_type
            )
        }
    }

    @Test
    fun testInvalidJson() {
        val json = """{ "invalid" : "json""""

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)

        assertThrows<ConfigErrorException> { supplier.get() }
    }

    private fun unprettyPrintJson(json: String) =
        json
            .replace("\n", "")
            .replace("\\s*:\\s*".toRegex(), ":")
            .replace(",\\s*".toRegex(), ",")
            .replace("\\{\\s*".toRegex(), "{")
            .replace("\\s*}".toRegex(), "}")
}
