/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.db.factory.DatabaseDriver
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.db.jdbc.JdbcUtils.parseJdbcParameters
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.base.Source
import io.airbyte.cdk.integrations.source.jdbc.DefaultJdbcSourceAcceptanceTest.BareBonesTestDatabase
import io.airbyte.cdk.integrations.source.jdbc.DefaultJdbcSourceAcceptanceTest.BareBonesTestDatabase.BareBonesConfigBuilder
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest
import io.airbyte.cdk.integrations.util.HostPortResolver.resolveHost
import io.airbyte.cdk.integrations.util.HostPortResolver.resolvePort
import io.airbyte.cdk.testutils.TestDatabase
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.util.MoreIterators
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.SyncMode
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.JDBCType
import java.util.function.Consumer
import java.util.function.Supplier
import java.util.stream.Stream
import org.jooq.SQLDialect
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.containers.PostgreSQLContainer

private val LOGGER = KotlinLogging.logger {}

/**
 * Runs the acceptance tests in the source-jdbc test module. We want this module to run these tests
 * itself as a sanity check. The trade off here is that this class is duplicated from the one used
 * in source-postgres.
 */
internal class DefaultJdbcSourceAcceptanceTest :
    JdbcSourceAcceptanceTest<
        DefaultJdbcSourceAcceptanceTest.PostgresTestSource, BareBonesTestDatabase>() {
    override fun config(): JsonNode {
        return testdb.testConfigBuilder().build()
    }

    override fun source(): PostgresTestSource {
        return PostgresTestSource()
    }

    override fun createTestDatabase(): BareBonesTestDatabase {
        return BareBonesTestDatabase(PSQL_CONTAINER).initialized()
    }

    public override fun supportsSchemas(): Boolean {
        return true
    }

    fun getConfigWithConnectionProperties(
        psqlDb: PostgreSQLContainer<*>,
        dbName: String,
        additionalParameters: String
    ): JsonNode {
        return Jsons.jsonNode(
            ImmutableMap.builder<Any, Any>()
                .put(JdbcUtils.HOST_KEY, resolveHost(psqlDb))
                .put(JdbcUtils.PORT_KEY, resolvePort(psqlDb))
                .put(JdbcUtils.DATABASE_KEY, dbName)
                .put(JdbcUtils.SCHEMAS_KEY, listOf(SCHEMA_NAME))
                .put(JdbcUtils.USERNAME_KEY, psqlDb.username)
                .put(JdbcUtils.PASSWORD_KEY, psqlDb.password)
                .put(JdbcUtils.CONNECTION_PROPERTIES_KEY, additionalParameters)
                .build()
        )
    }

    class PostgresTestSource :
        AbstractJdbcSource<JDBCType>(
            DRIVER_CLASS,
            Supplier { AdaptiveStreamingQueryConfig() },
            JdbcUtils.defaultSourceOperations
        ),
        Source {
        override fun toDatabaseConfig(config: JsonNode): JsonNode {
            val configBuilder =
                ImmutableMap.builder<Any, Any>()
                    .put(JdbcUtils.USERNAME_KEY, config[JdbcUtils.USERNAME_KEY].asText())
                    .put(
                        JdbcUtils.JDBC_URL_KEY,
                        String.format(
                            DatabaseDriver.POSTGRESQL.urlFormatString,
                            config[JdbcUtils.HOST_KEY].asText(),
                            config[JdbcUtils.PORT_KEY].asInt(),
                            config[JdbcUtils.DATABASE_KEY].asText()
                        )
                    )

            if (config.has(JdbcUtils.PASSWORD_KEY)) {
                configBuilder.put(JdbcUtils.PASSWORD_KEY, config[JdbcUtils.PASSWORD_KEY].asText())
            }

            return Jsons.jsonNode(configBuilder.build())
        }

        override val excludedInternalNameSpaces =
            setOf("information_schema", "pg_catalog", "pg_internal", "catalog_history")

        override fun getSupportedStateType(
            config: JsonNode?
        ): AirbyteStateMessage.AirbyteStateType {
            return AirbyteStateMessage.AirbyteStateType.STREAM
        }

        companion object {

            val DRIVER_CLASS: String = DatabaseDriver.POSTGRESQL.driverClassName

            @Throws(Exception::class)
            @JvmStatic
            fun main(args: Array<String>) {
                val source: Source = PostgresTestSource()
                LOGGER.info { "starting source: ${PostgresTestSource::class.java}" }
                IntegrationRunner(source).run(args)
                LOGGER.info { "completed source: ${PostgresTestSource::class.java}" }
            }
        }
    }

    class BareBonesTestDatabase(container: PostgreSQLContainer<*>) :
        TestDatabase<PostgreSQLContainer<*>, BareBonesTestDatabase, BareBonesConfigBuilder>(
            container
        ) {
        override fun inContainerBootstrapCmd(): Stream<Stream<String>> {
            val sql =
                Stream.of(
                    String.format("CREATE DATABASE %s", databaseName),
                    String.format("CREATE USER %s PASSWORD '%s'", userName, password),
                    String.format(
                        "GRANT ALL PRIVILEGES ON DATABASE %s TO %s",
                        databaseName,
                        userName
                    ),
                    String.format("ALTER USER %s WITH SUPERUSER", userName)
                )
            return Stream.of(
                Stream.concat(
                    Stream.of(
                        "psql",
                        "-d",
                        container.databaseName,
                        "-U",
                        container.username,
                        "-v",
                        "ON_ERROR_STOP=1",
                        "-a"
                    ),
                    sql.flatMap { stmt: String -> Stream.of("-c", stmt) }
                )
            )
        }

        override fun inContainerUndoBootstrapCmd(): Stream<String> {
            return Stream.empty()
        }

        override val databaseDriver: DatabaseDriver
            get() = DatabaseDriver.POSTGRESQL

        override val sqlDialect: SQLDialect
            get() = SQLDialect.POSTGRES

        override fun configBuilder(): BareBonesConfigBuilder {
            return BareBonesConfigBuilder(this)
        }

        class BareBonesConfigBuilder(testDatabase: BareBonesTestDatabase) :
            ConfigBuilder<BareBonesTestDatabase, BareBonesConfigBuilder>(testDatabase)
    }

    @Test
    fun testCustomParametersOverwriteDefaultParametersExpectException() {
        val connectionPropertiesUrl = "ssl=false"
        val config =
            getConfigWithConnectionProperties(
                PSQL_CONTAINER,
                testdb.databaseName,
                connectionPropertiesUrl
            )
        val customParameters = parseJdbcParameters(config, JdbcUtils.CONNECTION_PROPERTIES_KEY, "&")
        val defaultParameters = mapOf("ssl" to "true", "sslmode" to "require")
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            JdbcDataSourceUtils.assertCustomParametersDontOverwriteDefaultParameters(
                customParameters,
                defaultParameters
            )
        }
    }

    @Throws(Exception::class)
    override fun incrementalCursorCheck(
        initialCursorField: String?,
        cursorField: String,
        initialCursorValue: String?,
        endCursorValue: String?,
        expectedRecordMessages: List<AirbyteMessage>,
        airbyteStream: ConfiguredAirbyteStream
    ) {
        airbyteStream.syncMode = SyncMode.INCREMENTAL
        airbyteStream.cursorField = java.util.List.of(cursorField)
        airbyteStream.destinationSyncMode = DestinationSyncMode.APPEND

        val configuredCatalog =
            ConfiguredAirbyteCatalog().withStreams(java.util.List.of(airbyteStream))

        val dbStreamState = buildStreamState(airbyteStream, initialCursorField, initialCursorValue)

        val actualMessages =
            MoreIterators.toList(
                source()!!.read(
                    config(),
                    configuredCatalog,
                    Jsons.jsonNode(createState(java.util.List.of(dbStreamState))),
                ),
            )

        setEmittedAtToNull(actualMessages)

        val expectedStreams =
            java.util.List.of(buildStreamState(airbyteStream, cursorField, endCursorValue))

        val expectedMessages: MutableList<AirbyteMessage> = ArrayList(expectedRecordMessages)
        expectedMessages.addAll(
            createExpectedTestMessages(expectedStreams, expectedRecordMessages.size.toLong()),
        )

        setTraceEmittedAtToNull(actualMessages)
        setTraceEmittedAtToNull(expectedMessages)
        Assertions.assertEquals(expectedMessages.size, actualMessages.size)
        Assertions.assertTrue(expectedMessages.containsAll(actualMessages))
        Assertions.assertTrue(actualMessages.containsAll(expectedMessages))
    }

    override open fun assertStreamStatusTraceMessageIndex(
        idx: Int,
        allMessages: List<AirbyteMessage>,
        expectedStreamStatus: AirbyteStreamStatusTraceMessage
    ) {
        // no-op
    }

    @Test
    @Throws(Exception::class)
    override fun testReadOneColumn() {
        val catalog =
            CatalogHelpers.createConfiguredAirbyteCatalog(
                streamName(),
                defaultNamespace,
                Field.of(COL_ID, JsonSchemaType.NUMBER),
            )
        val actualMessages = MoreIterators.toList(source().read(config(), catalog, null))

        setEmittedAtToNull(actualMessages)

        val expectedMessages: MutableList<AirbyteMessage> = airbyteMessagesReadOneColumn

        Assertions.assertEquals(expectedMessages.size, actualMessages.size)
        Assertions.assertTrue(expectedMessages.containsAll(actualMessages))
        Assertions.assertTrue(actualMessages.containsAll(expectedMessages))
    }

    @Test
    @Throws(Exception::class)
    override fun testReadOneTableIncrementallyTwice() {
        val config = config()
        val namespace = defaultNamespace
        val configuredCatalog = getConfiguredCatalogWithOneStream(namespace)
        configuredCatalog.streams.forEach(
            Consumer { airbyteStream: ConfiguredAirbyteStream ->
                airbyteStream.syncMode = SyncMode.INCREMENTAL
                airbyteStream.cursorField = java.util.List.of(COL_ID)
                airbyteStream.destinationSyncMode = DestinationSyncMode.APPEND
            },
        )

        val actualMessagesFirstSync =
            MoreIterators.toList(
                source()!!.read(
                    config,
                    configuredCatalog,
                    createEmptyState(streamName(), namespace),
                ),
            )

        val stateAfterFirstSyncOptional =
            actualMessagesFirstSync
                .filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.STATE }
                .first()

        executeStatementReadIncrementallyTwice()

        val actualMessagesSecondSync =
            MoreIterators.toList(
                source()!!.read(
                    config,
                    configuredCatalog,
                    extractState(stateAfterFirstSyncOptional),
                ),
            )

        Assertions.assertEquals(
            2,
            actualMessagesSecondSync
                .filter { r: AirbyteMessage -> r.type == AirbyteMessage.Type.RECORD }
                .count()
                .toInt(),
        )
        val expectedMessages: MutableList<AirbyteMessage> =
            getExpectedAirbyteMessagesSecondSync(namespace)

        setEmittedAtToNull(actualMessagesSecondSync)

        Assertions.assertEquals(expectedMessages.size, actualMessagesSecondSync.size)
        Assertions.assertTrue(expectedMessages.containsAll(actualMessagesSecondSync))
        Assertions.assertTrue(actualMessagesSecondSync.containsAll(expectedMessages))
    }

    companion object {
        private lateinit var PSQL_CONTAINER: PostgreSQLContainer<*>

        @JvmStatic
        @BeforeAll
        fun init(): Unit {
            PSQL_CONTAINER = PostgreSQLContainer("postgres:13-alpine")
            PSQL_CONTAINER.start()
            CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s BIT(3) NOT NULL);"
            INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES(B'101');"
        }

        @JvmStatic
        @AfterAll
        fun cleanUp(): Unit {
            PSQL_CONTAINER.close()
        }
    }
}
