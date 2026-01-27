/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.legacy

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import com.google.common.collect.Lists
import io.airbyte.cdk.test.fixtures.legacy.AdaptiveSourceRunner
import io.airbyte.cdk.test.fixtures.legacy.FeatureFlags
import io.airbyte.cdk.test.fixtures.legacy.FeatureFlagsWrapper
import io.airbyte.cdk.test.fixtures.legacy.Jsons
import io.airbyte.cdk.test.fixtures.legacy.MoreResources
import io.airbyte.cdk.test.fixtures.legacy.SourceAcceptanceTest
import io.airbyte.cdk.test.fixtures.legacy.SshHelpers
import io.airbyte.cdk.test.fixtures.legacy.TestDestinationEnv
import io.airbyte.integrations.source.postgres.legacy.testFixtures.PostgresTestDatabase
import io.airbyte.protocol.models.JsonSchemaType
import io.airbyte.protocol.models.v0.CatalogHelpers
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.protocol.models.v0.Field
import io.airbyte.protocol.models.v0.SyncMode
import java.util.*
import java.util.List

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
            PostgresTestDatabase.`in`(
                PostgresTestDatabase.BaseImage.POSTGRES_17,
                PostgresTestDatabase.ContainerModifier.CERT
            )
        testdb.query({ ctx ->
            ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200));")
            ctx.fetch(
                "INSERT INTO id_and_name (id, name) VALUES (1,'picard'),  (2, 'crusher'), (3, 'vash');"
            )
            ctx.fetch("CREATE TABLE starships(id INTEGER, name VARCHAR(200));")
            ctx.fetch(
                "INSERT INTO starships (id, name) VALUES (1,'enterprise-d'),  (2, 'defiant'), (3, 'yamato');"
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
        get() =
            SshHelpers.injectSshIntoSpec(
                Jsons.deserialize<ConnectorSpecification>(
                    MoreResources.readResource(
                        "expected_cloud_deployment_spec.json",
                    ),
                    ConnectorSpecification::class.java,
                ),
                Optional.of<String?>("security"),
            )

    override val config: JsonNode
        get() {
            val certs: PostgresTestDatabase.Certificates = testdb.certificates
            return testdb
                .integrationTestConfigBuilder()
                .withStandardReplication()
                .withSsl(
                    ImmutableMap.builder<Any?, Any?>()
                        .put("mode", "verify-ca")
                        .put("ca_certificate", certs.caCertificate)
                        .put("client_certificate", certs.clientCertificate)
                        .put("client_key", certs.clientKey)
                        .put("client_key_password", PASSWORD)
                        .build(),
                )
                .build()
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

    override val state: JsonNode
        get() = Jsons.jsonNode<HashMap<Any?, Any?>?>(HashMap<Any?, Any?>())

    companion object {
        private const val STREAM_NAME = "id_and_name"
        private const val STREAM_NAME2 = "starships"
        private const val SCHEMA_NAME = "public"

        protected const val PASSWORD: String = "Passw0rd"
    }
}
