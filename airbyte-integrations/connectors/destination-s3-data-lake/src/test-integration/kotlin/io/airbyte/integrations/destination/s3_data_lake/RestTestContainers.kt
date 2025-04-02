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

object RestTestContainers {

    private val composeFile = File("src/test-integration/resources/rest/docker-compose.yml")

    /**
     * Define the docker-compose services and their wait strategies, so Testcontainers won't
     * consider them "started" until they're actually listening on those ports.
     */
    val testcontainers: ComposeContainer =
        ComposeContainer(composeFile)
            // Wait until each service is up on its container port.
            // The container is still using port 9000 internally for minio,
            // but no longer mapped to 9000 on the host.
            .withExposedService(
                "minio",
                9000,
                Wait.forListeningPort().withStartupTimeout(Duration.ofSeconds(60))
            )
            .withExposedService(
                "rest",
                8181,
                Wait.forListeningPort().withStartupTimeout(Duration.ofSeconds(60))
            )
            .withExposedService(
                "spark-iceberg",
                8080,
                Wait.forListeningPort().withStartupTimeout(Duration.ofSeconds(60))
            )

    private val startRestContainerRunOnce = AtomicBoolean(false)

    /** Start the test containers, or skip if they're already started. */
    fun start() {
        if (startRestContainerRunOnce.setOnce()) {
            testcontainers.start()
        }
        // If it's already started, do nothing; the containers remain up.
    }
}
