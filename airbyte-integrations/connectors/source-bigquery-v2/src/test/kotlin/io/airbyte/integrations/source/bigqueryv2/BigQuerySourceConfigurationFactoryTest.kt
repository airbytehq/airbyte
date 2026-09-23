/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.bigqueryv2.readapi.BigQueryReadApiAvailability
import java.security.KeyPairGenerator
import java.util.Base64
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
        jobProjectId: String? = null,
        maxDbConnections: Int? = null,
        useStorageReadApi: Boolean? = null,
    ): String {
        val node = Jsons.objectNode()
        projectId?.let { node.put("project_id", it) }
        datasetId?.let { node.put("dataset_id", it) }
        credentialsJson?.let { node.put("credentials_json", it) }
        jobProjectId?.let { node.put("job_project_id", it) }
        maxDbConnections?.let { node.put("max_db_connections", it) }
        useStorageReadApi?.let { node.put("use_storage_read_api", it) }
        return Jsons.writeValueAsString(node)
    }

    @Test
    fun testMinimalConfiguration() {
        val config: BigQuerySourceConfiguration = make(configJson())
        Assertions.assertEquals("my-project", config.projectId)
        Assertions.assertNull(config.datasetId)
        Assertions.assertEquals(emptySet<String>(), config.namespaces)
        // Jobs run in the data project unless 'job_project_id' says otherwise.
        Assertions.assertEquals("my-project", config.jobProjectId)
        Assertions.assertNull(config.emulatorHost)
        Assertions.assertEquals(SERVICE_ACCOUNT_KEY, config.credentialsJson)
        Assertions.assertEquals(
            "jdbc:bigquery://https://www.googleapis.com/bigquery/v2:443;ProjectId=my-project;OAuthType=0",
            String.format(config.jdbcUrlFmt, config.realHost, config.realPort),
        )
        Assertions.assertEquals(
            mapOf(
                "ProjectId" to "my-project",
                "OAuthServiceAcctEmail" to "airbyte@my-project.iam.gserviceaccount.com",
                "OAuthPvtKey" to PRIVATE_KEY_PEM,
                // The Storage Read API is on by default, for the read path and for the driver.
                "EnableHighThroughputAPI" to "1",
            ),
            config.jdbcProperties,
        )
        Assertions.assertEquals("www.googleapis.com", config.realHost)
        Assertions.assertEquals(443, config.realPort)
        Assertions.assertFalse(config.global)
        Assertions.assertFalse(config.checkPrivileges)
        Assertions.assertEquals(1, config.maxConcurrency)
        Assertions.assertNull(config.maxSnapshotReadDuration)
        Assertions.assertTrue(config.useStorageReadApi)
    }

    @Test
    fun testConcurrencyFollowsTheSocketCountInSpeedMode() {
        val spec: BigQuerySourceConfigurationSpecification = parse(configJson())
        val stdio =
            BigQuerySourceConfigurationFactory(
                dataChannelMedium = "STDIO",
                socketPaths = emptyList()
            )
        Assertions.assertEquals(1, stdio.makeWithoutExceptionHandling(spec).maxConcurrency)
        val sockets =
            BigQuerySourceConfigurationFactory(
                dataChannelMedium = "SOCKET",
                socketPaths = listOf("/tmp/s1.sock", "/tmp/s2.sock", "/tmp/s3.sock"),
            )
        Assertions.assertEquals(3, sockets.makeWithoutExceptionHandling(spec).maxConcurrency)
        // A socket medium without any path still yields a usable configuration.
        val noSockets =
            BigQuerySourceConfigurationFactory(
                dataChannelMedium = "SOCKET",
                socketPaths = emptyList()
            )
        Assertions.assertEquals(1, noSockets.makeWithoutExceptionHandling(spec).maxConcurrency)
    }

    @Test
    fun testMaxDbConnectionsOverridesTheDefaultConcurrency() {
        val stdio =
            BigQuerySourceConfigurationFactory(
                dataChannelMedium = "STDIO",
                socketPaths = emptyList()
            )
        Assertions.assertEquals(
            4,
            stdio
                .makeWithoutExceptionHandling(parse(configJson(maxDbConnections = 4)))
                .maxConcurrency,
        )
        val sockets =
            BigQuerySourceConfigurationFactory(
                dataChannelMedium = "SOCKET",
                socketPaths = listOf("/tmp/s1.sock", "/tmp/s2.sock", "/tmp/s3.sock"),
            )
        Assertions.assertEquals(
            2,
            sockets
                .makeWithoutExceptionHandling(parse(configJson(maxDbConnections = 2)))
                .maxConcurrency,
        )
        Assertions.assertEquals(
            5,
            sockets
                .makeWithoutExceptionHandling(parse(configJson(maxDbConnections = 5)))
                .maxConcurrency,
        )
    }

    @Test
    fun testMaxDbConnectionsMustBePositive() {
        for (bad in listOf(0, -1)) {
            val e =
                Assertions.assertThrows(ConfigErrorException::class.java) {
                    make(configJson(maxDbConnections = bad))
                }
            Assertions.assertEquals(
                "'max_db_connections' must be a positive integer, got $bad.",
                e.message
            )
        }
    }

    @Test
    fun testStorageReadApiIsOnByDefaultAndTogglesTheDriverProperty() {
        val off: BigQuerySourceConfiguration = make(configJson(useStorageReadApi = false))
        Assertions.assertFalse(off.useStorageReadApi)
        Assertions.assertFalse(off.jdbcProperties.containsKey("EnableHighThroughputAPI"))

        val default: BigQuerySourceConfiguration = make(configJson())
        Assertions.assertTrue(default.useStorageReadApi)
        Assertions.assertEquals("1", default.jdbcProperties["EnableHighThroughputAPI"])

        val on: BigQuerySourceConfiguration = make(configJson(useStorageReadApi = true))
        Assertions.assertTrue(on.useStorageReadApi)
        Assertions.assertEquals("1", on.jdbcProperties["EnableHighThroughputAPI"])
    }

    /**
     * The availability found by the READ's probe is consulted on every connection: once the Read
     * API is marked unavailable (no Read Session User role), the driver stops asking for it too.
     */
    @Test
    fun testStorageReadApiUnavailabilityRemovesTheDriverPropertyAtAccessTime() {
        val availability = BigQueryReadApiAvailability()
        val factory = BigQuerySourceConfigurationFactory(readApiAvailability = availability)
        val config: BigQuerySourceConfiguration =
            factory.make(
                Jsons.readValue(
                    configJson(useStorageReadApi = true),
                    BigQuerySourceConfigurationSpecification::class.java
                )
            )
        Assertions.assertTrue(config.useStorageReadApi)
        Assertions.assertEquals("1", config.jdbcProperties["EnableHighThroughputAPI"])
        availability.markUnavailable("no permission")
        Assertions.assertTrue(config.useStorageReadApi)
        Assertions.assertFalse(config.jdbcProperties.containsKey("EnableHighThroughputAPI"))
        Assertions.assertTrue(config.toString().contains("readApiAvailable=false"))
        availability.reset()
        Assertions.assertEquals("1", config.jdbcProperties["EnableHighThroughputAPI"])
    }

    @Test
    fun testStorageReadApiIsNotWiredAgainstTheEmulator() {
        System.setProperty(BigQueryEmulator.SYSTEM_PROPERTY, "http://localhost:9050")
        val config: BigQuerySourceConfiguration = make(configJson(useStorageReadApi = true))
        // The emulator path is test-only; its Storage Read API is too partial to be used.
        Assertions.assertFalse(config.useStorageReadApi)
        Assertions.assertFalse(config.jdbcProperties.containsKey("EnableHighThroughputAPI"))
    }

    @Test
    fun testJobProjectRunsTheJobsWhileTheDataProjectOwnsTheTables() {
        val config: BigQuerySourceConfiguration =
            make(configJson(jobProjectId = " billing-project "))
        Assertions.assertEquals("my-project", config.projectId)
        Assertions.assertEquals("billing-project", config.jobProjectId)
        Assertions.assertEquals(
            "jdbc:bigquery://https://www.googleapis.com/bigquery/v2:443;ProjectId=billing-project;OAuthType=0",
            String.format(config.jdbcUrlFmt, config.realHost, config.realPort),
        )
        Assertions.assertEquals("billing-project", config.jdbcProperties["ProjectId"])
        Assertions.assertTrue(config.toString().contains("jobProjectId=billing-project"))
    }

    @Test
    fun testBlankJobProjectMeansTheDataProject() {
        val config: BigQuerySourceConfiguration = make(configJson(jobProjectId = "  "))
        Assertions.assertEquals("my-project", config.jobProjectId)
        Assertions.assertEquals("my-project", config.jdbcProperties["ProjectId"])
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
        Assertions.assertFalse(config.toString().contains(PRIVATE_KEY_PEM), config.toString())
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
    fun testPrivateKeyMustBeParseable() {
        val badKey: String =
            SERVICE_ACCOUNT_KEY.replace(
                Jsons.writeValueAsString(PRIVATE_KEY_PEM),
                "\"-----BEGIN PRIVATE KEY-----\\nMIIB\\n-----END PRIVATE KEY-----\\n\"",
            )
        val e =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                make(configJson(credentialsJson = badKey))
            }
        Assertions.assertTrue(
            e.message!!.startsWith("'credentials_json' has an invalid 'private_key'"),
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
        /** A throwaway RSA key generated for this test run, PEM-encoded like a real key file. */
        val PRIVATE_KEY_PEM: String =
            KeyPairGenerator.getInstance("RSA")
                .apply { initialize(1024) }
                .generateKeyPair()
                .private
                .encoded
                .let { der: ByteArray ->
                    "-----BEGIN PRIVATE KEY-----\n" +
                        Base64.getMimeEncoder(64, "\n".toByteArray()).encodeToString(der) +
                        "\n-----END PRIVATE KEY-----\n"
                }

        val SERVICE_ACCOUNT_KEY: String =
            Jsons.writeValueAsString(
                Jsons.objectNode()
                    .put("type", "service_account")
                    .put("project_id", "my-project")
                    .put("private_key_id", "abc")
                    .put("private_key", PRIVATE_KEY_PEM)
                    .put("client_email", "airbyte@my-project.iam.gserviceaccount.com")
                    .put("client_id", "123")
                    .put("token_uri", "https://oauth2.googleapis.com/token")
            )
    }
}
