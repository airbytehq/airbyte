/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.Lists
import io.airbyte.cdk.test.fixtures.legacy.CheckedConsumer
import io.airbyte.cdk.test.fixtures.legacy.ContextQueryFunction
import io.airbyte.cdk.test.fixtures.legacy.DSLContextFactory
import io.airbyte.cdk.test.fixtures.legacy.Database
import io.airbyte.cdk.test.fixtures.legacy.DatabaseDriver
import io.airbyte.cdk.test.fixtures.legacy.JdbcUtils
import io.airbyte.cdk.test.fixtures.legacy.JdbcUtils.MODE_KEY
import io.airbyte.cdk.test.fixtures.legacy.Jsons
import io.airbyte.cdk.test.fixtures.legacy.SshBastionContainer
import io.airbyte.cdk.test.fixtures.legacy.SshTunnel
import io.airbyte.cdk.test.fixtures.legacy.SshTunnel.Companion.sshWrap
import io.airbyte.cdk.test.fixtures.legacy.TestDestinationEnv
import io.airbyte.integrations.source.postgres.legacy.testFixtures.PostgresTestDatabase
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.Field
import io.airbyte.protocol.models.v0.SyncMode
import java.io.IOException
import java.io.UncheckedIOException
import java.util.List
import org.jooq.DSLContext
import org.jooq.SQLDialect

abstract class AbstractSshPostgresSourceAcceptanceTest : AbstractPostgresSourceAcceptanceTest() {
    private val bastion: SshBastionContainer = SshBastionContainer()
    private lateinit var testdb: PostgresTestDatabase

    @Throws(Exception::class)
    private fun populateDatabaseTestData() {
        val outerConfig: JsonNode =
            testdb
                .integrationTestConfigBuilder()
                .withSchemas("public")
                .withoutSsl()
                .with("tunnel_method", bastion.getTunnelMethod(this.tunnelMethod, false)!!)
                .build()
        sshWrap(
            outerConfig,
            JdbcUtils.HOST_LIST_KEY,
            JdbcUtils.PORT_LIST_KEY,
            CheckedConsumer<JsonNode?, Exception?> { mangledConfig: JsonNode? ->
                Companion.getDatabaseFromConfig(mangledConfig!!)
                    .query<Any?>(
                        ContextQueryFunction { ctx: DSLContext? ->
                            ctx!!.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));")
                            ctx.fetch(
                                "INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');"
                            )
                            ctx.fetch("CREATE TABLE starships(id INTEGER, name VARCHAR(200));")
                            ctx.fetch(
                                "INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');"
                            )
                            null
                        },
                    )
            },
        )
    }

    abstract val tunnelMethod: SshTunnel.TunnelMethod

    // todo (cgardens) - dynamically create data by generating a database with a random name instead
    // of
    // requiring data to already be in place.
    @Throws(Exception::class)
    protected override fun setupEnvironment(environment: TestDestinationEnv?) {
        testdb =
            PostgresTestDatabase.`in`(
                PostgresTestDatabase.BaseImage.POSTGRES_17,
                PostgresTestDatabase.ContainerModifier.NETWORK
            )
        bastion.initAndStartBastion(testdb.container.network)
        populateDatabaseTestData()
    }

    protected override fun tearDown(testEnv: TestDestinationEnv?) {
        bastion.stopAndClose()
    }

    override val config: JsonNode
        get() {
            try {
                return testdb
                    .integrationTestConfigBuilder()
                    .withSchemas("public")
                    //                    .withoutSsl()
                    .withSsl(mutableMapOf(MODE_KEY to "disable"))
                    .with("tunnel_method", bastion.getTunnelMethod(this.tunnelMethod, true)!!)
                    .build()
            } catch (e: IOException) {
                throw UncheckedIOException(e)
            } catch (e: InterruptedException) {
                throw RuntimeException(e)
            }
        }

    override val configuredCatalog: ConfiguredAirbyteCatalog
        get() =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    Lists.newArrayList<ConfiguredAirbyteStream?>(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(Lists.newArrayList<String?>("id"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        STREAM_NAME,
                                        SCHEMA_NAME,
                                        Field.of("id", JsonSchemaType.INTEGER),
                                        Field.of("name", JsonSchemaType.STRING),
                                    )
                                    .withSupportedSyncModes(
                                        Lists.newArrayList<SyncMode?>(
                                            SyncMode.FULL_REFRESH,
                                            SyncMode.INCREMENTAL,
                                        ),
                                    )
                                    .withSourceDefinedPrimaryKey(
                                        List.of<MutableList<String?>?>(
                                            mutableListOf<String?>("id"),
                                        ),
                                    ),
                            ),
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(Lists.newArrayList<String?>("id"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        STREAM_NAME2,
                                        SCHEMA_NAME,
                                        Field.of("id", JsonSchemaType.INTEGER),
                                        Field.of("name", JsonSchemaType.STRING),
                                    )
                                    .withSupportedSyncModes(
                                        Lists.newArrayList<SyncMode?>(
                                            SyncMode.FULL_REFRESH,
                                            SyncMode.INCREMENTAL,
                                        ),
                                    )
                                    .withSourceDefinedPrimaryKey(
                                        List.of<MutableList<String?>?>(
                                            mutableListOf<String?>("id"),
                                        ),
                                    ),
                            ),
                    ),
                )

    override val state: JsonNode?
        get() = Jsons.jsonNode<HashMap<Any?, Any?>?>(HashMap<Any?, Any?>())

    companion object {
        private const val STREAM_NAME = "id_and_name"
        private const val STREAM_NAME2 = "starships"
        private const val SCHEMA_NAME = "public"

        private fun getDatabaseFromConfig(config: JsonNode): Database {
            return Database(
                DSLContextFactory.create(
                    config.get(JdbcUtils.USERNAME_KEY).asText(),
                    config.get(JdbcUtils.PASSWORD_KEY).asText(),
                    DatabaseDriver.POSTGRESQL.driverClassName,
                    String.format(
                        DatabaseDriver.POSTGRESQL.urlFormatString,
                        config.get(JdbcUtils.HOST_KEY).asText(),
                        config.get(JdbcUtils.PORT_KEY).asInt(),
                        config.get(JdbcUtils.DATABASE_KEY).asText(),
                    ),
                    SQLDialect.POSTGRES,
                ),
            )
        }
    }
}
