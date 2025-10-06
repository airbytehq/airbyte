/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.teradata

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.factory.DataSourceFactory
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.cdk.integrations.destination.StandardNameTransformer
import io.airbyte.cdk.integrations.standardtest.destination.JdbcDestinationAcceptanceTest
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.map.MoreMaps
import io.airbyte.commons.string.Strings
import io.airbyte.integrations.destination.teradata.envclient.TeradataHttpClient
import io.airbyte.integrations.destination.teradata.envclient.dto.CreateEnvironmentRequest
import io.airbyte.integrations.destination.teradata.envclient.dto.DeleteEnvironmentRequest
import io.airbyte.integrations.destination.teradata.envclient.dto.EnvironmentRequest
import io.airbyte.integrations.destination.teradata.envclient.dto.EnvironmentResponse
import io.airbyte.integrations.destination.teradata.envclient.dto.GetEnvironmentRequest
import io.airbyte.integrations.destination.teradata.envclient.dto.OperationRequest
import io.airbyte.integrations.destination.teradata.envclient.exception.BaseException
import io.airbyte.integrations.destination.teradata.util.TeradataConstants
import java.net.URISyntaxException
import java.nio.file.Files
import java.nio.file.Paths
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import java.time.Duration
import java.util.concurrent.ExecutionException
import java.util.regex.Pattern
import javax.sql.DataSource
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInstance
import org.slf4j.Logger
import org.slf4j.LoggerFactory

@Disabled("Disabled after DV2 migration. Re-enable with fixtures updated to DV2.")
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
open class TeradataDestinationAcceptanceTest : JdbcDestinationAcceptanceTest() {
    private val namingResolver = StandardNameTransformer()

    private lateinit var configJson: JsonNode
    private lateinit var database: JdbcDatabase
    private lateinit var dataSource: DataSource
    private val dest: TeradataDestination = TeradataDestination()

    override val imageName: String
        get() = "airbyte/destination-teradata:dev"

    override fun getConfig(): JsonNode {
        return configJson
    }

    @BeforeAll
    @Throws(Exception::class)
    fun initEnvironment() {

        var configJson =
            Jsons.clone(
                staticConfig,
            )
        this.configJson = configJson
        val teradataHttpClient =
            getTeradataHttpClient(
                configJson,
            )
        val name = configJson["env_name"].asText()
        val token = configJson["env_token"].asText()
        val getRequest = GetEnvironmentRequest(name)
        var response: EnvironmentResponse? = null
        try {
            response = teradataHttpClient.getEnvironment(getRequest, token)
        } catch (be: BaseException) {
            LOGGER.info("Environemnt " + name + " is not available. " + be.message)
        }
        if (response == null || response.ip == null) {
            val request =
                CreateEnvironmentRequest(
                    name,
                    configJson["env_region"].asText(),
                    configJson["env_password"].asText(),
                )
            response = teradataHttpClient.createEnvironment(request, token).get()
            LOGGER.info(
                "Environemnt {} is created successfully ",
                configJson["env_name"].asText(),
            )
        } else if (response.state == EnvironmentResponse.State.STOPPED) {
            val request = EnvironmentRequest(name, OperationRequest("start"))
            teradataHttpClient.startEnvironment(request, token)
        }
        if (response != null) {
            (configJson as ObjectNode).put(JdbcUtils.HOST_KEY, response.ip)
        }
        val authMap =
            ImmutableMap.builder<Any, Any>()
                .put(TeradataConstants.AUTH_TYPE, "TD2")
                .put(JdbcUtils.USERNAME_KEY, configJson.get("username").asText())
                .put(JdbcUtils.PASSWORD_KEY, configJson.get("env_password").asText())
                .build()
        (configJson as ObjectNode).set<JsonNode>(
            TeradataConstants.LOG_MECH,
            Jsons.jsonNode(authMap),
        )
    }

    @AfterAll
    @Throws(
        ExecutionException::class,
        InterruptedException::class,
        Exception::class,
    )
    fun cleanupEnvironment() {
        try {
            val teradataHttpClient =
                getTeradataHttpClient(
                    configJson,
                )
            val token = configJson["env_token"].asText()
            val request =
                DeleteEnvironmentRequest(
                    configJson["env_name"].asText(),
                )
            teradataHttpClient.deleteEnvironment(request, token)
            LOGGER.info(
                "Environemnt {} is deleted successfully ",
                configJson["env_name"].asText(),
            )
        } catch (be: BaseException) {
            LOGGER.error(
                "Environemnt " +
                    configJson["env_name"].asText() +
                    " is not available. " +
                    be.message
            )
        }
    }

    @get:Throws(Exception::class)
    open val staticConfig: JsonNode
        get() = Jsons.deserialize(Files.readString(Paths.get("secrets/config.json")))

    @Throws(Exception::class)
    override fun getFailCheckConfig(): JsonNode {
        val failureConfig = Jsons.clone(configJson)
        val logMechConfig = failureConfig[TeradataConstants.LOG_MECH]
        (logMechConfig as ObjectNode).put(JdbcUtils.PASSWORD_KEY, "wrongpassword")
        return failureConfig
    }

    override fun retrieveRecords(
        testEnv: TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode> {
        return retrieveRecordsFromTable(namingResolver.getIdentifier(streamName), namespace)
    }

    @Throws(SQLException::class)
    private fun retrieveRecordsFromTable(tableName: String, schemaName: String): List<JsonNode> {
        return database.bufferedResultSetQuery(
            { connection: Connection ->
                val statement = connection.createStatement()
                statement.executeQuery(
                    String.format(
                        "SELECT * FROM %s.%s ORDER BY %s ASC;",
                        schemaName,
                        tableName,
                        JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
                    ),
                )
            },
            { rs: ResultSet ->
                Jsons.deserialize(rs.getString(JavaBaseConstants.COLUMN_NAME_DATA))
            },
        )
    }

    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        val createSchemaQuery = String.format(CREATE_DATABASE, SCHEMA_NAME)
        try {
            (configJson as ObjectNode).put("schema", SCHEMA_NAME)
            dataSource = getDataSource(configJson)
            database = dest.getDatabase(dataSource)
            database.execute(createSchemaQuery)
        } catch (e: Exception) {
            AirbyteTraceMessageUtility.emitSystemErrorTrace(
                e,
                "Database $SCHEMA_NAME creation got failed.",
            )
        }
    }

    @Throws(Exception::class)
    override fun tearDown(testEnv: TestDestinationEnv) {
        val deleteQuery = String.format(String.format(DELETE_DATABASE, SCHEMA_NAME))
        val dropQuery = String.format(String.format(DROP_DATABASE, SCHEMA_NAME))
        try {
            database.execute(deleteQuery)
            database.execute(dropQuery)
        } catch (e: Exception) {
            AirbyteTraceMessageUtility.emitSystemErrorTrace(
                e,
                "Database $SCHEMA_NAME delete got failed.",
            )
        } finally {
            DataSourceFactory.close(dataSource)
        }
    }

    @Test
    override fun testLineBreakCharacters() {
        // overrides test in coming releases
    }

    @Test
    @Throws(Exception::class)
    override fun testCustomDbtTransformations() {
        // overrides test in coming releases
    }

    private fun getDataSource(config: JsonNode): DataSource {
        val jdbcConfig = dest.toJdbcConfig(config)
        return DataSourceFactory.create(
            jdbcConfig[JdbcUtils.USERNAME_KEY].asText(),
            if (jdbcConfig.has(JdbcUtils.PASSWORD_KEY)) jdbcConfig[JdbcUtils.PASSWORD_KEY].asText()
            else null,
            TeradataConstants.DRIVER_CLASS,
            jdbcConfig[JdbcUtils.JDBC_URL_KEY].asText(),
            getConnectionProperties(config),
            Duration.ofSeconds(10)
        )
    }

    private fun getConnectionProperties(config: JsonNode): Map<String, String> {
        val customProperties =
            JdbcUtils.parseJdbcParameters(
                config,
                JdbcUtils.JDBC_URL_PARAMS_KEY,
            )
        val defaultProperties = getDefaultConnectionProperties(config)
        assertCustomParametersDontOverwriteDefaultParameters(customProperties, defaultProperties)
        return MoreMaps.merge(customProperties, defaultProperties)
    }

    private fun getDefaultConnectionProperties(config: JsonNode): Map<String, String> {
        return dest.getDefaultConnectionProperties(config)
    }

    private fun assertCustomParametersDontOverwriteDefaultParameters(
        customParameters: Map<String, String>,
        defaultParameters: Map<String, String>
    ) {
        for (key in defaultParameters.keys) {
            require(
                !(customParameters.containsKey(key) &&
                    customParameters[key] != defaultParameters[key]),
            ) {
                "Cannot overwrite default JDBC parameter $key"
            }
        }
    }

    @Test
    @Throws(Exception::class)
    fun testQueryBand() {
        dataSource = getDataSource(configJson)
        database = dest.getDatabase(dataSource)
        Assertions.assertEquals(TeradataConstants.DEFAULT_QUERY_BAND, dest.queryBand)
    }

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(
                TeradataDestinationAcceptanceTest::class.java,
            )
        private val SCHEMA_NAME = Strings.addRandomSuffix("acc_test", "_", 5)

        private const val CREATE_DATABASE =
            "CREATE DATABASE \"%s\" AS PERMANENT = 60e6, SPOOL = 60e6 SKEW = 10 PERCENT"

        private const val DELETE_DATABASE = "DELETE DATABASE \"%s\""

        private const val DROP_DATABASE = "DROP DATABASE \"%s\""
        private val ALLOWED_URL_PATTERN: Pattern =
            Pattern.compile("^(https?://)(www\\.)?api.clearscape.teradata\\.com.*")

        private fun isValidUrl(url: String): Boolean {
            return ALLOWED_URL_PATTERN.matcher(url).matches()
        }

        @Throws(URISyntaxException::class)
        private fun getTeradataHttpClient(config: JsonNode): TeradataHttpClient {
            val envUrl = config["env_url"].asText()
            if (isValidUrl(envUrl)) {
                return TeradataHttpClient(envUrl)
            } else {
                LOGGER.error("Invalid or untrusted URL")
                throw URISyntaxException(envUrl, "Provide valid environment URL")
            }
        }
    }
}
