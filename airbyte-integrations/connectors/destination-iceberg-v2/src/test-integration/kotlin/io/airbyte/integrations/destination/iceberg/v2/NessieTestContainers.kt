/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import dasniko.testcontainers.keycloak.KeycloakContainer
import io.airbyte.cdk.load.util.setOnce
import io.minio.BucketExistsArgs
import io.minio.MakeBucketArgs
import io.minio.MinioClient
import io.minio.RemoveBucketArgs
import java.util.concurrent.atomic.AtomicBoolean
import org.projectnessie.testing.nessie.NessieContainer
import org.testcontainers.containers.MinIOContainer
import org.testcontainers.containers.Network

/** Shared test containers for all nessie tests, to avoid launching redundant docker containers. */
object NessieTestContainers {
    // Network configuration
    private val network = Network.newNetwork()
    private const val KEYCLOAK_ALIAS = "keycloak"
    private const val MINIO_ALIAS = "minio"
    private const val NESSIE_ALIAS = "nessie"

    // Container initialization control
    private val startRunOnce = AtomicBoolean(false)

    // Container instances
    val keycloakContainer =
        KeycloakContainer("quay.io/keycloak/keycloak:26.0.5")
            .withRealmImportFile("nessie/authn-keycloak/config/iceberg-realm.json")
            .withNetwork(network)
            .withNetworkAliases(KEYCLOAK_ALIAS)
            .withEnv(
                mapOf(
                    "KC_HEALTH_ENABLED" to "true",
                    "KC_BOOTSTRAP_ADMIN_USERNAME" to "admin",
                    "KC_BOOTSTRAP_ADMIN_PASSWORD" to "admin",
                ),
            )
            .withFeaturesEnabled("token-exchange")
            .withCustomCommand("--verbose")

    val minioContainer =
        MinIOContainer("minio/minio:RELEASE.2024-11-07T00-52-20Z")
            .withEnv(
                mapOf(
                    "MINIO_ROOT_USER" to "minioadmin",
                    "MINIO_ROOT_PASSWORD" to "minioadmin",
                ),
            )
            .withNetwork(network)
            .withNetworkAliases(MINIO_ALIAS)
            .withExposedPorts(9000)

    var nessieContainer: NessieContainer? = null

    fun start() {
        if (startRunOnce.setOnce()) {
            initializeAndStartContainers()
        }
    }

    private fun createMinioBucket() {
        val minioClient: MinioClient =
            MinioClient.builder()
                .endpoint(getMinioUrl())
                .credentials("minioadmin", "minioadmin")
                .build()

        val bucketName = "demobucket"

        // Force remove bucket if it exists
        if (minioClient.bucketExists(BucketExistsArgs.builder().bucket(bucketName).build())) {
            minioClient.removeBucket(RemoveBucketArgs.builder().bucket(bucketName).build())
        }

        // Create fresh bucket
        minioClient.makeBucket(MakeBucketArgs.builder().bucket(bucketName).build())
    }

    private fun initializeAndStartContainers() {
        // Start MinIO first
        minioContainer.start()
        createMinioBucket()

        // Start Keycloak and Nessie
        keycloakContainer.start()
        initializeAndStartNessie()
    }

    private fun initializeAndStartNessie() {
        // Initialize Nessie container
        nessieContainer =
            NessieContainer.builder()
                .dockerImage("ghcr.io/projectnessie/nessie:0.100.0")
                .build()
                .createContainer()
                .withNetwork(network)
                .withNetworkAliases(NESSIE_ALIAS)
                .withExposedPorts(19120, 9000)
                .withEnv(
                    mapOf(
                        // Version store settings
                        "nessie.version.store.type" to "IN_MEMORY",

                        // Authentication settings
                        "nessie.server.authentication.enabled" to "false",
                        "quarkus.oidc.auth-server-url" to "${getKeycloakUrl()}/realms/iceberg",
                        "quarkus.oidc.client-id" to "client1",
                        "quarkus.oidc.token.issuer" to "${getKeycloakUrl()}/realms/iceberg",

                        // Object store settings
                        "nessie.catalog.default-warehouse" to "warehouse",
                        "nessie.catalog.warehouses.warehouse.location" to "s3://demobucket/",
                        "nessie.catalog.service.s3.default-options.region" to "us-east-1",
                        "nessie.catalog.service.s3.default-options.path-style-access" to "true",
                        "nessie.catalog.service.s3.default-options.access-key" to
                            "urn:nessie-secret:quarkus:nessie.catalog.secrets.access-key",
                        "nessie.catalog.secrets.access-key.name" to "minioadmin",
                        "nessie.catalog.secrets.access-key.secret" to "minioadmin",
                        "nessie.catalog.service.s3.default-options.endpoint" to "${getMinioUrl()}/",

                        // Authorization settings
                        "nessie.server.authorization.enabled" to "false",
                        "nessie.server.authorization.rules.client1" to
                            "role=='service-account-client1'",
                        "nessie.server.authorization.rules.client2" to
                            "role=='service-account-client2' && !path.startsWith('sales')",
                        "nessie.server.authorization.rules.client3" to
                            "role=='service-account-client3' && !path.startsWith('eng')",
                    ),
                )
                .dependsOn(minioContainer)
                .dependsOn(keycloakContainer)

        nessieContainer?.start()
    }

    // External URLs (for test access)
    fun getKeycloakUrl(): String = "http://$KEYCLOAK_ALIAS:8080"
    fun getNessieUrl(): String = "http://$NESSIE_ALIAS:19120"
    fun getMinioUrl(): String = "http://$MINIO_ALIAS:9000"
}
