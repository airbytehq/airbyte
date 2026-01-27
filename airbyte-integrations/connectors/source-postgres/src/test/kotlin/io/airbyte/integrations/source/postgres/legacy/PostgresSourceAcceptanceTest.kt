/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.Lists
import io.airbyte.cdk.test.fixtures.legacy.ContextQueryFunction
import io.airbyte.cdk.test.fixtures.legacy.Database
import io.airbyte.cdk.test.fixtures.legacy.JdbcUtils
import io.airbyte.cdk.test.fixtures.legacy.JdbcUtils.MODE_KEY
import io.airbyte.cdk.test.fixtures.legacy.Jsons
import io.airbyte.cdk.test.fixtures.legacy.TestDestinationEnv
import io.airbyte.integrations.source.postgres.legacy.testFixtures.PostgresTestDatabase
import io.airbyte.integrations.source.postgres.legacy.testFixtures.PostgresTestDatabase.BaseImage
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.Field
import io.airbyte.protocol.models.v0.SyncMode
import java.sql.SQLException
import java.util.List
import org.jooq.DSLContext
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

open class PostgresSourceAcceptanceTest : AbstractPostgresSourceAcceptanceTest() {
    private lateinit var testdb: PostgresTestDatabase
    override var config: JsonNode? = null

    @Throws(Exception::class)
    protected override fun setupEnvironment(environment: TestDestinationEnv?) {
        testdb = PostgresTestDatabase.`in`(this.serverImage)
        config = getConfig(testdb.userName, testdb.password, "public")
        testdb.query({ ctx ->
            ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));")
            ctx.fetch(
                "INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');"
            )
            ctx.fetch("CREATE TABLE starships(id INTEGER, name VARCHAR(200));")
            ctx.fetch(
                "INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');"
            )
            ctx.fetch(
                "CREATE MATERIALIZED VIEW testview AS select * from id_and_name where id = '2';"
            )
            null
        },)
    }

    private val limitPermissionRoleName: String
        get() = testdb.withNamespace("limit_perm_role")

    private fun getConfig(username: String, password: String?, vararg schemas: String?): JsonNode {
        return testdb
            .configBuilder()
            .withResolvedHostAndPort()
            .withDatabase()
            .with(JdbcUtils.USERNAME_KEY, username)
            .let { cb ->
                password?.let { p -> cb.with(JdbcUtils.PASSWORD_KEY, p) }
                cb
            }
            .withSchemas(*schemas)
            .withSsl(mutableMapOf(MODE_KEY to "disable"))
            .withStandardReplication()
            .build()
    }

    protected override fun tearDown(testEnv: TestDestinationEnv?) {
        testdb.close()
    }

    override val configuredCatalog: ConfiguredAirbyteCatalog
        get() = this.commonConfigCatalog

    override val state: JsonNode?
        get() = Jsons.jsonNode<HashMap<Any, Any>?>(HashMap<Any, Any>())

    @Test
    @Throws(Exception::class)
    fun testFullRefreshWithRevokingSchemaPermissions() {
        prepareEnvForUserWithoutPermissions(testdb.database)

        config =
            getConfig(
                this.limitPermissionRoleName,
                LIMIT_PERMISSION_ROLE_PASSWORD,
                LIMIT_PERMISSION_SCHEMA,
            )
        val configuredCatalog: ConfiguredAirbyteCatalog? = this.limitPermissionConfiguredCatalog

        val fullRefreshRecords: MutableList<AirbyteRecordMessage?> =
            filterRecords(runRead(configuredCatalog)).toMutableList()
        val assertionMessage =
            "Expected records after full refresh sync for user with schema permission"
        Assertions.assertFalse(fullRefreshRecords.isEmpty(), assertionMessage)

        revokeSchemaPermissions(testdb.database)

        val lessPermFullRefreshRecords: MutableList<AirbyteRecordMessage?> =
            filterRecords(runRead(configuredCatalog)).toMutableList()
        val assertionMessageWithoutPermission =
            "Expected no records after full refresh sync for user without schema permission"
        Assertions.assertTrue(
            lessPermFullRefreshRecords.isEmpty(),
            assertionMessageWithoutPermission,
        )
    }

    @Test
    @Throws(Exception::class)
    fun testDiscoverWithRevokingSchemaPermissions() {
        prepareEnvForUserWithoutPermissions(testdb.database)
        revokeSchemaPermissions(testdb.database)
        config =
            getConfig(
                this.limitPermissionRoleName,
                LIMIT_PERMISSION_ROLE_PASSWORD,
                LIMIT_PERMISSION_SCHEMA,
            )

        runDiscover()
        val lastPersistedCatalogSecond: AirbyteCatalog = lastPersistedCatalog
        val assertionMessageWithoutPermission =
            "Expected no streams after discover for user without schema permissions"
        Assertions.assertTrue(
            lastPersistedCatalogSecond.getStreams().isEmpty(),
            assertionMessageWithoutPermission,
        )
    }

    @Throws(SQLException::class)
    private fun revokeSchemaPermissions(database: Database) {
        database.query<Any?>(
            ContextQueryFunction { ctx: DSLContext ->
                ctx.fetch(
                    String.format(
                        "REVOKE USAGE ON schema %s FROM %s;",
                        LIMIT_PERMISSION_SCHEMA,
                        this.limitPermissionRoleName,
                    ),
                )
                null
            },
        )
    }

    @Throws(SQLException::class)
    private fun prepareEnvForUserWithoutPermissions(database: Database) {
        database.query<Any?>(
            ContextQueryFunction { ctx: DSLContext ->
                ctx.fetch(
                    String.format(
                        "CREATE ROLE %s WITH LOGIN PASSWORD '%s';",
                        this.limitPermissionRoleName,
                        LIMIT_PERMISSION_ROLE_PASSWORD,
                    ),
                )
                ctx.fetch(String.format("CREATE SCHEMA %s;", LIMIT_PERMISSION_SCHEMA))
                ctx.fetch(
                    java.lang.String.format(
                        "GRANT CONNECT ON DATABASE %s TO %s;",
                        testdb.databaseName,
                        this.limitPermissionRoleName,
                    ),
                )
                ctx.fetch(
                    String.format(
                        "GRANT USAGE ON schema %s TO %s;",
                        LIMIT_PERMISSION_SCHEMA,
                        this.limitPermissionRoleName,
                    ),
                )
                ctx.fetch(
                    String.format(
                        "CREATE TABLE %s.id_and_name(id INTEGER, name VARCHAR(200));",
                        LIMIT_PERMISSION_SCHEMA,
                    ),
                )
                ctx.fetch(
                    String.format(
                        "INSERT INTO %s.id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');",
                        LIMIT_PERMISSION_SCHEMA,
                    ),
                )
                ctx.fetch(
                    String.format(
                        "GRANT SELECT ON table %s.id_and_name TO %s;",
                        LIMIT_PERMISSION_SCHEMA,
                        this.limitPermissionRoleName,
                    ),
                )
                null
            },
        )
    }

    private val commonConfigCatalog: ConfiguredAirbyteCatalog
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
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(Lists.newArrayList<String?>("id"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        STREAM_NAME_MATERIALIZED_VIEW,
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

    private val limitPermissionConfiguredCatalog: ConfiguredAirbyteCatalog?
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
                                        "id_and_name",
                                        LIMIT_PERMISSION_SCHEMA,
                                        Field.of("id", JsonSchemaType.INTEGER),
                                        Field.of("name", JsonSchemaType.STRING),
                                    )
                                    .withSupportedSyncModes(
                                        Lists.newArrayList<SyncMode?>(
                                            SyncMode.FULL_REFRESH,
                                            SyncMode.INCREMENTAL,
                                        ),
                                    ),
                            ),
                    ),
                )

    protected open val serverImage: BaseImage
        get() = BaseImage.POSTGRES_17

    companion object {
        private const val STREAM_NAME = "id_and_name"
        private const val STREAM_NAME2 = "starships"
        private const val STREAM_NAME_MATERIALIZED_VIEW = "testview"
        private const val SCHEMA_NAME = "public"
        const val LIMIT_PERMISSION_SCHEMA: String = "limit_perm_schema"
        const val LIMIT_PERMISSION_ROLE_PASSWORD: String = "test"
    }
}
