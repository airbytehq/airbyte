/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.factory.DataSourceFactory.create
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.db.jdbc.JdbcUtils.defaultSourceOperations
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.DestinationConfig
import io.airbyte.cdk.testutils.PostgreSQLContainerHelper.runSqlScript
import io.airbyte.commons.io.IOs.writeFileToRandomTmpDir
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.json.Jsons.jsonNode
import io.airbyte.commons.json.Jsons.serialize
import io.airbyte.commons.string.Strings.addRandomSuffix
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import java.io.Serializable
import java.nio.charset.StandardCharsets
import java.sql.Connection
import java.sql.ResultSet
import java.time.Instant
import java.util.*
import java.util.function.Consumer
import java.util.stream.Collectors
import java.util.stream.IntStream
import javax.sql.DataSource
import org.junit.jupiter.api.*
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.utility.MountableFile

@Execution(ExecutionMode.CONCURRENT)
@TestInstance(TestInstance.Lifecycle.PER_METHOD)
class PostgresDestinationTest {
    private var config: JsonNode? = null

    private fun buildConfigNoJdbcParameters(): JsonNode {
        return jsonNode<ImmutableMap<String, Serializable>>(
            ImmutableMap.of<String, Serializable>(
                JdbcUtils.HOST_KEY,
                "localhost",
                JdbcUtils.PORT_KEY,
                1337,
                JdbcUtils.USERNAME_KEY,
                "user",
                JdbcUtils.DATABASE_KEY,
                "db",
                JdbcUtils.SSL_KEY,
                true,
                "ssl_mode",
                ImmutableMap.of<String, String>("mode", "require")
            )
        )
    }

    private fun buildConfigEscapingNeeded(): JsonNode {
        return jsonNode(
            ImmutableMap.of(
                JdbcUtils.HOST_KEY,
                "localhost",
                JdbcUtils.PORT_KEY,
                1337,
                JdbcUtils.USERNAME_KEY,
                "user",
                JdbcUtils.DATABASE_KEY,
                "db/foo"
            )
        )
    }

    private fun buildConfigWithExtraJdbcParameters(extraParam: String): JsonNode {
        return jsonNode(
            ImmutableMap.of(
                JdbcUtils.HOST_KEY,
                "localhost",
                JdbcUtils.PORT_KEY,
                1337,
                JdbcUtils.USERNAME_KEY,
                "user",
                JdbcUtils.DATABASE_KEY,
                "db",
                JdbcUtils.JDBC_URL_PARAMS_KEY,
                extraParam
            )
        )
    }

    private fun buildConfigNoExtraJdbcParametersWithoutSsl(): JsonNode {
        return jsonNode(
            ImmutableMap.of(
                JdbcUtils.HOST_KEY,
                "localhost",
                JdbcUtils.PORT_KEY,
                1337,
                JdbcUtils.USERNAME_KEY,
                "user",
                JdbcUtils.DATABASE_KEY,
                "db",
                JdbcUtils.SSL_KEY,
                false
            )
        )
    }

    @BeforeEach
    fun setup() {
        config = createDatabaseWithRandomNameAndGetPostgresConfig(PSQL_DB!!)
    }

    @Test
    fun testJdbcUrlAndConfigNoExtraParams() {
        val jdbcConfig = PostgresDestination().toJdbcConfig(buildConfigNoJdbcParameters())
        Assertions.assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText())
    }

    @Test
    fun testJdbcUrlWithEscapedDatabaseName() {
        val jdbcConfig = PostgresDestination().toJdbcConfig(buildConfigEscapingNeeded())
        Assertions.assertEquals(
            EXPECTED_JDBC_ESCAPED_URL,
            jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText()
        )
    }

    @Test
    fun testJdbcUrlEmptyExtraParams() {
        val jdbcConfig = PostgresDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(""))
        Assertions.assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText())
    }

    @Test
    fun testJdbcUrlExtraParams() {
        val extraParam = "key1=value1&key2=value2&key3=value3"
        val jdbcConfig =
            PostgresDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam))
        Assertions.assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText())
    }

    @Test
    fun testDefaultParamsNoSSL() {
        val defaultProperties =
            PostgresDestination()
                .getDefaultConnectionProperties(buildConfigNoExtraJdbcParametersWithoutSsl())
        Assertions.assertEquals(HashMap<Any, Any>(), defaultProperties)
    }

    @Test
    fun testDefaultParamsWithSSL() {
        val defaultProperties =
            PostgresDestination().getDefaultConnectionProperties(buildConfigNoJdbcParameters())
        Assertions.assertEquals(SSL_JDBC_PARAMETERS, defaultProperties)
    }

    @Test
    fun testCheckIncorrectPasswordFailure() {
        val config = buildConfigNoJdbcParameters()
        (config as ObjectNode).put(JdbcUtils.PASSWORD_KEY, "fake")
        config.put(JdbcUtils.SCHEMA_KEY, "public")
        val destination = PostgresDestination()
        val actual = destination.check(config)!!
        Assertions.assertTrue(actual.message.contains("State code: 08001;"))
    }

    @Test
    fun testCheckIncorrectUsernameFailure() {
        val config = buildConfigNoJdbcParameters()
        (config as ObjectNode).put(JdbcUtils.USERNAME_KEY, "")
        config.put(JdbcUtils.SCHEMA_KEY, "public")
        val destination = PostgresDestination()
        val status = destination.check(config)!!
        Assertions.assertTrue(status.message.contains("State code: 08001;"))
    }

    @Test
    fun testCheckIncorrectHostFailure() {
        val config = buildConfigNoJdbcParameters()
        (config as ObjectNode).put(JdbcUtils.HOST_KEY, "localhost2")
        config.put(JdbcUtils.SCHEMA_KEY, "public")
        val destination = PostgresDestination()
        val status = destination.check(config)!!
        Assertions.assertTrue(status.message.contains("State code: 08001;"))
    }

    @Test
    fun testCheckIncorrectPortFailure() {
        val config = buildConfigNoJdbcParameters()
        (config as ObjectNode).put(JdbcUtils.PORT_KEY, "30000")
        config.put(JdbcUtils.SCHEMA_KEY, "public")
        val destination = PostgresDestination()
        val status = destination.check(config)!!
        Assertions.assertTrue(status.message.contains("State code: 08001;"))
    }

    @Test
    fun testCheckIncorrectDataBaseFailure() {
        val config = buildConfigNoJdbcParameters()
        (config as ObjectNode).put(JdbcUtils.DATABASE_KEY, "wrongdatabase")
        config.put(JdbcUtils.SCHEMA_KEY, "public")
        val destination = PostgresDestination()
        val status = destination.check(config)!!
        Assertions.assertTrue(status.message.contains("State code: 08001;"))
    }

    @Test
    @Throws(Exception::class)
    fun testUserHasNoPermissionToDataBase() {
        val database = getJdbcDatabaseFromConfig(getDataSourceFromConfig(config!!))

        database.execute { connection: Connection ->
            connection
                .createStatement()
                .execute(String.format("create user %s with password '%s';", USERNAME, PASSWORD))
        }
        database.execute { connection: Connection ->
            connection.createStatement().execute(String.format("create database %s;", DATABASE))
        }
        // deny access for database for all users from group public
        database.execute { connection: Connection ->
            connection
                .createStatement()
                .execute(String.format("revoke all on database %s from public;", DATABASE))
        }

        (config as ObjectNode?)!!.put(JdbcUtils.USERNAME_KEY, USERNAME)
        (config as ObjectNode?)!!.put(JdbcUtils.PASSWORD_KEY, PASSWORD)
        (config as ObjectNode?)!!.put(JdbcUtils.DATABASE_KEY, DATABASE)

        val destination: Destination = PostgresDestination()
        val status = destination.check(config!!)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status!!.status)
    }

    // This test is a bit redundant with PostgresIntegrationTest. It makes it easy to run the
    // destination in the same process as the test allowing us to put breakpoint in, which is handy
    // for
    // debugging (especially since we use postgres as a guinea pig for most features).
    @Test
    @Throws(Exception::class)
    fun sanityTest() {
        val destination: Destination = PostgresDestination()
        val config = this.config!!
        DestinationConfig.initialize(config, true)
        val consumer =
            destination.getSerializedMessageConsumer(
                config,
                CATALOG,
                Destination::defaultOutputRecordCollector
            )
        val expectedRecords = getNRecords(10)

        consumer!!.start()
        expectedRecords.forEach(
            Consumer { m: AirbyteMessage ->
                try {
                    val message = serialize<AirbyteMessage>(m)
                    consumer.accept(message, message.toByteArray(StandardCharsets.UTF_8).size)
                } catch (e: Exception) {
                    throw RuntimeException(e)
                }
            }
        )
        val stateMessage =
            serialize(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.STATE)
                    .withState(
                        AirbyteStateMessage()
                            .withData(jsonNode(ImmutableMap.of("$SCHEMA_NAME.$STREAM_NAME", 10)))
                    )
            )
        consumer.accept(stateMessage, stateMessage.toByteArray(StandardCharsets.UTF_8).size)

        val finalMessage =
            serialize(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.TRACE)
                    .withTrace(
                        AirbyteTraceMessage()
                            .withType(AirbyteTraceMessage.Type.STREAM_STATUS)
                            .withStreamStatus(
                                AirbyteStreamStatusTraceMessage()
                                    .withStreamDescriptor(
                                        StreamDescriptor()
                                            .withNamespace(SCHEMA_NAME)
                                            .withName(STREAM_NAME),
                                    )
                                    .withStatus(
                                        AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
                                    ),
                            )
                    )
            )
        consumer.accept(finalMessage, finalMessage.toByteArray(StandardCharsets.UTF_8).size)
        consumer.close()

        val database = getJdbcDatabaseFromConfig(getDataSourceFromConfig(config))

        val actualRecords =
            database.bufferedResultSetQuery(
                { connection: Connection ->
                    connection
                        .createStatement()
                        .executeQuery(
                            "SELECT * FROM airbyte_internal.public_raw__stream_id_and_name;"
                        )
                },
                { queryResult: ResultSet -> defaultSourceOperations.rowToJson(queryResult) }
            )

        Assertions.assertEquals(
            expectedRecords
                .stream()
                .map<AirbyteRecordMessage> { obj: AirbyteMessage -> obj.record }
                .map<JsonNode> { obj: AirbyteRecordMessage -> obj.data }
                .collect(Collectors.toList<JsonNode>()),
            actualRecords
                .stream()
                .map<String> { o: JsonNode -> o["_airbyte_data"].asText() }
                .map<JsonNode>(Jsons::deserialize)
                .collect(Collectors.toList<JsonNode>())
        )
    }

    private fun getNRecords(n: Int): List<AirbyteMessage> {
        return IntStream.range(0, n)
            .boxed()
            .map { i: Int ->
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withStream(STREAM_NAME)
                            .withNamespace(SCHEMA_NAME)
                            .withEmittedAt(Instant.now().toEpochMilli())
                            .withData(jsonNode(ImmutableMap.of("id", i, "name", "human $i")))
                    )
            }
            .collect(Collectors.toList())
    }

    private fun getJdbcDatabaseFromConfig(dataSource: DataSource): JdbcDatabase {
        return DefaultJdbcDatabase(dataSource, defaultSourceOperations)
    }

    private fun createDatabaseWithRandomNameAndGetPostgresConfig(
        psqlDb: PostgreSQLContainer<Nothing>
    ): JsonNode {
        val dbName = addRandomSuffix("db", "_", 10).lowercase(Locale.getDefault())
        val initScriptName = "init_$dbName.sql"
        val tmpFilePath = writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE $dbName;")

        runSqlScript(MountableFile.forHostPath(tmpFilePath), psqlDb)
        return getDestinationConfig(psqlDb, dbName)
    }

    private fun getDestinationConfig(psqlDb: PostgreSQLContainer<*>?, dbName: String): JsonNode {
        return jsonNode<ImmutableMap<Any, Any>>(
            ImmutableMap.builder<Any, Any>()
                .put(JdbcUtils.HOST_KEY, psqlDb!!.host)
                .put(JdbcUtils.PORT_KEY, psqlDb.firstMappedPort)
                .put(JdbcUtils.DATABASE_KEY, dbName)
                .put(JdbcUtils.USERNAME_KEY, psqlDb.username)
                .put(JdbcUtils.PASSWORD_KEY, psqlDb.password)
                .put(JdbcUtils.SCHEMA_KEY, "public")
                .put(JdbcUtils.SSL_KEY, false)
                .build()
        )
    }

    private fun getDataSourceFromConfig(config: JsonNode): DataSource {
        return create(
            config.get(JdbcUtils.USERNAME_KEY).asText(),
            config.get(JdbcUtils.PASSWORD_KEY).asText(),
            DatabaseDriver.POSTGRESQL.driverClassName,
            String.format(
                DatabaseDriver.POSTGRESQL.urlFormatString,
                config.get(JdbcUtils.HOST_KEY).asText(),
                config.get(JdbcUtils.PORT_KEY).asInt(),
                config.get(JdbcUtils.DATABASE_KEY).asText()
            )
        )
    }

    companion object {
        private var PSQL_DB: PostgreSQLContainer<Nothing>? = null

        private const val USERNAME = "new_user"
        private const val DATABASE = "new_db"
        private const val PASSWORD = "new_password"

        private const val SCHEMA_NAME = "public"
        private const val STREAM_NAME = "id_and_name"

        val SSL_JDBC_PARAMETERS: Map<String, String> =
            ImmutableMap.of("ssl", "true", "sslmode", "require")
        private val CATALOG: ConfiguredAirbyteCatalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        CatalogHelpers.createConfiguredAirbyteStream(
                                STREAM_NAME,
                                SCHEMA_NAME,
                                Field.of("id", JsonSchemaType.NUMBER),
                                Field.of("name", JsonSchemaType.STRING)
                            )
                            .withGenerationId(43)
                            .withSyncId(42)
                            .withMinimumGenerationId(43)
                    )
                )

        private const val EXPECTED_JDBC_URL = "jdbc:postgresql://localhost:1337/db?"

        private const val EXPECTED_JDBC_ESCAPED_URL = "jdbc:postgresql://localhost:1337/db%2Ffoo?"

        @JvmStatic
        @BeforeAll
        fun init(): Unit {
            PSQL_DB = PostgreSQLContainer("postgres:13-alpine")
            PSQL_DB!!.start()
        }

        @JvmStatic
        @AfterAll
        fun cleanUp(): Unit {
            PSQL_DB!!.close()
        }
    }
}
