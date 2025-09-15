/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.util.setOnce
import java.io.File
import java.time.Duration
import java.util.concurrent.atomic.AtomicBoolean
import org.testcontainers.containers.ComposeContainer
import org.testcontainers.containers.wait.strategy.Wait

/**
 * Shared test containers for all nessie tests, so that we don't launch redundant docker containers
 */
object NessieTestContainers {
    val testcontainers: ComposeContainer =
        ComposeContainer(File("src/test-integration/resources/nessie/docker-compose.yml"))
            .withExposedService(
                "nessie",
                19120,
                Wait.forListeningPort().withStartupTimeout(Duration.ofSeconds(60))
            )
            .withExposedService(
                "minio",
                9000,
                Wait.forListeningPort().withStartupTimeout(Duration.ofSeconds(60))
            )
            .withExposedService(
                "keycloak",
                8080,
                Wait.forListeningPort().withStartupTimeout(Duration.ofSeconds(60))
            )
    private val startNessieContainerRunOnce = AtomicBoolean(false)

    /**
     * Start the test containers, or if another thread already called this method, wait for them to
     * finish starting
     */
    fun start() {
        if (startNessieContainerRunOnce.setOnce()) {
            testcontainers.start()
        }
    }

    // intentionally no stop method - testcontainers automatically stop when their parent java
    // process exits (via ryuk)
}
