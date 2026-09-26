/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.spec

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.integrations.destination.snowflake.SnowflakeBeanFactory
import io.airbyte.integrations.destination.snowflake.auth.SnowflakeWorkloadIdentityDataSource
import io.airbyte.integrations.destination.snowflake.auth.WorkloadIdentityProvider
import io.airbyte.integrations.destination.snowflake.cdk.SnowflakeMigratingConfigurationSpecificationSupplier
import java.util.Properties
import net.snowflake.client.jdbc.SnowflakeConnectString
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource
import org.junit.jupiter.params.provider.ValueSource

internal class SnowflakeWorkloadIdentityConfigurationTest {
    @ParameterizedTest
    @EnumSource(WorkloadIdentityProvider::class)
    fun parsesEveryProviderAndBuildsPoolWithoutReadingCredentials(
        provider: WorkloadIdentityProvider
    ) {
        val extra =
            when (provider) {
                WorkloadIdentityProvider.OIDC -> ",\"token_file_path\":\"/not-mounted-yet/token\""
                WorkloadIdentityProvider.AZURE -> ",\"entra_resource\":\"api://test-resource\""
                else -> ""
            }
        val configuration =
            configuration(
                """{"auth_type":"Workload Identity Federation","workload_identity_provider":"$provider"$extra}"""
            )
        val auth =
            assertInstanceOf(WorkloadIdentityAuthConfiguration::class.java, configuration.authType)
        assertEquals(provider, auth.provider)
        assertEquals(
            if (provider == WorkloadIdentityProvider.OIDC) "/not-mounted-yet/token" else null,
            auth.tokenFilePath
        )
        assertEquals(
            if (provider == WorkloadIdentityProvider.AZURE) "api://test-resource" else null,
            auth.entraResource
        )
        SnowflakeBeanFactory().snowflakeDataSource(configuration, "COMMUNITY").use { pool ->
            assertInstanceOf(SnowflakeWorkloadIdentityDataSource::class.java, pool.dataSource)
            assertNull(pool.username)
            assertNull(pool.password)
            assertNull(pool.jdbcUrl)
            assertNull(pool.driverClassName)
            assertFalse(pool.dataSourceProperties.containsKey("token"))
            assertFalse(pool.dataSourceProperties.containsKey("private_key_file"))
            assertEquals("AIRBYTE_WH", pool.dataSourceProperties["warehouse"])
            assertEquals("AIRBYTE_DB", pool.dataSourceProperties["database"])
            assertEquals("AIRBYTE_ROLE", pool.dataSourceProperties["role"])
            assertEquals("airbyte_community", pool.dataSourceProperties["application"])
            assertEquals("JSON", pool.dataSourceProperties["JDBC_QUERY_RESULT_FORMAT"])
            assertEquals("true", pool.dataSourceProperties["ABORT_DETACHED_QUERY"])
        }
    }

    @Test
    fun generatedSpecExposesWifAlongsideExistingCredentials() {
        val schema =
            ValidatedJsonUtils.generateAirbyteJsonSchema(SnowflakeSpecification::class.java)
        val json = schema.toString()
        listOf(
                "Workload Identity Federation",
                "Key Pair Authentication",
                "Username and Password",
                "workload_identity_provider",
                "token_file_path",
                "entra_resource",
                "AWS",
                "AZURE",
                "GCP",
                "OIDC"
            )
            .forEach { assertTrue(json.contains(it), "Generated schema is missing $it") }
        // findValues("properties") stops descending when it finds the root properties object.
        val credentialOptions = schema.path("properties").path("credentials").path("oneOf")
        assertTrue(credentialOptions.isArray)
        val wifProperties =
            credentialOptions
                .map { it.path("properties") }
                .single { it.has("workload_identity_provider") }
        assertTrue(wifProperties.has("token_file_path"))
        assertTrue(wifProperties.has("entra_resource"))
        assertFalse(wifProperties.has("password"))
        assertFalse(wifProperties.has("private_key"))
        assertFalse(wifProperties.has("token"))
    }

    @Test
    fun requiresExplicitProvider() {
        assertThrows<ConfigErrorException> {
            configuration("""{"auth_type":"Workload Identity Federation"}""")
        }
    }

    @ParameterizedTest
    @ValueSource(strings = ["", " ", "relative/token"])
    fun rejectsMissingOrRelativeOidcPath(path: String) {
        assertThrows<ConfigErrorException> {
            configuration(
                """{"auth_type":"Workload Identity Federation","workload_identity_provider":"OIDC","token_file_path":"$path"}"""
            )
        }
    }

    @Test
    fun rejectsAbsentOidcPath() {
        assertThrows<ConfigErrorException> {
            configuration(
                """{"auth_type":"Workload Identity Federation","workload_identity_provider":"OIDC"}"""
            )
        }
    }

    @Test
    fun rejectsProviderSpecificFieldsForOtherProviders() {
        assertThrows<ConfigErrorException> {
            configuration(
                """{"auth_type":"Workload Identity Federation","workload_identity_provider":"AWS","token_file_path":"/token"}"""
            )
        }
        assertThrows<ConfigErrorException> {
            configuration(
                """{"auth_type":"Workload Identity Federation","workload_identity_provider":"GCP","entra_resource":"api://resource"}"""
            )
        }
        assertThrows<ConfigErrorException> {
            configuration(
                """{"auth_type":"Workload Identity Federation","workload_identity_provider":"AZURE","entra_resource":""}"""
            )
        }
    }

    @Test
    fun conflictingUrlCredentialsAreReportedAsConfigurationErrors() {
        val config =
            configuration(
                """{"auth_type":"Workload Identity Federation","workload_identity_provider":"AWS"}"""
            )
        val error =
            assertThrows<ConfigErrorException> {
                SnowflakeBeanFactory()
                    .snowflakeDataSource(
                        config.copy(jdbcUrlParams = "password=never-log-this"),
                        "COMMUNITY"
                    )
            }
        assertFalse(error.message.orEmpty().contains("never-log-this"))
    }

    @Test
    fun existingAuthenticationTypesStillDeserialize() {
        val password =
            configuration("""{"auth_type":"Username and Password","password":"test-password"}""")
        assertEquals(UsernamePasswordAuthConfiguration("test-password"), password.authType)
        val key =
            configuration(
                """{"auth_type":"Key Pair Authentication","private_key":"test-key","private_key_password":"test-passphrase"}"""
            )
        assertEquals(KeyPairAuthConfiguration("test-key", "test-passphrase"), key.authType)
    }

    @Test
    fun awsStsPackagingDependencyIsPresent() {
        // Packaging check only: this does not validate IRSA token exchange or refresh.
        Class.forName("com.amazonaws.services.securitytoken.AWSSecurityTokenService")
    }

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "http://example.snowflakecomputing.com",
                "never-log-this.invalid",
                "example.snowflakecomputing.com.never-log-this.invalid",
                "never-log-this@example.snowflakecomputing.com",
                "example.localstack.cloud"
            ]
    )
    fun runtimeRejectsUntrustedHostsWithoutDependingOnFormSchema(host: String) {
        val config =
            configuration(
                """{"auth_type":"Workload Identity Federation","workload_identity_provider":"OIDC","token_file_path":"/not-mounted-yet/token"}""",
                host
            )
        val error =
            assertThrows<ConfigErrorException> {
                SnowflakeBeanFactory().snowflakeDataSource(config, "COMMUNITY")
            }
        assertFalse(error.message.orEmpty().contains("never-log-this"))
    }

    @ParameterizedTest
    @ValueSource(
        strings = ["ssl=false", "SSL=off", "%73sl=false", "ssl=false&ssl=true", "protocol=http"]
    )
    fun runtimeRejectsHttpParameters(params: String) {
        val config =
            configuration(
                    """{"auth_type":"Workload Identity Federation","workload_identity_provider":"AWS"}"""
                )
                .copy(jdbcUrlParams = params)
        assertThrows<ConfigErrorException> {
            SnowflakeBeanFactory().snowflakeDataSource(config, "COMMUNITY")
        }
    }

    @ParameterizedTest
    @ValueSource(
        strings =
            [
                "orgname-account_name.snowflakecomputing.com",
                "https://orgname-account_name.snowflakecomputing.com",
                "orgname-account_name.privatelink.snowflakecomputing.com"
            ]
    )
    fun acceptsUnderscoreHostsAndPinnedDriverResolvesHttps(host: String) {
        val config =
            configuration(
                """{"auth_type":"Workload Identity Federation","workload_identity_provider":"OIDC","token_file_path":"/not-mounted-yet/token"}""",
                host
            )
        SnowflakeBeanFactory().snowflakeDataSource(config, "COMMUNITY").use { pool ->
            assertInstanceOf(SnowflakeWorkloadIdentityDataSource::class.java, pool.dataSource)
        }
        val parsed = SnowflakeConnectString.parse("jdbc:snowflake://$host/?", Properties())
        assertTrue(parsed.isValid)
        assertEquals("https", parsed.scheme)
        assertEquals("orgname-account_name", parsed.account)
        assertTrue(parsed.host.startsWith("orgname-account-name."))
        assertTrue(parsed.host.endsWith(".snowflakecomputing.com"))
    }

    private fun configuration(
        credentials: String,
        host: String = "example.snowflakecomputing.com"
    ): SnowflakeConfiguration {
        val json =
            """{
            "host":"$host",
            "username":"AIRBYTE_USER",
            "role":"AIRBYTE_ROLE",
            "warehouse":"AIRBYTE_WH",
            "database":"AIRBYTE_DB",
            "schema":"PUBLIC",
            "credentials":$credentials
        }"""
        val spec = SnowflakeMigratingConfigurationSpecificationSupplier(json).get()
        return SnowflakeConfigurationFactory().makeWithoutExceptionHandling(spec)
    }
}
