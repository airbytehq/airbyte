/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.Lists
import io.airbyte.cdk.test.fixtures.legacy.JdbcUtils.MODE_KEY
import io.airbyte.cdk.test.fixtures.legacy.Jsons
import io.airbyte.cdk.test.fixtures.legacy.TestDestinationEnv
import io.airbyte.integrations.source.postgres.legacy.testFixtures.PostgresTestDatabase
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.Field
import io.airbyte.protocol.models.v0.SyncMode
import java.util.List

class XminPostgresSourceAcceptanceTest : AbstractPostgresSourceAcceptanceTest() {
    private lateinit var testdb: PostgresTestDatabase

    @get:Throws(Exception::class)
    override val config: JsonNode
        get() =
            testdb
                .integrationTestConfigBuilder()
                .withSchemas("public")
                .withSsl(mutableMapOf(MODE_KEY to "disable"))
                .withXminReplication()
                .build()

    @Throws(Exception::class)
    protected override fun setupEnvironment(environment: TestDestinationEnv?) {
        testdb =
            PostgresTestDatabase.`in`(PostgresTestDatabase.BaseImage.POSTGRES_17)
                .with("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));")
                .with(
                    "INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');"
                )
                .with("CREATE TABLE starships(id INTEGER, name VARCHAR(200));")
                .with(
                    "INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');"
                )
                .with(
                    "CREATE MATERIALIZED VIEW testview AS select * from id_and_name where id = '2';"
                )
    }

    @Throws(Exception::class)
    protected override fun tearDown(testEnv: TestDestinationEnv?) {
        testdb.close()
    }

    @get:Throws(Exception::class)
    override val configuredCatalog: ConfiguredAirbyteCatalog
        get() =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    Lists.newArrayList<ConfiguredAirbyteStream?>(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        STREAM_NAME,
                                        SCHEMA_NAME,
                                        Field.of("id", JsonSchemaType.INTEGER),
                                        Field.of("name", JsonSchemaType.STRING),
                                    )
                                    .withSupportedSyncModes(
                                        Lists.newArrayList<SyncMode?>(SyncMode.INCREMENTAL)
                                    )
                                    .withSourceDefinedCursor(true)
                                    .withSourceDefinedPrimaryKey(
                                        List.of<MutableList<String?>?>(
                                            mutableListOf<String?>("id"),
                                        ),
                                    ),
                            ),
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        STREAM_NAME2,
                                        SCHEMA_NAME,
                                        Field.of("id", JsonSchemaType.INTEGER),
                                        Field.of("name", JsonSchemaType.STRING),
                                    )
                                    .withSupportedSyncModes(
                                        Lists.newArrayList<SyncMode?>(SyncMode.INCREMENTAL)
                                    )
                                    .withSourceDefinedCursor(true)
                                    .withSourceDefinedPrimaryKey(
                                        List.of<MutableList<String?>?>(
                                            mutableListOf<String?>("id"),
                                        ),
                                    ),
                            ),
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        STREAM_NAME_MATERIALIZED_VIEW,
                                        SCHEMA_NAME,
                                        Field.of("id", JsonSchemaType.INTEGER),
                                        Field.of("name", JsonSchemaType.STRING),
                                    )
                                    .withSupportedSyncModes(
                                        Lists.newArrayList<SyncMode?>(SyncMode.INCREMENTAL)
                                    )
                                    .withSourceDefinedCursor(true)
                                    .withSourceDefinedPrimaryKey(
                                        List.of<MutableList<String?>?>(
                                            mutableListOf<String?>("id"),
                                        ),
                                    ),
                            ),
                    ),
                )

    @get:Throws(Exception::class)
    override val state: JsonNode?
        get() = Jsons.jsonNode<HashMap<Any?, Any?>?>(HashMap<Any?, Any?>())

    companion object {
        private const val STREAM_NAME = "id_and_name"
        private const val STREAM_NAME2 = "starships"
        private const val STREAM_NAME_MATERIALIZED_VIEW = "testview"
        private const val SCHEMA_NAME = "public"
    }
}
