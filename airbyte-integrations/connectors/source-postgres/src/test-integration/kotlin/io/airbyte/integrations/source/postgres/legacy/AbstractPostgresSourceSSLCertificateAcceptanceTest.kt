/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.test.fixtures.legacy.Jsons
import io.airbyte.cdk.test.fixtures.legacy.TestDestinationEnv
import io.airbyte.integrations.source.postgres.PostgresTestDatabase
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.Field
import io.airbyte.protocol.models.v0.SyncMode

abstract class AbstractPostgresSourceSSLCertificateAcceptanceTest :
    AbstractPostgresSourceAcceptanceTest() {
    protected lateinit var testdb: PostgresTestDatabase

    @Throws(Exception::class)
    protected override fun setupEnvironment(environment: TestDestinationEnv?) {
        testdb =
            PostgresTestDatabase.Companion.`in`(
                    PostgresTestDatabase.BaseImage.POSTGRES_17,
                    PostgresTestDatabase.ContainerModifier.CERT
                )
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

    abstract val certificateConfiguration: MutableMap<Any?, Any?>

    protected override fun tearDown(testEnv: TestDestinationEnv?) {
        testdb.close()
    }

    override val config: JsonNode
        get() =
            testdb
                .integrationTestConfigBuilder()
                .withSchemas("public")
                .withStandardReplication()
                .withSsl(this.certificateConfiguration)
                .build()

    override val configuredCatalog: ConfiguredAirbyteCatalog
        get() =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    mutableListOf<ConfiguredAirbyteStream?>(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(mutableListOf<String?>("id"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        STREAM_NAME,
                                        SCHEMA_NAME,
                                        Field.of("id", JsonSchemaType.INTEGER),
                                        Field.of("name", JsonSchemaType.STRING),
                                    )
                                    .withSupportedSyncModes(
                                        mutableListOf<SyncMode?>(
                                            SyncMode.FULL_REFRESH,
                                            SyncMode.INCREMENTAL,
                                        ),
                                    )
                                    .withSourceDefinedPrimaryKey(
                                        listOf<MutableList<String?>?>(
                                            mutableListOf<String?>("id"),
                                        ),
                                    ),
                            ),
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(mutableListOf<String?>("id"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        STREAM_NAME2,
                                        SCHEMA_NAME,
                                        Field.of("id", JsonSchemaType.INTEGER),
                                        Field.of("name", JsonSchemaType.STRING),
                                    )
                                    .withSupportedSyncModes(
                                        mutableListOf<SyncMode?>(
                                            SyncMode.FULL_REFRESH,
                                            SyncMode.INCREMENTAL,
                                        ),
                                    )
                                    .withSourceDefinedPrimaryKey(
                                        listOf<MutableList<String?>?>(
                                            mutableListOf<String?>("id"),
                                        ),
                                    ),
                            ),
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withCursorField(mutableListOf<String?>("id"))
                            .withDestinationSyncMode(DestinationSyncMode.APPEND)
                            .withStream(
                                CatalogHelpers.createAirbyteStream(
                                        STREAM_NAME_MATERIALIZED_VIEW,
                                        SCHEMA_NAME,
                                        Field.of("id", JsonSchemaType.INTEGER),
                                        Field.of("name", JsonSchemaType.STRING),
                                    )
                                    .withSupportedSyncModes(
                                        mutableListOf<SyncMode?>(
                                            SyncMode.FULL_REFRESH,
                                            SyncMode.INCREMENTAL,
                                        ),
                                    )
                                    .withSourceDefinedPrimaryKey(
                                        listOf<MutableList<String?>?>(
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
        private const val STREAM_NAME_MATERIALIZED_VIEW = "testview"
        private const val SCHEMA_NAME = "public"
        const val PASSWORD: String = "Passw0rd"
    }
}
