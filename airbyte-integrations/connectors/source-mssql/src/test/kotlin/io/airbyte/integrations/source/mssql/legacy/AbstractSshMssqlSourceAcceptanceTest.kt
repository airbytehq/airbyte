/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.source.mssql.legacy

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.Lists
import io.airbyte.cdk.test.fixtures.legacy.*
import io.airbyte.cdk.test.fixtures.legacy.DSLContextFactory.create
import io.airbyte.cdk.test.fixtures.legacy.Jsons.jsonNode
import io.airbyte.cdk.test.fixtures.legacy.SshHelpers.specAndInjectSsh
import io.airbyte.cdk.test.fixtures.legacy.SshTunnel.Companion.sshWrap
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.Companion.`in`
import io.airbyte.protocol.models.Field
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.*
import org.jooq.DSLContext
import org.jooq.SQLDialect
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import java.io.IOException
import java.io.UncheckedIOException

abstract class AbstractSshMssqlSourceAcceptanceTest : SourceAcceptanceTest() {
    abstract val tunnelMethod: SshTunnel.TunnelMethod?

    private val bastion = SshBastionContainer()
    private var testdb: MsSQLTestDatabase? = null

    override val config: JsonNode
        get() {
            try {
                return testdb!!.integrationTestConfigBuilder()
                    .withoutSsl()
                    .with("tunnel_method", bastion.getTunnelMethod(tunnelMethod!!, true)!!)
                    .build()
            } catch (e: IOException) {
                throw UncheckedIOException(e)
            } catch (e: InterruptedException) {
                throw RuntimeException(e)
            }
        }

    @Throws(Exception::class)
    private fun populateDatabaseTestData() {
        val outerConfig = testdb!!.integrationTestConfigBuilder()
            .withSchemas("public")
            .withoutSsl()
            .with("tunnel_method", bastion.getTunnelMethod(tunnelMethod!!, false)!!)
            .build()
        sshWrap(
            outerConfig,
            JdbcUtils.HOST_LIST_KEY,
            JdbcUtils.PORT_LIST_KEY,
            CheckedFunction { mangledConfig: JsonNode ->
                getDatabaseFromConfig(mangledConfig)
                    .query<List<JsonNode>?> { ctx: DSLContext ->
                        ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), born DATETIMEOFFSET(7));")
                        ctx.fetch(
                            "INSERT INTO id_and_name (id, name, born) VALUES " +
                                    "(1, 'picard', '2124-03-04T01:01:01Z'), " +
                                    "(2, 'crusher', '2124-03-04T01:01:01Z'), " +
                                    "(3, 'vash', '2124-03-04T01:01:01Z');"
                        )
                        return@query null
                    }
            })
    }

    @Throws(Exception::class)
    override fun setupEnvironment(environment: TestDestinationEnv?) {
        testdb = `in`(MsSQLTestDatabase.BaseImage.MSSQL_2022)
        LOGGER.info("starting bastion")
        bastion.initAndStartBastion(testdb!!.container.network)
        LOGGER.info("bastion started")
        populateDatabaseTestData()
    }

    override fun tearDown(testEnv: TestDestinationEnv?) {
        bastion.stopAndClose()
    }

    override val imageName: String
        get() = "airbyte/source-mssql:dev"

    @get:Throws(Exception::class)
    override val spec: ConnectorSpecification
        get() = specAndInjectSsh

    override val configuredCatalog: ConfiguredAirbyteCatalog
        get() = ConfiguredAirbyteCatalog().withStreams(
            Lists.newArrayList(
                ConfiguredAirbyteStream()
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withCursorField(Lists.newArrayList("id"))
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                    .withStream(
                        CatalogHelpers.createAirbyteStream(
                            STREAM_NAME, SCHEMA_NAME,
                            Field.of("id", JsonSchemaType.NUMBER),
                            Field.of("name", JsonSchemaType.STRING)
                        )
                            .withSupportedSyncModes(
                                Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                            )
                    ),
                ConfiguredAirbyteStream()
                    .withSyncMode(SyncMode.INCREMENTAL)
                    .withCursorField(Lists.newArrayList("id"))
                    .withDestinationSyncMode(DestinationSyncMode.APPEND)
                    .withStream(
                        CatalogHelpers.createAirbyteStream(
                            STREAM_NAME2, SCHEMA_NAME,
                            Field.of("id", JsonSchemaType.NUMBER),
                            Field.of("name", JsonSchemaType.STRING)
                        )
                            .withSupportedSyncModes(
                                Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)
                            )
                    )
            )
        )

    override val state: JsonNode
        get() = jsonNode(HashMap<Any, Any>())

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(AbstractSshMssqlSourceAcceptanceTest::class.java)

        private const val SCHEMA_NAME = "dbo"
        private const val STREAM_NAME = "id_and_name"
        private const val STREAM_NAME2 = "starships"

        private fun getDatabaseFromConfig(config: JsonNode?): Database {
            return Database(
                create(
                    config!![JdbcUtils.USERNAME_KEY].asText(),
                    config[JdbcUtils.PASSWORD_KEY].asText(),
                    DatabaseDriver.MSSQLSERVER.driverClassName,
                    String.format(
                        DatabaseDriver.MSSQLSERVER.urlFormatString,
                        config[JdbcUtils.HOST_KEY].asText(),
                        config[JdbcUtils.PORT_KEY].asInt(),
                        config[JdbcUtils.DATABASE_KEY].asText()
                    ) + ";encrypt=false;trustServerCertificate=true",
                    SQLDialect.DEFAULT
                )
            )
        }
    }
}
