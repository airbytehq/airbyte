/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.cdk

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.snowflake.spec.CredentialsSpecification
import io.airbyte.integrations.destination.snowflake.spec.KeyPairAuthSpecification
import io.airbyte.integrations.destination.snowflake.spec.NumberDataType
import io.airbyte.integrations.destination.snowflake.spec.ProgrammaticAccessTokenAuthConfiguration
import io.airbyte.integrations.destination.snowflake.spec.ProgrammaticAccessTokenAuthSpecification
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfigurationFactory
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import io.airbyte.integrations.destination.snowflake.spec.UsernamePasswordAuthSpecification
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

internal class SnowflakeMigratingConfigurationSpecificationSupplierTest {

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "account.snowflakecomputing.com",
                "org-account.snowflakecomputing.com",
                "account.us-east-2.aws.snowflakecomputing.com",
                "account.us-east-1.privatelink.snowflakecomputing.com",
                "account.localstack.cloud",
                "account.proxy.example.com",
                "proxy.example.org",
                "a.b.c.d.e.f.example.net",
            ]
    )
    fun testHostDomains(host: String) {
        val supplier = SnowflakeMigratingConfigurationSpecificationSupplier()
        val hostPattern = supplier.jsonSchema["properties"]["host"]["pattern"].asText().toRegex()
        for (prefix in listOf("", "http://", "https://")) { // # ignore-https-check
            val endpoint = prefix + host
            assertTrue(hostPattern.matches(endpoint), endpoint)
            for (fixture in
                listOf(
                    "config_with_credentials_auth_type.json",
                    "config_with_credentials_auth_type_key_pair.json",
                    "config_with_credentials_auth_type_pat.json",
                    "config_with_top_level_password.json",
                    "config_without_credentials_auth_type.json",
                    "config_without_credentials_auth_type_key_pair.json",
                )) {
                val json = this.javaClass.getResource("/$fixture")!!.readText()
                val configuration = Jsons.readTree(json).deepCopy<ObjectNode>()
                configuration.put("host", endpoint)
                val migrated = migrateJson(Jsons.writeValueAsString(configuration))
                val spec = ValidatedJsonUtils.parseOne(SnowflakeSpecification::class.java, migrated)
                assertEquals(
                    endpoint,
                    SnowflakeConfigurationFactory().makeWithoutExceptionHandling(spec).host
                )
            }
        }
    }

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "",
                "https://",
                ".example.com",
                "proxy..example.com",
                "proxy.example.com/path",
                "proxy.example.com?query=value",
                "proxy.example.com#fragment",
            ]
    )
    fun testInvalidHost(host: String) {
        val json =
            this.javaClass.getResource("/config_with_credentials_auth_type.json")!!.readText()
        val configuration = Jsons.readTree(json).deepCopy<ObjectNode>()
        configuration.put("host", host)
        assertThrows<ConfigErrorException> {
            ValidatedJsonUtils.parseOne(
                SnowflakeSpecification::class.java,
                Jsons.writeValueAsString(configuration)
            )
        }
    }

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
    fun testCredentialsWithAuthTypeProgrammaticAccessToken() {
        val json =
            this.javaClass.getResource("/config_with_credentials_auth_type_pat.json")!!.readText()

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        assertDoesNotThrow {
            val spec = supplier.get()
            assertEquals(
                CredentialsSpecification.Type.PROGRAMMATIC_ACCESS_TOKEN,
                spec.credentials?.auth_type
            )
            assertEquals(
                ProgrammaticAccessTokenAuthSpecification::class.java,
                spec.credentials?.javaClass
            )
            assertEquals(
                "test-programmatic-access-token",
                ((spec.credentials) as ProgrammaticAccessTokenAuthSpecification)
                    .programmaticAccessToken
            )

            val config = SnowflakeConfigurationFactory().makeWithoutExceptionHandling(spec)
            assertEquals(
                ProgrammaticAccessTokenAuthConfiguration("test-programmatic-access-token"),
                config.authType
            )
        }
    }

    @Test
    fun testCredentialsWithAuthTypeProgrammaticAccessTokenFlat() {
        val json =
            unprettyPrintJson(
                this.javaClass
                    .getResource("/config_with_credentials_auth_type_pat.json")!!
                    .readText()
            )

        val supplier =
            SnowflakeMigratingConfigurationSpecificationSupplier(jsonPropertyValue = json)
        assertDoesNotThrow {
            val spec = supplier.get()
            assertEquals(
                CredentialsSpecification.Type.PROGRAMMATIC_ACCESS_TOKEN,
                spec.credentials?.auth_type
            )
            assertEquals(
                "test-programmatic-access-token",
                ((spec.credentials) as ProgrammaticAccessTokenAuthSpecification)
                    .programmaticAccessToken
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
    fun testNumberDataTypeDefaultsToFloatWhenAbsentFromConfig() {
        // Missing `number_data_type` parses as null and defaults to FLOAT.
        val json =
            unprettyPrintJson(
                this.javaClass.getResource("/config_with_credentials_auth_type.json")!!.readText()
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

    private fun unprettyPrintJson(json: String) =
        json
            .replace("\n", "")
            .replace("\\s*:\\s*".toRegex(), ":")
            .replace(",\\s*".toRegex(), ",")
            .replace("\\{\\s*".toRegex(), "{")
            .replace("\\s*}".toRegex(), "}")
}
