/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.test.fixtures.legacy.AdaptiveSourceRunner
import io.airbyte.cdk.test.fixtures.legacy.FeatureFlags
import io.airbyte.cdk.test.fixtures.legacy.FeatureFlagsWrapper
import io.airbyte.cdk.test.fixtures.legacy.Jsons
import io.airbyte.cdk.test.fixtures.legacy.SourceAcceptanceTest
import io.airbyte.cdk.test.fixtures.legacy.SshHelpers
import io.airbyte.cdk.test.fixtures.legacy.TestDestinationEnv
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.Field
import io.airbyte.protocol.models.v0.SyncMode
import java.util.*

class CloudDeploymentPostgresSourceAcceptanceTest : SourceAcceptanceTest() {
    private lateinit var testdb: PostgresTestDatabase

    override fun featureFlags(): FeatureFlags {
        return FeatureFlagsWrapper.overridingDeploymentMode(
            super.featureFlags(),
            AdaptiveSourceRunner.CLOUD_MODE,
        )
    }

    @Throws(Exception::class)
    override fun setupEnvironment(environment: TestDestinationEnv?) {
        testdb =
            PostgresTestDatabase.Companion.`in`(
                PostgresTestDatabase.BaseImage.POSTGRES_17,
                PostgresTestDatabase.ContainerModifier.CERT
            )
        testdb.query<Any?>({ ctx ->
            ctx.fetch("CREATE SCHEMA $SCHEMA_NAME;")
            ctx.fetch("CREATE TABLE $SCHEMA_NAME.id_and_name(id INTEGER, name VARCHAR(200));")
            ctx.fetch(
                "INSERT INTO $SCHEMA_NAME.id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');"
            )
            ctx.fetch("CREATE TABLE $SCHEMA_NAME.starships(id INTEGER, name VARCHAR(200));")
            ctx.fetch(
                "INSERT INTO $SCHEMA_NAME.starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');"
            )
            null
        },)
    }

    override fun tearDown(testEnv: TestDestinationEnv?) {
        testdb.close()
    }

    override val imageName: String
        get() = "airbyte/source-postgres:dev"

    @get:Throws(Exception::class)
    override val spec: ConnectorSpecification?
        get() = SshHelpers.getSpecAndInjectSsh(Optional.empty())

    override val config: JsonNode
        get() {
            val certs: PostgresTestDatabase.Certificates = testdb.certificates
            return testdb
                .integrationTestConfigBuilder()
                .withStandardReplication()
                .withSchemas(SCHEMA_NAME)
                .withSsl(
                    mutableMapOf(
                        "mode" to "verify-ca",
                        "ca_certificate" to certs.caCertificate,
                        "client_certificate" to certs.clientCertificate,
                        "client_key" to certs.clientKey,
                        "client_key_password" to PASSWORD,
                    ),
                )
                .build()
        }

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
                    ),
                )

    override val state: JsonNode
        get() = Jsons.jsonNode<HashMap<Any?, Any?>?>(HashMap<Any?, Any?>())

    companion object {
        private const val STREAM_NAME = "id_and_name"
        private const val STREAM_NAME2 = "starships"
        private const val SCHEMA_NAME = "cloud_deployment_postgres_source_acceptance_test"

        protected const val PASSWORD: String = "Passw0rd"
    }
}
