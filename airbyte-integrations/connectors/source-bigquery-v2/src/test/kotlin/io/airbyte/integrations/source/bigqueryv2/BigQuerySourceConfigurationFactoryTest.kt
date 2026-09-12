/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.util.Jsons
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class BigQuerySourceConfigurationFactoryTest {

    @AfterEach
    fun clearEmulatorProperty() {
        System.clearProperty(BigQueryEmulator.SYSTEM_PROPERTY)
    }

    private fun parse(json: String): BigQuerySourceConfigurationSpecification =
        Jsons.readValue(json, BigQuerySourceConfigurationSpecification::class.java)

    private fun make(json: String): BigQuerySourceConfiguration =
        BigQuerySourceConfigurationFactory().makeWithoutExceptionHandling(parse(json))

    private fun configJson(
        projectId: String? = "my-project",
        datasetId: String? = null,
        credentialsJson: String? = SERVICE_ACCOUNT_KEY,
    ): String {
        val node = Jsons.objectNode()
        projectId?.let { node.put("project_id", it) }
        datasetId?.let { node.put("dataset_id", it) }
        credentialsJson?.let { node.put("credentials_json", it) }
        return Jsons.writeValueAsString(node)
    }

    @Test
    fun testMinimalConfiguration() {
        val config: BigQuerySourceConfiguration = make(configJson())
        Assertions.assertEquals("my-project", config.projectId)
        Assertions.assertNull(config.datasetId)
        Assertions.assertEquals(emptySet<String>(), config.namespaces)
        Assertions.assertNull(config.emulatorHost)
        Assertions.assertEquals(SERVICE_ACCOUNT_KEY, config.credentialsJson)
        Assertions.assertEquals(
            "jdbc:bigquery://https://www.googleapis.com/bigquery/v2:443;ProjectId=my-project;OAuthType=0",
            String.format(config.jdbcUrlFmt, config.realHost, config.realPort),
        )
        Assertions.assertEquals(
            mapOf("ProjectId" to "my-project", "OAuthPvtKey" to SERVICE_ACCOUNT_KEY),
            config.jdbcProperties,
        )
        Assertions.assertEquals("www.googleapis.com", config.realHost)
        Assertions.assertEquals(443, config.realPort)
        Assertions.assertFalse(config.global)
        Assertions.assertFalse(config.checkPrivileges)
        Assertions.assertEquals(1, config.maxConcurrency)
        Assertions.assertNull(config.maxSnapshotReadDuration)
    }

    @Test
    fun testDatasetBecomesTheOnlyNamespace() {
        val config: BigQuerySourceConfiguration = make(configJson(datasetId = " my_dataset "))
        Assertions.assertEquals("my_dataset", config.datasetId)
        Assertions.assertEquals(setOf("my_dataset"), config.namespaces)
    }

    @Test
    fun testBlankDatasetMeansAllDatasets() {
        Assertions.assertEquals(emptySet<String>(), make(configJson(datasetId = "  ")).namespaces)
    }

    @Test
    fun testCredentialsAreNotInToStringNorInTheJdbcUrl() {
        val config: BigQuerySourceConfiguration = make(configJson())
        Assertions.assertFalse(config.toString().contains("PRIVATE KEY"), config.toString())
        Assertions.assertFalse(config.toString().contains("OAuthPvtKey=" + SERVICE_ACCOUNT_KEY))
        Assertions.assertFalse(config.jdbcUrlFmt.contains("PRIVATE KEY"))
    }

    @Test
    fun testMissingProjectId() {
        val e =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                make(configJson(projectId = null))
            }
        Assertions.assertEquals("Missing required 'project_id' property.", e.message)
        val blank =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                make(configJson(projectId = " "))
            }
        Assertions.assertEquals("Missing required 'project_id' property.", blank.message)
    }

    @Test
    fun testMissingCredentials() {
        val e =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                make(configJson(credentialsJson = null))
            }
        Assertions.assertEquals("Missing required 'credentials_json' property.", e.message)
    }

    @Test
    fun testCredentialsMustBeJson() {
        val e =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                make(configJson(credentialsJson = "not json"))
            }
        Assertions.assertTrue(
            e.message!!.startsWith("'credentials_json' is not valid JSON"),
            e.message
        )
    }

    @Test
    fun testCredentialsMustBeAServiceAccountKey() {
        val userKey =
            """{"type":"authorized_user","client_id":"x","client_secret":"y","refresh_token":"z"}"""
        val e =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                make(configJson(credentialsJson = userKey))
            }
        Assertions.assertEquals(
            "'credentials_json' must be a service account key (\"type\": \"service_account\"), got \"type\": \"authorized_user\".",
            e.message,
        )
        val array =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                make(configJson(credentialsJson = "[1,2]"))
            }
        Assertions.assertEquals("'credentials_json' must be a JSON object.", array.message)
    }

    @Test
    fun testCredentialsMustHaveEmailAndPrivateKey() {
        val e =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                make(
                    configJson(
                        credentialsJson = """{"type":"service_account","client_email":"a@b.c"}"""
                    )
                )
            }
        Assertions.assertEquals(
            "'credentials_json' is missing the 'private_key' property of a service account key.",
            e.message,
        )
    }

    @Test
    fun testMakeLetsConfigErrorsThrough() {
        val e =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                BigQuerySourceConfigurationFactory().make(parse(configJson(projectId = null)))
            }
        Assertions.assertEquals("Missing required 'project_id' property.", e.message)
    }

    @Test
    fun testEmulatorConfiguration() {
        System.setProperty(BigQueryEmulator.SYSTEM_PROPERTY, "http://localhost:9050/")
        val config: BigQuerySourceConfiguration = make(configJson(credentialsJson = "whatever"))
        Assertions.assertEquals("http://localhost:9050", config.emulatorHost)
        Assertions.assertEquals(
            "jdbc:bigquery://http://localhost:9050;ProjectId=my-project;OAuthType=2",
            String.format(config.jdbcUrlFmt, config.realHost, config.realPort),
        )
        Assertions.assertEquals(
            mapOf(
                "ProjectId" to "my-project",
                "OAuthAccessToken" to BigQueryEmulator.DUMMY_ACCESS_TOKEN,
                "EndpointOverrides" to "BIGQUERY=http://localhost:9050",
            ),
            config.jdbcProperties,
        )
    }

    companion object {
        val SERVICE_ACCOUNT_KEY: String =
            """
{
  "type": "service_account",
  "project_id": "my-project",
  "private_key_id": "abc",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIB\n-----END PRIVATE KEY-----\n",
  "client_email": "airbyte@my-project.iam.gserviceaccount.com",
  "client_id": "123",
  "token_uri": "https://oauth2.googleapis.com/token"
}
""".trim()
    }
}
