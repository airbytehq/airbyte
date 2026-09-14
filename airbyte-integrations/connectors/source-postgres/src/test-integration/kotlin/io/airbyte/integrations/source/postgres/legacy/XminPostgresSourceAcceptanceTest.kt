/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.test.fixtures.legacy.JdbcUtils.MODE_KEY
import io.airbyte.cdk.test.fixtures.legacy.Jsons
import io.airbyte.cdk.test.fixtures.legacy.TestDestinationEnv
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.Field
import io.airbyte.protocol.models.v0.SyncMode

class XminPostgresSourceAcceptanceTest : AbstractPostgresSourceAcceptanceTest() {
    private lateinit var testdb: PostgresTestDatabase

    @get:Throws(Exception::class)
    override val config: JsonNode
        get() =
            testdb
                .integrationTestConfigBuilder()
                .withSchemas(SCHEMA_NAME)
                .withSsl(mutableMapOf(MODE_KEY to "disable"))
                .withXminReplication()
                .build()

    @Throws(Exception::class)
    protected override fun setupEnvironment(environment: TestDestinationEnv?) {
        testdb =
            PostgresTestDatabase.`in`(PostgresTestDatabase.BaseImage.POSTGRES_17)
                .with("CREATE SCHEMA $SCHEMA_NAME;")
                .with("CREATE TABLE $SCHEMA_NAME.id_and_name(id INTEGER, name VARCHAR(200));")
                .with(
                    "INSERT INTO $SCHEMA_NAME.id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');"
                )
                .with("CREATE TABLE $SCHEMA_NAME.starships(id INTEGER, name VARCHAR(200));")
                .with(
                    "INSERT INTO $SCHEMA_NAME.starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');"
                )
                .with(
                    "CREATE MATERIALIZED VIEW $SCHEMA_NAME.testview AS select * from $SCHEMA_NAME.id_and_name where id = '2';"
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
                    mutableListOf<ConfiguredAirbyteStream?>(
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
                                        mutableListOf<SyncMode?>(SyncMode.INCREMENTAL)
                                    )
                                    .withSourceDefinedCursor(true)
                                    .withSourceDefinedPrimaryKey(
                                        listOf<MutableList<String?>?>(
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
                                        mutableListOf<SyncMode?>(SyncMode.INCREMENTAL)
                                    )
                                    .withSourceDefinedCursor(true)
                                    .withSourceDefinedPrimaryKey(
                                        listOf<MutableList<String?>?>(
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
                                        mutableListOf<SyncMode?>(SyncMode.INCREMENTAL)
                                    )
                                    .withSourceDefinedCursor(true)
                                    .withSourceDefinedPrimaryKey(
                                        listOf<MutableList<String?>?>(
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
        private const val SCHEMA_NAME = "xmin_postgres_source_acceptance_test"
    }
}
