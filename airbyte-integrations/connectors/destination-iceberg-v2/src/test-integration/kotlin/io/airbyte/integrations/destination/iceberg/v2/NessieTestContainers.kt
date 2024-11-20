/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.util.setOnce
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.util.concurrent.atomic.AtomicBoolean
import org.junit.jupiter.api.Assertions.fail
import org.projectnessie.minio.MinioContainer
import org.testcontainers.containers.ComposeContainer
import org.testcontainers.containers.startupcheck.StartupCheckStrategy
import org.testcontainers.containers.wait.strategy.DockerHealthcheckWaitStrategy

private val logger = KotlinLogging.logger {}

/**
 * Shared test containers for all nessie tests, so that we don't launch redundant docker containers
 */
object NessieTestContainers {
    val testcontainers: ComposeContainer =
        ComposeContainer(File("src/test-integration/resources/nessie/docker-compose.yml"))
            .withExposedService("nessie", 19120)
            .withExposedService("minio", 9000)
            .withExposedService("keycloak", 8080)
    private val startRunOnce = AtomicBoolean(false)

    /**
     * Start the test containers, or if another thread already called this method, wait for them to
     * finish starting
     */
    fun start() {
        if (startRunOnce.setOnce()) {
//            testcontainers.start()
            val minio = MinioContainer()
                .withEnv("MINIO_ROOT_USER", "inioadmin")
                .withEnv("MINIO_ROOT_PASSWORD", "inioadmin")
                .withEnv("MINIO_ADDRESS", ":9000")
                .withEnv("MINIO_CONSOLE_ADDRESS", ":9090")
                .withExposedPorts(9000)
            minio.start()
            val minioPort = minio.getMappedPort(9000)
            fail("Started minio. Port is $minioPort")
        } else {
            // afaict there's no method to wait for the containers to start
            // so just poll until these methods stop throwing exceptions
            while (true) {
//                try {
//                    testcontainers.getServicePort("nessie", 19120)
//                    testcontainers.getServicePort("minio", 9000)
//                    testcontainers.getServicePort("keycloak", 8080)
//                } catch (e: IllegalStateException) {
//                    // do nothing
//                }
                break
            }
        }
    }

    // intentionally no stop method - testcontainers automatically stop when their parent java
    // process exits (via ryuk)
}
